# This file is licensed under MIT license.
# See the LICENSE file in the project root for more information.

from PyQt5.QtWidgets import QMainWindow
import ui.MainWindow
from opengl_widget import OpenGLWidget


class MainWindow(QMainWindow, ui.MainWindow.Ui_MainWindow):
    def __init__(self, version_profile):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.gl_widget = OpenGLWidget(version_profile=version_profile)
        self.layout_scene.addWidget(self.gl_widget)