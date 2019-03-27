#!/usr/bin/python
import pygame
from pygame.locals import *
import os

pygame.init()
screen = pygame.display.set_mode((600, 600), 0, 32)
pygame.display.set_caption("Simple Car Simulator")
mainLoop = True


class Car(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image0 = pygame.Surface([100, 100])
        self.image0.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image0, (255, 0, 0), (1, 1, 98, 98))  # When rect size == surf size, rotate not work
        self.rect0 = self.image0.get_rect(center=(200, 200))

        self.image = self.image0
        self.rect = self.rect0
        self.rot = 0

    def update(self, *args):
        self.rot += 1
        self.rot_center(self.rot)

    def rot_center(self, angle):
        self.image = pygame.transform.rotate(self.image0, angle)
        self.rect = self.image.get_rect(center=self.rect0.center)


bg_color = pygame.Color(255, 255, 255, 255)
clock = pygame.time.Clock()

car = Car()
allsprites = pygame.sprite.RenderPlain((car))

while mainLoop:
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == QUIT:
            mainLoop = False

    allsprites.update()

    screen.fill(bg_color)
    allsprites.draw(screen)
    pygame.display.update()
pygame.quit()
