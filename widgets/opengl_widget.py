# This file is licensed under MIT license.
# See the LICENSE file in the project root for more information.

from PyQt5.QtGui import (
        QOpenGLBuffer,
        QOpenGLShader,
        QOpenGLShaderProgram,
        QOpenGLVersionProfile,
        QOpenGLVertexArrayObject,
        QSurfaceFormat,
    )
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GL import shaders
from ctypes import sizeof
import numpy as np
#import OpenGL.arrays.vbo
from OpenGL.arrays.arraydatatype import ArrayDatatype

c_float_p = ctypes.POINTER(ctypes.c_float)
c_uint32_p = ctypes.POINTER(ctypes.c_uint32)


def np_to_float_p(array):
    return array.ctypes.data_as(c_float_p)


def np_to_uint32_p(array):
    return array.ctypes.data_as(c_float_p)


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


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, version_profile=None):
        super(self.__class__, self).__init__()
        self.version_profile = version_profile

    def initializeGL(self):
        glClearColor(0.1, 0.2, 0.3, 1.0)

        positions = np.array([0.5,  0.5, 0.0,
                              0.5, -0.5, 0.0,
                             -0.5, -0.5, 0.0,
                             -0.5,  0.5, 0.0],
                             dtype=np.float32)
        indexes = np.array([0, 1, 3, 1, 2, 3], dtype=np.uint32)

        vertex_shader_code = """
        #version 330 core
        layout (location = 0) in vec3 position;
        void main() {
            gl_Position = vec4(position.x, position.y, position.z, 1.0);
        }
        """

        fragment_shader_code = """
        #version 330 core
        out vec4 color;
        void main() {
            color = vec4(1.0f, 0.5f, 0.2f, 1.0f);
        }
        """

        vertex_shader = shaders.compileShader(vertex_shader_code, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(fragment_shader_code, GL_FRAGMENT_SHADER)
        self._shader = shaders.compileProgram(vertex_shader, fragment_shader)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        self.__vao = glGenVertexArrays(1)
        glBindVertexArray(self.__vao)
        ebo = EBO(indexes, GL_STATIC_DRAW)
        vbo = VBO(positions, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(ctypes.c_float), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindVertexArray(0)


    def paintGL(self):
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self._shader)
        glBindVertexArray(self.__vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0)
        #glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)


    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
