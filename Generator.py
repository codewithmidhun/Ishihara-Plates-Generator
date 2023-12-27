import math
import random
import datetime
import time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

start_time = time.time()

white = (255, 255, 255, 255)
black = (0, 0, 0, 255)
dark_grey = (50, 50, 50, 255)

background_colour = white
display_size = 900
outer_radius = display_size / 2
(width, height) = (display_size, display_size)
middle = (width / 2, height / 2)

screen = Image.new("RGBA", (width, height), background_colour)
progressbar = Image.new("RGBA", (width, height), background_colour)

running = True
schablone = Image.open("hahalol.jpg")
schablone_size = schablone.size

scaling_factor_x = schablone_size[0] / width
scaling_factor_y = schablone_size[1] / height

min_radius = 4
max_radius = 15
shifting_range = 30
modify_range = 1.5
gradient_range = 0.3

do_colorschwift = False
do_lightschwift = False
do_gradientshift = False

use_bw = False
use_redgreen = False

iterations = 50000

if use_redgreen:
    color1 = (148, 173, 81)
    color2 = (217, 111, 71)
else:
    color1 = (202, 252, 3)
    color2 = (6, 138, 214)


def colorschwift(color, intervall):
    color = np.clip(np.random.randint(color - intervall, color + intervall + 1), 0, 255)
    return tuple(color)


def lightschwift(color, modifier):
    modifier = 1 / modifier if modifier < 1 else modifier
    modifier = random.uniform(1 / modifier, modifier)
    color = np.clip((np.array(color) * modifier).astype(int), 0, 255)
    return tuple(color)


def gradientshift(first_color, second_color, gradient_range):
    gradient_change = random.uniform(0, gradient_range)
    difference = np.array(first_color) - np.array(second_color)
    first_color = np.clip(first_color - (difference * gradient_change), 0, 255)
    return tuple(first_color)


class Circle:
    def __init__(self, x, y, radius, state):
        self.x = x
        self.y = y
        self.radius = radius
        self.state = state  # only useful for b/w drawing

    def draw(self, draw):
        if use_bw:
            if self.state:
                farbe = color1
                farbe2 = color2
            else:
                farbe = color2
                farbe2 = color1
            if do_gradientshift:
                farbe = gradientshift(farbe, farbe2, gradient_range)
        else:
            farbe = schablonenfarbe
        if do_colorschwift:
            farbe = colorschwift(farbe, shifting_range)
        if do_lightschwift:
            farbe = lightschwift(farbe, modify_range)
        draw.ellipse(
            [(self.x - self.radius, self.y - self.radius),
             (self.x + self.radius, self.y + self.radius)],
            outline=farbe, fill=farbe
        )


circles = []

for i in range(iterations):
    random_x = random.randint(0, schablone_size[0] - 1)
    random_y = random.randint(0, schablone_size[1] - 1)

    resize_x = int(random_x / scaling_factor_x)
    resize_y = int(random_y / scaling_factor_y)
    schablonenfarbe = schablone.getpixel((random_x, random_y))
    state = schablonenfarbe == black

    if not ((screen.getpixel((resize_x, resize_y))) == background_colour):
        continue

    distance_to_origin = math.dist((resize_x, resize_y), middle)
    biggest_possible_radius = outer_radius - distance_to_origin

    if not (biggest_possible_radius > min_radius):
        continue

    for circle in circles:
        current_radius = math.dist((resize_x, resize_y), (circle.x, circle.y)) - circle.radius
        if current_radius < biggest_possible_radius:
            biggest_possible_radius = current_radius
            if biggest_possible_radius < min_radius:
                break

    if biggest_possible_radius >= min_radius:
        biggest_possible_radius = min(int(biggest_possible_radius), max_radius)
        myCircle = Circle(resize_x, resize_y, biggest_possible_radius, state)
        circles.append(myCircle)
        myCircle.draw(ImageDraw.Draw(screen))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] or not running:
        break
    if keys[pygame.K_ESCAPE]:
        break

print(str(i + 1) + "/" + str(iterations))
print("fertig mit malen :)")
print(len(circles))
print("--- %s seconds ---" % (time.time() - start_time))

while running:
    screen.show()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for circle in circles:
                if math.dist(mouse_pos, (circle.x, circle.y)) < circle.radius:
                    circle.state = not circle.state
                    circle.draw(ImageDraw.Draw(screen))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False

fileoutput = f"testcircle_from_{datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')}.jpg"
screen.save(fileoutput)
pygame.quit()
