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

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, version_profile=None):
        super(self.__class__, self).__init__()
        self.version_profile = version_profile

    def initializeGL(self):
        glClearColor(0.1, 0.2, 0.3, 1.0)

        positions = [0.5,  0.5, 0.0,
                     0.5, -0.5, 0.0,
                    -0.5, -0.5, 0.0,
                    -0.5,  0.5, 0.0]
        indexes = [0, 1, 3, 1, 2, 3]

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

        ibo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(ctypes.c_uint) * len(indexes), (ctypes.c_uint * len(indexes))(*indexes), GL_STATIC_DRAW)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, sizeof(ctypes.c_float) * len(positions), (ctypes.c_float * len(positions))(*positions), GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(ctypes.c_float), ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindVertexArray(0)


    def paintGL(self):
        #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self._shader)
        glBindVertexArray(self.__vao)
        #glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)


    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
