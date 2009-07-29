'''
TODO:
- find more suitable font
- intro text

Welcome, Glarxz. As you know we are planning invasion of the planet Earth and
subsequent enslavement of all its unwary natives. You will be responsible
for the important task of sabotaging Earthling satellites on Sector 9 of
the Earth orbit. Remember, the more satellites you will destroy the more
your bonus will be. Here is your Magnetic Attractor, Corporal.

- outro text depending on ending level

1 What?!? Your days are numbered, Corporal!
2 Lousy job, Corporal.
3 Could have been better, Corporal.
4 Work better, Corporal.
5 And here is your bonus, Corporal.
6 You did a fine job, Corporal.
7 Excellect work, Corporal!
8 I'm sure your promotion awaits you, Corporal.
9 The Earth will be ours, Corporal!

- high scores
- refactoring
- combos!
'''

import sys, pygame, random, math
from pygame.locals import *
from random import *
import Lib
from Lib import *
import Config
from Config import config


# constants


global assets
global objects
global particles
global game

# game parameters
game = None

# hash of all assets
assets = dict()

# list of all objects - objects, debris etc
objects = list()

# list of all particles
particles = list()




# cursor class (ccur)
class Cursor(Animation):
    imageNormal = None
    imagePressed = None
    isPressed = 0
    position = list()
    startTime = 0

    # grabbed satellite
    grabbed = None

    # grabbed animation
    animGrabbed = None

    
    def __init__(self, iNormal, iPressed):
        self.imageNormal = iNormal
        self.imagePressed = iPressed
        self.image = self.imageNormal
        self.numFrames = 1
        self.position = pygame.mouse.get_pos()
        self.rect = self.image.get_rect()
        self.frameDelay = config['animationCursorDelay']


    # paint mouse cursor
    def paint(self, screen):
        pos = pygame.mouse.get_pos()

        self.rect.centerx = pos[0]
        self.rect.centery = pos[1]

        if self.isPressed:
            Animation.paint(self, screen)
        else:
            screen.blit(self.image, self.rect)


    # paint pixel trail from cursor to grabbed satellite
    def paintTrail(self, screen):
        pos = pygame.mouse.get_pos()
        ln = math.floor(0.15 * math.sqrt((self.grabbed.fx - pos[0]) * \
                      (self.grabbed.fx - pos[0]) + \
                           (self.grabbed.fy - pos[1]) *
                           (self.grabbed.fy - pos[1])))

        dx = self.grabbed.fx - pos[0]
        dy = self.grabbed.fy - pos[1]
        m = max(abs(dx), abs(dy)) / 5
        dx /= m
        dy /= m

        xbase = pos[0]
        ybase = pos[1]
        for i in xrange(0, int(ln)):
            xbase += dx
            ybase += dy
            self.paintTrailRandom(screen, xbase, ybase)
            self.paintTrailRandom(screen, xbase, ybase)
            self.paintTrailRandom(screen, xbase, ybase)

    def paintTrailRandom(self, screen, xbase, ybase):
        x = xbase - 20 + random() * 40
        y = ybase - 20 + random() * 40
        c = choice(config['trailColors'])
        col = Color(c[0], c[1], c[2])
        screen.set_at((int(x), int(y)), col)


    # set pressed state
    def setPressed(self, state):
        self.isPressed = state
        self.position = pygame.mouse.get_pos()

        if self.isPressed:
            self.image = self.imagePressed
            self.numFrames = 4
            self.startTime = pygame.time.get_ticks()

            # check for satellite to grab
            for o in objects:
                o.checkGrabbed()

            # satellite grabbed, make animation
            if self.grabbed != None:
                self.animGrabbed = Animation()
                self.animGrabbed.image = assets['satSelected']
                self.animGrabbed.numFrames = 2


        else:
            self.image = self.imageNormal
            self.numFrames = 1
            self.startTime = 0
            self.animGrabbed = None
            self.grabbed = None


    # update state
    def update(self, ticks):
        # check for grab release
        if self.isPressed and ticks - self.startTime > config['grabTime']:
            self.setPressed(0)
            self.grabbed = None;

        self.position = pygame.mouse.get_pos()

        if self.grabbed != None:
            # update mouse delta
            dx = self.position[0] - self.grabbed.fx
            dy = self.position[1] - self.grabbed.fy

#            print 'd:', dx, dy

            # normalize dx,dy
            m = max(abs(dx), abs(dy))
            fdx = 0
            fdy = 0
            if m > 0:
                fdx = config['maxObjectSpeed'] * float(dx) / float(m)
                fdy = config['maxObjectSpeed'] * float(dy) / float(m)

#            print 'd:', dx, dy, 'f:', fdx, fdy, ' m:', m

            if fdx != 0:
                if abs(fdx) > abs(dx):
                    fdx = dx
                self.grabbed.dirx = fdx

            if fdy != 0:
                if abs(fdy) > abs(dy):
                    fdy = dy
                self.grabbed.diry = fdy
        pass
    pass
pass


# world object class (cwo) - satellites, debris, etc
class WorldObject(Animation):
    # object type
    type = ''

    # life
    life = 1

    # current direction
    dx = 0.0
    dy = 0.0

    # float x,y
    fx = 0
    fy = 0

    # goal direction
    dirx = 0.0
    diry = 0.0

    # collision timeout parameters
    collideTime = 0
    isCollided = 0

    # object alive?
    isDead = 0

    # object was grabbed at some point
    isTouched = 0

    def __init__(self, type, onEdge = 0):
        self.__dict__['type'] = type

        if self.type == 'satellite':
            self.image = assets['satellite']
            self.life = config['satelliteLife']

        elif self.type == 'debris':
            self.image = assets['rock']
            self.life = 1

        # check for collision
        while 1:
            # spawn objects on screen edges during the game
            if not onEdge:
                x = randint(0, config['screenWidth'])
                y = randint(0, config['screenHeight'])
            else:
                x = randint(0, config['screenWidth'])
                y = randint(0, config['screenHeight'])

                if random() > 0.5:
                    if random() > 0.5:
                        x = 0
                    else:
                        x = config['screenWidth'] - 1
                else:
                    if random() > 0.5:
                        y = 0
                    else:
                        y = config['screenHeight'] - 1

            r = self.image.get_rect()
            if (self.numFrames > 1):
                r.width = 32
                r.height = 32
            self.__dict__['rect'] = Rect(x, y, r.width, r.height)

            ok = 1

            for o2 in objects:
                if self.rect.colliderect(o2.rect):
                    ok = 0

            if ok:
                break
        pass

        self.__dict__['dirx'] = config['objectSpeed'] * random() - 1
        self.__dict__['diry'] = config['objectSpeed'] * random() - 1

        self.__dict__['fx'] = self.rect.centerx
        self.__dict__['fy'] = self.rect.centery
    pass


    # setting attributes
    def __setattr__(self, name, value):
        if name == 'fx':
            self.__dict__['fx'] = value
            self.rect.centerx = value

        elif name == 'fy':
            self.__dict__['fy'] = value
            self.rect.centery = value

        else:
            self.__dict__[name] = value
    pass


    # paint this (cwop)
    def paint(self, screen):
        Animation.paint(self, screen)
        
        # show satellite movement direction
        if self.type == 'satellite' and config['debugShowDir']:
            r = Rect(self.rect.left, self.rect.top, 15, 15)
            r.centerx += 32 + self.dx * 10
            r.centery += 32 + self.dy * 10

            screen.blit(assets['dir'], r)

        # this object grabbed
        if cursor.grabbed == self:
            cursor.animGrabbed.rect.x = self.rect.left
            cursor.animGrabbed.rect.y = self.rect.top
            Animation.paint(cursor.animGrabbed, screen)
    pass


    # check for grabbing this object
    def checkGrabbed(self):
        # only satellites can be grabbed
        if self.type != 'satellite':
            return 0
        
        r = cursor.rect
        rect = Rect(cursor.position[0], cursor.position[1], \
                            r.width, r.height)

        if self.rect.colliderect(rect):
            cursor.grabbed = self
            self.isTouched = 1
            if config['playSound']:
                assets['sndGrab'].stop()
                assets['sndGrab'].play()

            return 1

        return 0
    pass


    # get $val damage from $obj (cwod)
    def damage(self, obj, val):
        # remove hp
        self.life -= val

        # change image
        img = ''
        if self.type == 'satellite':
            img = 'satellite'
            if self.life == config['satelliteLife'] - 1:
                img = 'satelliteDamaged1'
            elif self.life == config['satelliteLife'] - 2:
                img = 'satelliteDamaged2'

        elif self.type == 'debris':
            img = 'rock'

        self.image = assets[img]

        # object alive
        if self.life > 0:
            return
        
        # death
        self.isDead = 1

        # clean grabbed state from cursor
        if cursor.grabbed == self:
            cursor.setPressed(0)

        if self.type == 'satellite' or obj.type == 'satellite':
            points = 0

            # more points if both objects satellites
            if self.type == 'satellite' and obj.type == 'satellite':
                points = game.level
            elif self.type == 'satellite':
                points = 1

            if points > 0:
                game.addPoints(points)

                # create text
                e = Particle('text', '', self.rect.centerx, \
                             self.rect.centery - 10, 0, - 0.25)
                e.setText('+' + str(points))
                particles.append(e)

        # create explosion
        if self.type == 'satellite':
            e = Particle('image', assets['explosion'], \
                         self.rect.left, self.rect.top, self.dx, self.dy)
        elif self.type == 'debris':
            e = Particle('image', assets['rockExplosion'], \
                         self.rect.left, self.rect.top, self.dx, self.dy)
            e.frameDelay = config['animationRockExplosionDelay']
            e.lifeTime = config['rockExplosionLifeTime']
        particles.append(e)

        # delete object
        try:
            objects.remove(self)
        except:
            pass
    pass


    # check for collisions between two objects
    def checkCollision(self, o):
        if self == o or not self.rect.colliderect(o.rect):
            return

        # one of objects is already collided, waiting for timeout
        if self.isCollided or o.isCollided:
            return

        # get 1 damage
        self.damage(o, 1)
        o.damage(self, 1)

        # play appropriate sound
        if config['playSound']:
            if self.isDead or o.isDead:
                assets['sndExplosion'].play()
            else:
                assets['sndHit'].play()

        # bounce, change dir
        dirx = self.dirx - o.dirx
        diry = self.diry - o.diry
        o.dirx = dirx
        o.diry = diry
        self.dirx = - dirx
        self.diry = - diry

#        print 'self:', self.dirx, self.diry, 'o:', o.dirx, o.diry

#        waitForEvent()

        # move both in that dir
        if not self.isDead:
            self.fx += self.dirx
            self.fy += self.diry
        if not o.isDead:
            o.fx += o.dirx
            o.fy += o.diry

        # set collision timeout for both objects
        self.isCollided = 1
        self.collideTime = pygame.time.get_ticks()
        o.isCollided = 1
        o.collideTime = pygame.time.get_ticks()

#        if self == cursor.grabbed or o == cursor.grabbed:
#            cursor.setPressed(0)
    pass


    # update state (object movement) (cwou)
    def update(self, prevTicks, ticks):
        msec = ticks - prevTicks

        # remove collision timeout
        if self.isCollided and ticks - self.collideTime > config['collisionTimeout']:
            self.isCollided = 0

        # slightly randomize movement
        self.dirx += - 0.1 + 0.2 * random()
        self.diry += - 0.1 + 0.2 * random()

        # correct movement speed if not grabbed
        if cursor.grabbed != self and \
           math.hypot(self.dirx, self.diry) > config['objectSpeed']:
            # normalize to speed
            m = max(abs(self.dirx), abs(self.diry))
            self.dirx /= m
            self.diry /= m
            self.dirx *= config['objectSpeed']
            self.diry *= config['objectSpeed']

        # change slightly delta to dir
        self.dx += (self.dirx - self.dx) / 10.0
        self.dy += (self.diry - self.dy) / 10.0

        # change position by delta
        self.fx += 3 * float(self.dx) / float(msec)
        self.fy += 3 * float(self.dy) / float(msec)

        # check boundaries
        if self.fx >= config['screenWidth']:
            self.fx = 1
        if self.fx <= 0:
            self.fx = config['screenWidth'] - 1
        if self.fy >= config['screenHeight']:
            self.fy = 1
        if self.fy <= 0:
            self.fy = config['screenHeight'] - 1

        # spawn trail sprite if damaged
        if self.type == 'satellite' and \
           self.life < config['satelliteLife'] and \
           ((self.life > 1 and random() < 0.01) or \
            (self.life == 1 and random() < 0.03)):
            e = Particle('image', assets['explosion'], self.fx, self.fy, 0, 0)
            e.setTrail()
            particles.append(e)
        pass
    pass
pass


# particle class (cpart)
class Particle(Animation):
    type = ''
    text = ''
    startTime = 0
    lifeTime = config['explosionLifeTime']

    # float x,y
    fx = 0.0
    fy = 0.0

    # movement delta
    dx = 0.0
    dy = 0.0

    # trail parameters
    isTrail = 0
    trailLength = 0
    trailSpawnTime = 0

    def __init__(self, type, img, x, y, dx, dy):
        self.startTime = pygame.time.get_ticks()
        self.type = type

        if self.type == 'image':
            self.fx = x
            self.fy = y
            self.setImage(img)

            # normalize dir
            m = max(abs(dx), abs(dy))

            if m > 0:
                self.dx = 0.5 * dx / m
                self.dy = 0.5 * dy / m

        elif self.type == 'text':
            self.fx = x
            self.fy = y

            self.dx = dx
            self.dy = dy
    pass


    # set image
    def setImage(self, img):
        self.image = img
        self.frameDelay = config['animationExplosionDelay']
        self.rect = Rect(self.fx, self.fy, self.image.get_rect().height, \
                         self.image.get_rect().height)
        self.fx = self.rect.centerx
        self.fy = self.rect.centery
    pass


    # set text
    def setText(self, text):
        self.text = text

        size = font.size(self.text)
        self.image = font.render(self.text, 1, (0, 255, 0, 0),
                                 (50, 50, 50, 200));
        self.rect = Rect(self.fx - size[0] / 2, self.fy - size[1] / 2, \
                 size[0], size[1])
    pass


    # paint this
    def paint(self, screen):
        if self.type == 'image':
            Animation.paint(self, screen)

        elif self.type == 'text':
            screen.blit(self.image, self.rect)

    # set trail var
    def setTrail(self):
        self.isTrail = 1
        self.image = assets['smoke']
        self.rect.centerx -= 16
        self.rect.centery -= 16


    # update state
    def update(self, ticks):
        global particles
        
        # remove explosion on timeout
        if ticks - self.startTime > self.lifeTime:
            particles.remove(self)

        if self.isTrail:
            return

        if self.type == 'image' and self.image == assets['explosion']:
            # spawn trail sprite
            if ticks - self.trailSpawnTime > 200 :
                e = Particle('image', assets['explosion'], self.fx, self.fy, 0, 0)
                e.setTrail()
                particles.append(e)
                self.trailSpawnTime = ticks
                self.trailLength += 1

        # movement
        self.fx += self.dx
        self.fy += self.dy

        self.rect.centerx = self.fx
        self.rect.centery = self.fy
    pass
pass


# main game class (cgam)
class Game:
    points = 0
    level = config['startLevel']
    numSatellites = 0
    numDebris = 0
    time = config['startTime']
    warnStartTime = 0

    # timer ticks
    prevTicks = pygame.time.get_ticks()
    ticks = prevTicks + 1

    #isPaused = False
    isFinished = False

    def __init__(self):
        global objects

        # init cursor
        cursor.setPressed(0)

        self.numDebris = self.level
        self.numSatellites = 2 + self.level / 2

        objects = list()

        # spawn objects
        for i in xrange(self.numSatellites):
            o = WorldObject('satellite')

            for o2 in objects:
                if o.rect.colliderect(o2.rect):
                    o = WorldObject('satellite')

            objects.append(o)
        pass

        # spawn debris
        for i in xrange(self.numDebris):
            o = WorldObject('debris')

            for o2 in objects:
                if o.rect.colliderect(o2.rect):
                    o = WorldObject('debris')

            objects.append(o)
        pass

#        for i in xrange(1, 10):
#            print i, 850.0 * float(2 + 0.5 * i) / (float(i))
#            print 'd', i, 500.0 * float(1 + 1.0) / (float(i))
    pass


    # add points, raise level if needed
    def addPoints(self, points):
        time = config['levelTime'][self.level]
        if points == 1 and self.level > 1:
            time /= 4.0

        self.points += points
        self.time += time
#        print 'PTS', points, 'T+', time

        # check for new level
        newLevel = 0
        for l in config['levelPoints']:
            if self.points >= l:
                newLevel += 1
        pass    

        # level not raised
        if self.level >= newLevel:
            return

        # raise level and difficulty
        self.level = newLevel
        self.numDebris = self.level
        self.numSatellites = 2 + self.level / 2

        # play sound
        if config['playSound']:
            assets['sndLevel'].play()

#        print 'l:', self.level, 'sats:', self.numSatellites, 'debris:',\
#            self.numDebris
    pass


    # check for game finish
    def checkFinish(self):
        # player still has time
        if self.time > 0:
            return

        self.isFinished = True
    pass


    # update game state (cgamup)
    def update(self):
        # count number of ticks passed
        self.ticks = pygame.time.get_ticks()

        # time passed
        self.time -= (self.ticks - self.prevTicks)

        if self.ticks - self.prevTicks == 0:
            return

        # warning sound when time is low
        if self.time <= 5000 and self.ticks - self.warnStartTime > 500:
            self.warnStartTime = self.ticks
            if config['playSound']:
                assets['sndTime'].play()

        # check for finish
        self.checkFinish()

        # update cursor
        cursor.update(self.ticks)

        # update particles
        for p in particles:
            p.update(self.ticks)

        # update objects
        for o in objects:
            o.update(self.prevTicks, self.ticks)

        # check objects for collisions
        for o in objects:
            for o2 in objects:
                o.checkCollision(o2)

        # spawn more satellites if needed
        cnt = countObjects('satellite')
        if cnt < self.numSatellites:
            o = WorldObject('satellite', 1)
            objects.append(o)

        # spawn more debris if needed
        cnt = countObjects('debris')
        if cnt < self.numDebris:
            o = WorldObject('debris', 1)
            objects.append(o)

        self.prevTicks = self.ticks
    pass
pass


# load all assets
def loadAssets():
    global assets

    # images
    assets['bg'] = pygame.image.load("assets/bg.png")
    assets['cursorNormal'] = pygame.image.load("assets/cursor.png")
    assets['cursorPressed'] = pygame.image.load("assets/cursor_pressed.png")
    assets['dir'] = pygame.image.load("assets/dir.png")
    assets['satellite'] = pygame.image.load("assets/sat1.png")
    assets['satelliteDamaged1'] = pygame.image.load("assets/sat1_dmg1.png")
    assets['satelliteDamaged2'] = pygame.image.load("assets/sat1_dmg2.png")
    assets['satSelected'] = pygame.image.load("assets/sat_sel.png")
    assets['explosion'] = pygame.image.load("assets/explosion.png")
    assets['explosionTrail'] = pygame.image.load("assets/explosion_trail.png")
    assets['smoke'] = pygame.image.load("assets/smoke.png")
    assets['rock'] = pygame.image.load("assets/rock.png")
    assets['rockExplosion'] = pygame.image.load("assets/rock_explosion.png")

    # sounds
    if config['playSound']:
        assets['sndExplosion'] = pygame.mixer.Sound("assets/snd_explosion.ogg")
        assets['sndGrab'] = pygame.mixer.Sound("assets/snd_grab.ogg")
        assets['sndHit'] = pygame.mixer.Sound("assets/snd_hit.ogg")
        assets['sndLevel'] = pygame.mixer.Sound("assets/snd_level.ogg")
        assets['sndTime'] = pygame.mixer.Sound("assets/snd_time.ogg")
pass


# event handling
def handleEvents():
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif e.type == pygame.KEYDOWN:
            # esc exits game
            if e.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

            if e.key == K_SPACE:
                #game.isPaused = True
                introText(font, ("Game is paused.",
                                 "Press any key to continue"))

                # clean ticks because of pause
                game.prevTicks = pygame.time.get_ticks()
#                game.isPaused = False

            # F12 - toggle fullscreen
#            elif e.key == K_F12:
#                print 'ok'
#                pygame.display.toggle_fullscreen()

        # mouse pressed
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            cursor.setPressed(1)

        # mouse released
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            cursor.setPressed(0)
pass        


# count number of objects of this type
def countObjects(type):
    cnt = 0

    for o in objects:
        if o.type == type:
            cnt += 1

    return cnt
pass


# paint status panel
def paintStatus():
    text = 'Level: ' + str(game.level) + \
           '  Points: ' + str(int(game.points)) + \
           '  Time left: '
    if game.time >= 10000:
        text += str(int(game.time / 1000))
    else:
        text += '%.1f' % float(game.time / 1000.0)
    size = font.size(text)
    
    surf = font.render(text, 1, (255, 255, 255, 0));
    r = Rect(10, config['screenHeight'] - size[1] - 5, size[0], size[1])
    screen.blit(surf, r)
pass


# paint screen
def paintScreen():
    # paint trail
    if cursor.grabbed != None:
        cursor.paintTrail(screen)

    # paint objects
    for o in objects:
        o.paint(screen)

    # paint grabbed satellite
    if cursor.grabbed != None:
        cursor.grabbed.paint(screen)

    # paint particles
    for e in reversed(particles):
        e.paint(screen)

    # paint mouse cursor
    cursor.paint(screen)

    # paint status panel
    paintStatus()
pass


# waits for event
def waitForEvent():
    while 1:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif e.type == pygame.KEYDOWN:
                return
        pass
    pass
pass


# draw centered intro text 
def introText(fontIntro, textList):
    # clear screen
    screen.fill(black)

    height = fontIntro.get_height() + 20
    totalHeight = height * len(textList)

    cnt = 0
    for text in textList:
        size = fontIntro.size(text)
        surf = fontIntro.render(text, 1, (255, 255, 255, 0));
        r = Rect((config['screenWidth'] - size[0]) / 2, \
                 (config['screenHeight'] - size[1] - totalHeight + height * cnt) / 2, \
                 size[0], size[1])
        screen.blit(surf, r)

        cnt += 1
    pass

    # update screen
    pygame.display.flip()

    waitForEvent()
pass


# intro
def playIntro():
    # intro music
    if config['playMusic']:
        pygame.mixer.music.load("assets/mus_intro.ogg")
        pygame.mixer.music.play(-1)

    fontIntro = pygame.font.Font('freesansbold.ttf', 10)
    introText(fontIntro, 
              ("Satellite Dash v0.1", 
                   "Press and hold LEFT MOUSE BUTTON to grab satellites",
                   "Bump satellites into each other to gain points and time", 
                   "Press SPACE to pause game"))

    # ingame music
    if config['playMusic']:
        pygame.mixer.music.load("assets/mus_ingame.ogg")
        pygame.mixer.music.play(-1)
pass


# outro
def playOutro():
    # outro music
    if config['playMusic']:
        pygame.mixer.music.load("assets/mus_intro.ogg")
        pygame.mixer.music.play(-1)

    fontOutro = pygame.font.Font('freesansbold.ttf', 10)
    introText(fontOutro,
              ("GAME OVER",
               "Score: " + str(game.points)))

    pygame.quit()
    sys.exit()
pass


# main function

pygame.mixer.pre_init(44100, 16, 2, 2048)
pygame.init()
pygame.mouse.set_visible(False)

size = (config['screenWidth'], config['screenHeight'])
black = (0, 0, 0)

if config['fullScreen']:
    screen = pygame.display.set_mode(size, FULLSCREEN)
else:
    screen = pygame.display.set_mode(size)
font = pygame.font.Font('freesansbold.ttf', 10)

# load all needed assets
loadAssets()

# mouse cursor
cursor = Cursor(assets['cursorNormal'], assets['cursorPressed'])

# intro stuff
playIntro()

# start new game
game = Game()

clock = pygame.time.Clock()
bgRect = Rect(0,0, config['screenWidth'], config['screenHeight'])

while 1:
    clock.tick(config['fpsLimit'])

    if config['debugFrameTime']:
        ticksDebug = pygame.time.get_ticks()

    # handle user input
    handleEvents()

    # clear screen
    screen.fill(black)

    # draw background
    screen.blit(assets['bg'], bgRect)

    # update game state
    game.update()

    # game could finish in update()
    if game.isFinished:
        break

    # paint everything
    paintScreen()

    # update screen
    pygame.display.flip()

    if config['debugFrameTime']:
        print (pygame.time.get_ticks() - ticksDebug)


# outro stuff - display scores etc
playOutro()

pass
