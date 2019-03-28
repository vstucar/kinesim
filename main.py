#!/usr/bin/python
from ecs.core import *


class PositionComponent(BaseComponent):
    def __init__(self, x=0, y=0):
        super(self.__class__, self).__init__()
        self.x = x
        self.y = y


class ControlComponent(BaseComponent):
    def __init__(self, throttle=0):
        super(ControlComponent, self).__init__()
        self.throttle = throttle


class VisualComponent(BaseComponent):
    def __init__(self, wtf):
        super(self.__class__, self).__init__()
        self.wtf = wtf


def control_system(state):
    print('render_system update')
    for control_cmp in state.get_components_by_class(ControlComponent):
        position_cmp = control_cmp.parent.get_first_component_by_class(PositionComponent)
        if position_cmp is not None:
            print('\t#%s: apply throttle %d' % (control_cmp.parent.name, control_cmp.throttle))
            position_cmp.x += control_cmp.throttle


def render_system(state):
    print('render_system update')
    for visual_cmp in state.get_components_by_class(VisualComponent):
        position_cmp = visual_cmp.parent.get_first_component_by_class(PositionComponent)
        if position_cmp is not None:
            print('\t#%s: %s at (%d, %d)' % (visual_cmp.parent.name, visual_cmp.wtf, position_cmp.x, position_cmp.y))


def main():
    engine = Engine()
    EventBus.subscribe(stdevent.EVENT_UPDATE, control_system)
    EventBus.subscribe(stdevent.EVENT_UPDATE, render_system)

    car = Entity('car1')
    car.add_component(PositionComponent(0, 0))
    car.add_component(VisualComponent('car_visual'))
    car.add_component(ControlComponent(1))
    engine.add_entity(car)

    for i in range(5):
        engine.update()


if __name__ == '__main__':
    main()
