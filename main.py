#!/usr/env/python

# This file is licensed under MIT license.
# See the LICENSE file in the project root for more information.

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QOpenGLVersionProfile, QSurfaceFormat
from widgets.main_window import  MainWindow


def main():
    fmt = QSurfaceFormat()
    fmt.setVersion(4, 1)
    fmt.setProfile(QSurfaceFormat.CoreProfile)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)

    vp = QOpenGLVersionProfile()
    vp.setVersion(4, 1)
    vp.setProfile(QSurfaceFormat.CoreProfile)

    app = QApplication(sys.argv)
    window = MainWindow(vp)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
