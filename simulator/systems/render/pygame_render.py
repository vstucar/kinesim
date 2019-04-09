# This file is licensed under MIT license.
# See the LICENSE file in the project root for more information.

import pygame
from simulator.ecs.core import EventBus
import simulator.ecs.stdevent as stdevent
from simulator.components.components import *
from simulator.systems.systems import *
import simulator.events as events
import simulator.helpers.log_helper as log_helper

render_logger = log_helper.getLogger('Render')


class Sprite(pygame.sprite.Sprite):
    """
    Sprite wrapper with simplified position and rotation set
    """
    def __init__(self, pos, size,  color):
        pygame.sprite.Sprite.__init__(self)
        self.__image0 = pygame.Surface([size[0]+2, size[1]+2])
        self.__image0.fill((0, 0, 0, 0))
        self.__image0.set_colorkey((0, 0, 0, 0))
        pygame.draw.rect(self.__image0, color, (1, 1, size[0], size[1]))  # When rect size == surf size, rotate not work
        self.__rect0 = self.__image0.get_rect(center=pos)
        self.__rot = 0
        self.__apply_transform()

    @property
    def pos(self):
        return self.__rect0.center

    @pos.setter
    def pos(self, value):
        self.__rect0.center = value
        self.__apply_transform()

    @property
    def rot(self):
        return self.__rot

    @rot.setter
    def rot(self, value):
        self.__rot = value
        self.__apply_transform()

    def __apply_transform(self):
        self.image = pygame.transform.rotate(self.__image0, self.rot)
        self.rect = self.image.get_rect(center=self.__rect0.center)


class PyGameRenderSystem:
    """
    Rendering with pygame
    """
    def __init__(self):
        render_logger.debug('Initialization')
        EventBus.subscribe(stdevent.EVENT_SETUP, self.__setup)
        EventBus.subscribe(stdevent.EVENT_TEARDOWN, self.__teardown)
        EventBus.subscribe(stdevent.EVENT_UPDATE, self.__update)
        EventBus.subscribe(events.EVENT_INIT_GRAPHICS, self.__setup_graphics)

    # setup renderer and set pygame
    def __setup(self, engine):
        render_logger.debug('Setup')
        self.__engine = engine

        pygame.init()
        self.__screen = pygame.display.set_mode((600, 600), 0, 32)
        pygame.display.set_caption("Simple Car Simulator")
        self.__bg_color = pygame.Color(255, 255, 255, 255)

    # Called after all VisualComponent created and create their visual representation
    # Dynamic VisualComponent adding/removing not supported for now
    def __setup_graphics(self, engine):
        sprites = []
        for visual_comp in self.__engine.get_components_by_class(VisualComponent):
            position_cmp = visual_comp.parent.get_first_component_by_class(PositionComponent)
            kinematic_cmp = visual_comp.parent.get_first_component_by_class(KinematicComponent)
            sprite = Sprite(position_cmp.pos, kinematic_cmp.size, visual_comp.color)
            visual_comp.ext.sprite = sprite
            sprites.append(sprite)
        self.__allsprites = pygame.sprite.RenderPlain(sprites)

    # Deinit pygame
    def __teardown(self, engine):
        render_logger.debug('Teardown')
        pygame.quit()

    # Update sprites and do rendering
    def __update(self, engine, dt):
        self.__screen.fill(self.__bg_color)

        for visual_comp in self.__engine.get_components_by_class(VisualComponent):
            position_cmp = visual_comp.parent.get_first_component_by_class(PositionComponent)
            visual_comp.ext.sprite.pos = position_cmp.pos
            visual_comp.ext.sprite.rot = position_cmp.rot

        self.__allsprites.draw(self.__screen)
        pygame.display.update()