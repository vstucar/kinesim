import glfw
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.arrays.arraydatatype import ArrayDatatype
from ctypes import sizeof
import numpy as np
import matplotlib.pyplot as plt
import glm

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
        super(VBO, self).__init__(GL_ARRAY_BUFFER, data, usage)


# Element (Index) Buffer Object wrapper
class EBO(BufferObject):
    def __init__(self, data, usage):
        super(EBO, self).__init__(GL_ELEMENT_ARRAY_BUFFER, data, usage)


####################################################

def draw_vec(P, vec, length):
    P1 = P + vec/np.linalg.norm(vec) * length
    coords = np.vstack([P, P1])
    plt.plot(coords[:,0], coords[:,1])

def draw_point(P):
    plt.plot([P[0]], [P[1]], 'o')
    
def draw_line(A, B):
    coords = np.vstack([A, B])
    plt.plot(coords[:,0], coords[:,1])

def draw_segment(A1, B1, A2, B2):
    draw_line(A1, A2)
    draw_line(B1, B2)
    draw_line(A2, B2)

def draw_tri(A, B, C):
    coords = np.vstack([A, B, C])
    plt.fill(coords[:,0], coords[:,1])    

# Calculate instersection coordinates of two line defined by
# direction vector and point
def line_intersect(P1, v1, P2, v2):
    x = (v2[0]*(P1[0]*v1[1] - P1[1]*v1[0]) - v1[0]*(P2[0]*v2[1] - P2[1]*v2[0]))/(v2[0]*v1[1] - v2[1]*v1[0])
    y = (v2[1]*(P1[0]*v1[1] - P1[1]*v1[0]) - v1[1]*(P2[0]*v2[1] - P2[1]*v2[0]))/(v2[0]*v1[1] - v2[1]*v1[0])
    return np.array([x,y])

# Normalize numpy vector
def normalize(vec):
    return vec/np.linalg.norm(vec)

# Triangulate one segment of the lane
# Road consists of two lanes
def triangulate_lane_segment(P1, P2, O1, O2, color, data):
    color = np.append(np.random.random((3)), 1)
    data.extend([P1, color, P2, color, O1, color])
    color = np.append(np.random.random((3)), 1)
    data.extend([O1, color, P2, color, O2, color])
    draw_tri(P1, P2, O1)
    draw_tri(O1, P2, O2)


# Generate vertex data for road segment
def create_road(points, width):
    up = np.array([0,0,1])
    color = np.array([1,0,0,1])
    plt.plot(points[:,0], points[:,1])

    vertex_data = []

    v1 = normalize(points[1] - points[0])
    n1 = np.cross(up, v1)[:2]
    A1 = points[0] + n1 * width/2
    B1 = points[0] - n1 * width/2

    for i in range(len(points)-2):
        O1 = points[i]
        O2 = points[i+1]

        v2 = normalize(points[i+2] - points[i+1])
        n2 = np.cross(up, v2)[:2]
        n = (n1 + n2)/2

        A2 = line_intersect(A1, v1, O2, n)
        B2 = line_intersect(B1, v1, O2, -n)
        
        #draw_segment(A1, B1, A2, B2)
        triangulate_lane_segment(A1, A2, O1, O2, color, vertex_data)
        triangulate_lane_segment(B1, B2, O1, O2, color, vertex_data)
        
        A1 = A2
        B1 = B2
        n1 = n2
        v1 = v2
    
    O1 = points[-2]
    O2 = points[-1]    
    A2 = O2 + n1 * width/2
    B2 = O2 - n1 * width/2
    #draw_segment(A1, B1, A2, B2)
    triangulate_lane_segment(A1, A2, O1, O2, color, vertex_data)
    triangulate_lane_segment(B1, B2, O1, O2, color, vertex_data)

    #plt.gca().set_aspect('equal', adjustable='box')
    #plt.show()
    return np.concatenate(vertex_data).astype(np.float32)

####################################################

vertex_shader_code = """
#version 330 core

layout (location = 0) in vec2 position;
layout (location = 1) in vec4 color;

out vec4 vertex_color;

uniform mat4 m_position;
uniform mat4 m_camera;
uniform mat4 m_projection;

void main()
{
    gl_Position = m_projection * vec4(position.x, position.y, 0, 1.0);
    vertex_color = color;
}
"""

fragment_shader_code = """
#version 330 core

in vec4 vertex_color;
out vec4 color;

void main()
{
    color = vertex_color;
}
"""

vertex_dtype = [('pos', np.float32, 2),
                ('color', np.float32, 4)]

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
        [30, 0]
    ])

    vertices = create_road(points, 6)
    
    #vertices = np.array([
    #    -0.8,  0.8, 1,0,0,1,
    #     0.0,  0.8, 1,0,0,1,
    #     0.0, -0.8, 1,0,0,1,
    #     0.8,  0.8, 0,1,0,1,
    #     0.0,  0.8, 0,1,0,1,
    #     0.0, -0.8, 0,1,0,1 
    #], dtype=np.float32)


    # Create shaders
    vertex_shader = shaders.compileShader(vertex_shader_code, GL_VERTEX_SHADER)
    fragment_shader = shaders.compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)
    shader_program = shaders.compileProgram(vertex_shader, fragment_shader)
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    # Transformations
    uniform_proj = glGetUniformLocation(shader_program, 'm_projection')
    uniform_camera = glGetUniformLocation(shader_program, 'm_camera')
    uniform_pos = glGetUniformLocation(shader_program, 'm_position')    
    
    mat_proj = glm.ortho(-5.0, 40.0, -5.0, 30.0, -1.0, 1.0)
    mat_camera = glm.mat4(1.0)
    mat_position = glm.mat4(1.0)

    glUseProgram(shader_program)
    glUniformMatrix4fv(uniform_proj, 1, GL_FALSE, glm.value_ptr(mat_proj))
    #glUniformMatrix4fv(uniform_camera, 1, GL_FALSE, glm.value_ptr(mat_camera))
    #glUniformMatrix4fv(uniform_pos, 1, GL_FALSE, glm.value_ptr(mat_position))



    # Create buffers
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    vbo = VBO(vertices, GL_STATIC_DRAW)

    # Position data
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_TRUE, 6 * sizeof(ctypes.c_float), ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Color data
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 6 * sizeof(ctypes.c_float), ctypes.c_void_p(2*sizeof(ctypes.c_float)))
    glEnableVertexAttribArray(1)
    vbo.unbind()

    glBindVertexArray(0)

    glClearColor(0.1, 0.2, 0.3, 1.0)
    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        
        glUseProgram(shader_program)
        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, len(vertices))
        glBindVertexArray(0)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == '__main__':
    main()