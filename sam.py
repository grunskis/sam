import pygame, os, subprocess

import ConfigParser

from pygame.locals import *

MAME_PATH = "advmame"
MAME_CONFIG = ""

def clear(surface):
    surface.fill(pygame.Color("black"))

def text_surface(font, text, current):
    if current:
        text = "[ " + text + " ]"
    return font.render(text, False, pygame.Color("white"))

def draw_menu(menu, screen, font, current):
    width = pygame.display.Info().current_w

    for index in range(len(menu)):
        option = menu[index]
        text = text_surface(font, option, index == current)
        x = width / 2 - text.get_width() / 2
        screen.blit(text, (x, 100 + 50 * index))

def event_next(event):
    if event.type == KEYDOWN and event.key == K_DOWN:
        return True
    if event.type == JOYAXISMOTION and event.axis == 1 and int(event.value) == -1:
        return True
    return False

def event_previous(event):
    if event.type == KEYDOWN and event.key == K_UP:
        return True
    if event.type == JOYAXISMOTION and event.axis == 1 and int(event.value) == 1:
        return True
    return False

def event_select(event):
    if event.type == KEYDOWN and event.key == K_RETURN:
        return True
    if event.type == JOYBUTTONDOWN and event.button == 0:
        return True
    return False

def event_quit(event):
    if event.type == QUIT:
        return True
    if event.type == KEYDOWN and event.key == K_ESCAPE:
        return True
    return False

def input(events):
    for event in events:
        if event_quit(event):
            return "quit"
        elif event_next(event):
            return "move-next"
        elif event_previous(event):
            return "move-previous"
        elif event_select(event):
            return "select"

def process(command, games):
    global current

    menu = games.options('all')
    
    if command == "quit":
        os._exit(0)
    elif command == "move-next":
        current += 1
        if current > len(menu)-1:
            current = 0
    elif command == "move-previous":
        current -= 1
        if current < 0:
            current = len(menu)-1
    elif command == "select":
        rom = games.get('all', menu[current])
        if len(MAME_CONFIG) > 0:
            subprocess.call([MAME_PATH, "-cfg", MAME_CONFIG, rom])
        else:
            subprocess.call([MAME_PATH, rom])
        return False

    return True

pygame.init()

config = ConfigParser.SafeConfigParser({ 'mame_config': '' })
config.read("sam.conf")

games = ConfigParser.SafeConfigParser()
games.read("games.conf")

if not pygame.joystick.get_count():
    print "Joystick not found..."
    os._exit(0)

MAME_PATH = config.get('sam', 'mame_path')
MAME_CONFIG = config.get('sam', 'mame_config')

flags = 0
resolution = tuple(map(int, config.get('sam', 'resolution').split('x')))

if config.getboolean('sam', 'fullscreen'):
    modes = pygame.display.list_modes()
    if len(modes) <= 0:
        print "No supported fullscreen modes found..."
        os._exit(0)
    flags = pygame.FULLSCREEN
    resolution = modes[0]

window = pygame.display.set_mode(resolution, flags)
screen = pygame.display.get_surface()

pygame.display.set_caption("Simple Arcade Menu")

basedir = os.path.dirname(os.path.abspath(__file__))
font = pygame.font.Font(os.path.join(basedir, "data", "slkscr.ttf"), 48)
sound = pygame.mixer.Sound(os.path.join(basedir, "data", "sound.wav"))

stick = pygame.joystick.Joystick(0)
stick.init()

current = 0
menu = games.options('all')

draw_menu(menu, screen, font, current)
pygame.display.flip()

while True:
    command = input(pygame.event.get())

    if command and process(command, games):
        clear(screen)
        draw_menu(menu, screen, font, current)
        pygame.display.flip()
        sound.play()

    pygame.time.delay(10)
