# config file

global config

config = dict()

# play music
config['playMusic'] = 0

# play sound
config['playSound'] = 0

# fps limit
config['fpsLimit'] = 60

# full screen
config['fullScreen'] = 1

# screen dimensions
config['screenWidth'] = 320
config['screenHeight'] = 240

# animation delays and lifetimes
config['animationDelay'] = 300
config['animationCursorDelay'] = 100
config['animationExplosionDelay'] = 100
config['explosionLifeTime'] = 500
config['animationRockExplosionDelay'] = 100
config['rockExplosionLifeTime'] = 380


# starting time and level
config['startTime'] = 30000
config['startLevel'] = 1

# object speed
config['objectSpeed'] = 2.5

# grabbed object speed
config['maxObjectSpeed'] = 8.0

# satellite life
config['satelliteLife'] = 3

# grabbing time (msec)
config['grabTime'] = 100000

# object invulnerability length after collision (msec)
config['collisionTimeout'] = 150

# show direction of satellite movement
config['debugShowDir'] = False

# show frame drawing time
config['debugFrameTime'] = False

# how much points and time is given for one collision
config['levelPoints'] = (0, 10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, \
    50000, 100000, 500000, 999999)
config['levelTime'] = (2000, 1800, 1600, 1400, 1200, 1000, 750, 500, 300, 250, 200, 100, \
              90, 80, 70, 60, 50, 40, 30)


# trail colors
config['trailColors'] = ((219, 252, 252), (134, 220, 252), \
    (37, 170, 234), (5, 94, 212))
