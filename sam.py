import pygame, os, subprocess

from pygame.locals import *

MAME_PATH = "/home/martins/Tools/mame/bin/advmame"
MAME_CFG_PATH = "/home/martins/.advance/advmame.rc"

RESOLUTION = (800, 600)

MENU = [
    {"name": "pacman", "rom": "pacman"},
    {"name": "space invaders", "rom": "invaddlx"},
    {"name": "super mario", "rom": "mario"}
]

def clear(surface):
    surface.fill(pygame.Color("black"))

def text_surface(font, text, current):
    if current:
        text = "[ " + text + " ]"
    return font.render(text, False, pygame.Color("white"))

def draw_menu(menu, screen, font, current):
    width, _ = RESOLUTION

    for index in range(len(menu)):
        option = MENU[index]["name"]
        text = text_surface(font, option, index == current)
        x = width / 2 - text.get_width() / 2
        screen.blit(text, (x, 100 + 50 * index))

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

def process(command):
    global current
    
    if command == "quit":
        os._exit(0)
    elif command == "move-next":
        current += 1
        if current > len(MENU)-1:
            current = 0
    elif command == "move-previous":
        current -= 1
        if current < 0:
            current = len(MENU)-1
    elif command == "select":
        rom = MENU[current]["rom"]
        subprocess.call([MAME_PATH, "-cfg", MAME_CFG_PATH, rom])
        return False

    return True

pygame.init()

if not pygame.joystick.get_count():
    print "Joystick not found..."
    os._exit(0)

window = pygame.display.set_mode(RESOLUTION)
screen = pygame.display.get_surface()

pygame.display.set_caption("Simple Arcade Menu")

basedir = os.path.dirname(os.path.abspath(__file__))
font = pygame.font.Font(os.path.join(basedir, "data", "slkscr.ttf"), 48)
sound = pygame.mixer.Sound(os.path.join(basedir, "data", "sound.wav"))

stick = pygame.joystick.Joystick(0)
stick.init()

current = 0

draw_menu(MENU, screen, font, current)
pygame.display.flip()

while True:
    command = input(pygame.event.get())

    if command and process(command):
        clear(screen)
        draw_menu(MENU, screen, font, current)
        pygame.display.flip()
        sound.play()

    pygame.time.delay(10)
