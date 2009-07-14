# library classes

import pygame
from pygame.locals import *
import Config
from Config import config


# animation class

class Animation:
    rect = Rect(0,0,0,0)
    image = None
    frameImage = None
    frame = -1
    frameDelay = config['animationDelay']
    frameTime = 0
    numFrames = 4
    
    def __init__(self):
        pass

    # paint animation
    def paint(self, screen):
        # change to next frame if appropriate
        self.nextFrame()
        
        # show object image
        screen.blit(self.frameImage, self.rect)
    pass

    # set next frame for display
    def nextFrame(self):
        # non-animation
        if self.numFrames <= 1:
            self.frameImage = self.image
            return

        # frame delay has not passed yet
        if pygame.time.get_ticks() - self.frameTime < self.frameDelay:
            return

        self.frameTime = pygame.time.get_ticks()

        self.frame += 1
        if (self.frame >= self.numFrames):
            self.frame = 0

        imr = self.image.get_rect()
        r = Rect(imr.width * self.frame / self.numFrames, 0, \
                 imr.width / self.numFrames, imr.height)
#        print r
        if (r.x + r.width > imr.width):
            r = imr
#            print r, self.image.get_rect(), self.numFrames
        self.frameImage = self.image.subsurface(r)
    pass
pass
