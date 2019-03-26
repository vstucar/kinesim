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


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, version_profile=None):
        super(self.__class__, self).__init__()
        self.version_profile = version_profile

    def initializeGL(self):
        self.gl = self.context().versionFunctions(self.version_profile)
        if not self.gl:
            raise RuntimeError("unable to apply OpenGL version profile")

        self.gl.initializeOpenGLFunctions()
        self.gl.glClearColor(0.0, 0.0, 0.0, 0.0)

    def paintGL(self):
        if not self.gl:
            return
        self.gl.glClear(self.gl.GL_COLOR_BUFFER_BIT | self.gl.GL_DEPTH_BUFFER_BIT)

    def resizeGL(self, w, h):
        self.gl.glViewport(0, 0, w, h)