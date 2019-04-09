import glfw
from OpenGL.GL import *
from OpenGL.arrays.arraydatatype import ArrayDatatype
from OpenGL.GL.ARB.texture_rg import *
from ctypes import sizeof
import numpy as np
import matplotlib.pyplot as plt
import glm
from time import sleep
import struct

def create_context():
    if not glfw.init():
        print('Failed to init glfw')
        return None

    #glfw.window_hint(glfw.VISIBLE, False)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    window = glfw.create_window(600, 600, 'Wtf', None, None)
    if not window:
        print('Failed to create window')
        glfw.terminate()
        return None

    glfw.make_context_current(window)
    return window

# Simple OpenGL buffer wrapper
class BufferObject(object):

    # Creates, binds(!) and loads data to the buffer
    def __init__(self, target, data, usage):
        self.__target = target
        self.buffer = glGenBuffers(1)
        glBindBuffer(target, self.buffer)
        glBufferData(target, ArrayDatatype.arrayByteCount(data), data, usage)

    # Bind buffer
    def bind(self):
        glBindBuffer(self.__target, self.buffer)

    # Unbind buffer
    def unbind(self):
        glBindBuffer(self.__target, 0)


# Vertex Buffer Object wrapper
class VBO(BufferObject):
    def __init__(self, data, usage):
        super(self.__class__, self).__init__(GL_ARRAY_BUFFER, data, usage)


# Element (Index) Buffer Object wrapper
class EBO(BufferObject):
    def __init__(self, data, usage):
        super(self.__class__, self).__init__(GL_ELEMENT_ARRAY_BUFFER, data, usage)


class Shader(object):
    def __init__(self, shader_type, source, name = None):
        self.__shader = glCreateShader(shader_type)
        self.__name = name
        glShaderSource(self.__shader, source)
        glCompileShader(self.__shader)
        if glGetShaderiv(self.__shader, GL_COMPILE_STATUS) != 1:
            message = glGetShaderInfoLog(self.__shader)
            print('Shader "%s" compilation error:' % self.name)
            print(message)
            print(source)
            raise ValueError('Shader "%s" compilation error' % self.name)

    def __del__(self):
        glDeleteShader(self.__shader)


    @property
    def shader(self):
        return self.__shader

    @property
    def name(self):
        return self.__name if self.__name is not None else 'Unnamed shader'


class VertexShader(Shader):
    def __init__(self, source, name=None):
        super(self.__class__, self).__init__(GL_VERTEX_SHADER, source, name)

class FragmentShader(Shader):
    def __init__(self, source, name=None):
        super(self.__class__, self).__init__(GL_FRAGMENT_SHADER, source, name)

class ShaderProgram(object):
    def __init__(self, shaders, name=None):
        self.__program = glCreateProgram()
        for shader in shaders:
            print('Attach %s' % shader.name)
            glAttachShader(self.__program, shader.shader)
        glLinkProgram(self.__program)
        if glGetProgramiv(self.__program, GL_LINK_STATUS) != 1:
            message = glGetProgramInfoLog(self.__program)
            print('Shader program "%s" linking error:' % name)
            print(message)
            raise ValueError('Shader program "%s" linking error:' % name)
        else:
            print('Shader program "%s" linked' % name)

    @property
    def program(self):
        return self.__program
    
    @property
    def name(self):
        return self.__name if self.__name is not None else 'Unnamed shader program'

    def use(self):
        glUseProgram(self.__program)

    def unuse(self):
        glUseProgram(0)
    


class MainShaderProgram(ShaderProgram):
    def __init__(self):
        vertex_shader = VertexShader(vertex_shader_code, 'vertex')
        fragment_shader = FragmentShader(fragment_shader_code, 'fragment')
        super(self.__class__, self).__init__([vertex_shader, fragment_shader], 'main_program')

        self.__uniform_proj = glGetUniformLocation(self.program, 'm_projection')
        self.__uniform_view = glGetUniformLocation(self.program, 'm_view')
        self.__uniform_model = glGetUniformLocation(self.program, 'm_model')

        self.use()
        self.set_proj(glm.mat4(1.0))
        self.set_view(glm.mat4(1.0))
        self.set_model(glm.mat4(1.0))
        self.unuse()

    def set_proj(self, matrix):
        glUniformMatrix4fv(self.__uniform_proj, 1, GL_FALSE, glm.value_ptr(matrix))

    def set_view(self, matrix):
        glUniformMatrix4fv(self.__uniform_view, 1, GL_FALSE, glm.value_ptr(matrix))

    def set_model(self, matrix):
        glUniformMatrix4fv(self.__uniform_model, 1, GL_FALSE, glm.value_ptr(matrix))

####################################################

vertex_dtype = [('pos', np.float32, 2),
                ('color', np.ubyte, 1)]


# Calculate instersection coordinates of two line defined by
# direction vector and point
def line_intersect(P1, v1, P2, v2):
    x = (v2[0]*(P1[0]*v1[1] - P1[1]*v1[0]) - v1[0]*(P2[0]*v2[1] - P2[1]*v2[0]))/(v2[0]*v1[1] - v2[1]*v1[0])
    y = (v2[1]*(P1[0]*v1[1] - P1[1]*v1[0]) - v1[1]*(P2[0]*v2[1] - P2[1]*v2[0]))/(v2[0]*v1[1] - v2[1]*v1[0])
    return np.array([x,y])

# Normalize numpy vector
def normalize(vec):
    return vec/np.linalg.norm(vec)

def make_vertex(point, color):
    return np.array([(point, color)], dtype=vertex_dtype)

# Triangulate one segment of the lane
def triangulate_line_segment(P1, P2, O1, O2, color, data):
    data.extend([make_vertex(P1, color), make_vertex(P2, color), make_vertex(O1, color)])
    data.extend([make_vertex(O1, color), make_vertex(P2, color), make_vertex(O2, color)])

# Triangulate one segment of the road 
# Road consists of multiple lines
# Assume all arrays have same length
def triangulate_segment(cur_points, next_points, colors, data):
    for i in range(len(cur_points)-1):
        triangulate_line_segment(cur_points[i], cur_points[i+1], next_points[i], next_points[i+1],
                                 colors[i], data)

# Create colors (test code)
def create_colors(lines_cnt):
    rng = range(lines_cnt/2)
    return np.concatenate([
        [10+i+1 for i in rng[::-1]],
        [i+1 for i in rng]
    ])    

# Generate vertex data for road segment
# Support only even count of lines
# Indexes starts from center line
def create_road(points, lines_cnt, lines_width):

    if len(points) < 2:
        raise ValueError('Road should contains at least two points')

    if lines_cnt % 2 != 0:
        raise ValueError('Odd lines count not supported')

    if lines_width <= 0:
        raise ValueError('Lines width should be greater then zero')

    up = np.array([0,0,1])
    colors = create_colors(lines_cnt)
    print(colors)
    vertex_data = []

    offsets = (np.arange(-lines_cnt/2, lines_cnt/2 + 1) * lines_width).reshape((lines_cnt+1, 1))
    v1 = normalize(points[1] - points[0])
    n1 = np.cross(up, v1)[:2]
    cur_points = points[0] + n1*offsets

    for seg_i in range(len(points)-2):
        v2 = normalize(points[seg_i+2] - points[seg_i+1])
        n2 = np.cross(up, v2)[:2]
        n = (n1 + n2)/2
        next_points = np.array([line_intersect(p, v1, points[seg_i+1], n) for p in cur_points])
        triangulate_segment(cur_points, next_points, colors, vertex_data)
        
        n1 = n2
        v1 = v2
        cur_points = next_points


    next_points = points[-1] + n1*offsets
    triangulate_segment(cur_points, next_points, colors, vertex_data)

    return np.concatenate(vertex_data)

####################################################

vertex_shader_code = """
#version 330 core

layout (location = 0) in vec2 position;
layout (location = 1) in uint color;

flat out uint vertex_color;

uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_projection;

void main()
{
    gl_Position = m_projection * m_view * m_model * vec4(position, 0, 1.0);
    vertex_color = color;
}
"""

fragment_shader_code = """
#version 330 core

flat in uint vertex_color;
out uint color;

void main()
{
    color = vertex_color;
}
"""

def main():

    window = create_context()
    if window is None:
        return

    points = np.array([
        [0,0],
        [10, 0],
        [10, 10],
        [15,15],
        [30, 15],
        [45, 0]
    ], dtype=np.float32)

    vertices = create_road(points, 6, 1)    

    # Create shaders
    shader_program = MainShaderProgram()

    # Transformations
    shader_program.use()
    shader_program.set_proj(glm.ortho(-5.0, 40.0, -5.0, 40.0, -1.0, 1.0))
    shader_program.unuse()

    # Create buffers
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)
    vbo = VBO(vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 2*4+1, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribIPointer(1, 1, GL_UNSIGNED_BYTE, 2*4+1, ctypes.c_void_p(2*4))
    glEnableVertexAttribArray(1)
    vbo.unbind()
    glBindVertexArray(0)
    
    TEX_WIDTH = 100
    TEX_HEIGHT = 100

    # Render to the texture
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_R8UI, TEX_WIDTH, TEX_HEIGHT, 0, GL_RED_INTEGER, GL_UNSIGNED_BYTE, None)
    glBindTexture(GL_TEXTURE_2D, 0)

    framebuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        print('Failed to init framebuffer')
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # Do render
    glViewport(0, 0, TEX_WIDTH, TEX_HEIGHT)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    shader_program.use()
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))
    glBindVertexArray(0)
    array = np.frombuffer(glReadPixels(0, 0, TEX_WIDTH, TEX_HEIGHT, GL_RED_INTEGER, GL_UNSIGNED_BYTE), dtype=np.ubyte)
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    array = array.reshape(TEX_WIDTH, TEX_HEIGHT)
    d={}
    for a in array.flatten():
        if a not in d:
            d[a]=1
        else:
            d[a]+=1

    print(d)
    plt.imshow(array)
    plt.show()

    glfw.terminate()

if __name__ == '__main__':
    main()