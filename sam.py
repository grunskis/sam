import pygame, os, subprocess

from pygame.locals import *

MAME_PATH = "/home/martins/Tools/mame/bin/advmame"
MAME_CFG_PATH = "/home/martins/.advance/advmame.rc"

RESOLUTION = (800, 600)

MENU = {
    "pacman": {"rom": "pacman"},
    "space invaders": {"rom": "invaddlx"},
    "super mario": {"rom": "mario"}
}

def text_surface(font, text, current):
    if current:
        text = "[ " + text + " ]"
    return font.render(text, False, pygame.Color("white"))

def draw_menu(menu, screen, font, current):
    width, height = RESOLUTION

    for option in menu.keys():
        index = menu.keys().index(option)
        text = text_surface(font, option, index == current)
        x = width / 2 - text.get_width() / 2
        screen.blit(text, (x, 100 + 50 * index))
    
    pygame.display.update()

def event_next(event):
    if event.type == KEYDOWN and event.key == K_DOWN:
        return True
    if event.type == JOYAXISMOTION and event.axis == 1 and event.value == -1.0:
        return True
    return False

def event_previous(event):
    if event.type == KEYDOWN and event.key == K_UP:
        return True
    if event.type == JOYAXISMOTION and event.axis == 1 and event.value == 1.0:
        return True
    return False

def event_play(event):
    if event.type == KEYDOWN and event.key == K_RETURN:
        return True
    if event.type == JOYBUTTONDOWN and event.button == 0:
        return True
    return False

def input(events, menu, current):
    for event in events:
        if event.type == QUIT: 
            os._exit(0)
        elif event_next(event):
            current += 1
            if current > len(menu)-1:
                current = 0
            return current
        elif event_previous(event):
            current -= 1
            if current < 0:
                current = len(menu)-1
            return current
        elif event_play(event):
            rom = menu.get(menu.keys()[current])["rom"]
            subprocess.call([MAME_PATH, "-cfg", MAME_CFG_PATH, rom])
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            os._exit(0)

pygame.init()

if not pygame.joystick.get_count():
    print "Joystick not found..."
    os._exit(0)

window = pygame.display.set_mode(RESOLUTION)
pygame.display.set_caption("Simple Arcade Menu")
screen = pygame.display.get_surface()

basedir = os.path.dirname(os.path.abspath(__file__))
font = pygame.font.Font(os.path.join(basedir, "data", "slkscr.ttf"), 48)
sound = pygame.mixer.Sound(os.path.join(basedir, "data", "sound.wav"))

current = 0

stick = pygame.joystick.Joystick(0)
stick.init()

draw_menu(MENU, screen, font, current)

while True:
    selection = input(pygame.event.get(), MENU, current)
    if selection != None:
        current = selection
        screen.fill(pygame.Color("black")) # clear surface
        draw_menu(MENU, screen, font, current)
        sound.play()
    pygame.time.delay(10)
