from ecs.core import *
import numpy as np


class PositionComponent(BaseComponent):
    def __init__(self, pos=np.zeros(2), rot=0):
        super(self.__class__, self).__init__()
        self.pos = pos
        self.rot = rot


class ControlComponent(BaseComponent):
    def __init__(self, acc=np.zeros(2)):
        super(ControlComponent, self).__init__()
        self.acc = acc


class KinematicComponent(BaseComponent):
    def __init__(self, size):
        super(KinematicComponent, self).__init__()
        self.speed = np.zeros(2)
        self.size = size


class VisualComponent(BaseComponent):
    def __init__(self, color):
        super(self.__class__, self).__init__()
        self.color = color
