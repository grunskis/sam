import pygame, os, subprocess

import ConfigParser

from pygame.locals import *

def clear(surface):
    surface.fill(pygame.Color("black"))

def text_surface(font, text, current):
    if current:
        text = "[ " + text + " ]"
    return font.render(text, False, pygame.Color("white"))

def draw_menu(menu, screen, font, offsety, current):
    width = pygame.display.Info().current_w

    (items, up, down) = menu

    for i, item in enumerate(items):
        text = text_surface(font, item, i == current)
        x = width / 2.0 - text.get_width() / 2.0
        screen.blit(text, (x, offsety + 50 * i))

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

def split(items, first, count):
    count = min([count, len(items)])
    last = first + count

    if len(items[first:last]) < count:
        first = len(items[first:last])

    up = True if first > 0 else False
    down = True if last < len(items) else False
        
    return (items[first:last], up, down)


pygame.init()

config = ConfigParser.SafeConfigParser({ 'mame_config': '' })
config.read("sam.conf")

games = ConfigParser.SafeConfigParser()
games.read("games.conf")

joystick_required = config.getboolean('sam', 'joystick_required')
if joystick_required and not pygame.joystick.get_count():
    print "Joystick not found..."
    os._exit(0)

mame_path = config.get('sam', 'mame_path')
mame_config = config.get('sam', 'mame_config')

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

use_sound = config.getboolean('sam', 'use_sound')
if use_sound:
    sound = pygame.mixer.Sound(os.path.join(basedir, "data", "sound.wav"))
    sound.set_volume(0.4)

try:
    stick = pygame.joystick.Joystick(0)
    stick.init()
except pygame.error:
    if joystick_required:
        os._exit(0)

menu = games.options('all')
menu.sort()

first = 0
current = 0

per_screen = int(pygame.display.Info().current_h / 50.0) - 2
offsety = (pygame.display.Info().current_h / 2.0) - (per_screen * 50 / 2.0)

draw_menu(split(menu, first, per_screen), screen, font, offsety, current)
pygame.display.flip()

while True:
    command = input(pygame.event.get())

    if command:
        clear(screen)

        if command == "move-next" and current < len(menu)-1:
            if use_sound:
                sound.play()
            
            current += 1
            if first + current > per_screen-1:
                first += 1
        elif command == "move-previous" and current > 0:
            if use_sound:
                sound.play()
            
            current -= 1
            if first > current:
                first -= 1
        elif command == "select":
            pygame.event.clear()

            # need to get out of fullscreen to start mame
            if flags & pygame.FULLSCREEN == pygame.FULLSCREEN:
                pygame.display.set_mode(resolution, 0)

            rom = games.get('all', menu[current])
            if len(mame_config) > 0:
                subprocess.call([mame_path, "-cfg", mame_config, rom])
            else:
                subprocess.call([mame_path, rom])

            # restore fullscreen mode if it was previoudly set
            if flags & pygame.FULLSCREEN == pygame.FULLSCREEN:
                pygame.display.set_mode(resolution, flags)
        elif command == "quit":
            os._exit(0)

        draw_menu(split(menu, first, per_screen), screen, font, offsety, current - first)
        pygame.display.flip()

    pygame.time.delay(100)
