#!/usr/bin/python

# This file is licensed under MIT license.
# See the LICENSE file in the project root for more information.

import numpy as np
import logging
import pygame
from pygame.locals import *
from ecs.core import *
from simulator.components import *
from render.pygame_render import PyGameRenderSystem
from simulator.systems import *
import events
import log_helper

log_helper.setLevel('Event Bus', logging.WARN)


# Game loop stopping
main_loop = True
def pyevent_system(state, dt):
    global main_loop
    for event in pygame.event.get():
        if event.type == QUIT:
            main_loop = False


def main():
    engine = Engine()

    # Setup all systems. The order is important
    EventBus.subscribe(stdevent.EVENT_UPDATE, pyevent_system)
    EventBus.subscribe(stdevent.EVENT_UPDATE, control_system)
    render_system = PyGameRenderSystem()

    # Create entity
    car = Entity('car1')
    car.add_component(PositionComponent(np.array([100.0, 100.0])))
    car.add_component(VisualComponent((255, 0, 0)))
    car.add_component(ControlComponent(np.array([10, 0])))
    car.add_component(KinematicComponent((60, 30)))
    engine.add_entity(car)

    # Notify renderer that all graphics is set
    EventBus.publish(events.EVENT_INIT_GRAPHICS, engine)

    clock = pygame.time.Clock()
    while main_loop:
        clock.tick(30)
        engine.update(1/30.0)


if __name__ == '__main__':
    main()
