import os
import random
import math
import pygame 
import asyncio
from os import listdir
from os.path import isfile, join
import sys
#from readLevel import *

pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5
level = 'levelOne.csv'
global window, Sprite
window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_apple(size):
    path = join("assets", "Items", "Powerups", "Apple", "Apple.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

def get_finish(size):
    path = join("assets", "finish.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0, 0, size, size)
    surface.blit(image, (-8, -15), rect)
    return pygame.transform.scale2x(surface)


class Burger(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = "burger"
        self.image.blit(pygame.image.load("assets/enemeies/Burger.png"), (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))
        
        

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.lifes = 3
        self.timesDone = 0

    def jump(self):
        if collide(self, objects, PLAYER_VEL * 2) != None and self.timesDone == 0 or collide(self, objects, -PLAYER_VEL * 2) != None and self.timesDone == 0:
            self.jump_count = 0
            self.timesDone += 1
        self.y_vel = jumpHeight
        self.animation_count = 0
        self.jump_count += 1
        self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        self.fall_count += 1
        self.update_sprite()

    def death(self):
        Black = (0, 0, 0)
        pygame.draw.rect(window, Black, (0, 0, 1000, 800))
        self.lifes -= 1
        font = pygame.font.Font('freesansbold.ttf', 32)
        if self.lifes < 0:
            text = font.render("Game Over", True,(255, 255,255))
            self.lifes =3
        else:    
            text = font.render(f'You Died  lives x{self.lifes}', True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (WIDTH // 2, HEIGHT // 2)
        window.blit(text, textRect)
        pygame.display.update()
        pygame.time.wait(1000)



    
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
        self.timesDone = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Button():
	def __init__(self, image, pos, text_input, font, base_color, hovering_color):
		self.image = image
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.base_color, self.hovering_color = base_color, hovering_color
		self.text_input = text_input
		self.text = self.font.render(self.text_input, True, self.base_color)
		if self.image is None:
			self.image = self.text
		self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			return True
		return False

	def changeColor(self, position):
		if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
			self.text = self.font.render(self.text_input, True, self.hovering_color)
		else:
			self.text = self.font.render(self.text_input, True, self.base_color)

class Apple(Object):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "apple")
        self.apple = load_sprite_sheets("Items\\Powerups", "Apple", width, height)
        block = get_apple(32)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        
        
class Finish(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "finish")
        block = get_finish(width)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
        
    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))



def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, player, object, offset_x):
    for tile in background:
        window.blit(bg_image, tile)
    
    for obj in object:
        obj.draw(window, offset_x)

    #level, levelRect = loadText()

    #window.blit(level, levelRect)

    player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
        

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "finish":
            global finishedLevel
            finishedLevel = True
            print('Finished Level')
            

    

def getLevel(level):
    array = []
    with open("levels/"+level , mode ='r') as file:   
        for lines in file.readlines():
                lines = lines.strip('\n')
                lines = lines.split(',')
                
                array.append(lines)
    
    return array

def loadLevel(level, block_size, levelCount):
    array = getLevel(level[levelCount])
    floor =[]
    object = []
    count = 0
    for counter in range(len(array)):
        for index in range(len(array[counter])):
                if array[counter][index] == '0':
                    pass
                elif array[counter][index] == '1':
                    count += 1
                elif array[counter][index] == '2':
                    floor.append(Block(count * block_size, HEIGHT - block_size, block_size))
                    count += 1
                elif array[counter][index] == '3':
                    object.append(Block(block_size * (index), HEIGHT - block_size * (counter +2), block_size))

                elif array[counter][index] == '4':
                    object.append(Finish(block_size * (index), HEIGHT - block_size * (counter +2), 124, 124))
                    
    return object+floor


def loadText():
    global levelNum
    level = font(35).render("press jump twice to double jump", True, "white")
    levelRect = "level.get_rect(center=(500, 260))"
    try:
        if levelNum == 0:
            level = font(35).render("Use arrows to move and up arrow to jump", True, "white")
            levelRect = level.get_rect(center=(500, 260))
        elif levelNum == 1:
            level = font(35).render("press jump twice to double jump", True, "white")
            levelRect = level.get_rect(center=(500, 260))
        elif levelNum == 2:
            level = font(35).render("you can wall jump by jumping into the wall youll gain a extra jump ", True, "white")
            levelRect = level.get_rect(center=(500, 260))
    except:
        level = font(45).render("well done you won")


    return level, levelRect
 
def font(size):
    return pygame.font.Font('freesansbold.ttf', size)  
    
    
def options():
    running=True
    while running:

        window.fill("white")
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        OPTIONS_TEXT = font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(500, 260))
        window.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(500, 460), 
                            text_input="BACK", font=font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    running = False
                
                    

        pygame.display.update()    
        
def controls():
    running=True
    while running:

        window.fill("white")
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        OPTIONS_TEXT = font(25).render("This is the Controls screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(500, 50))
        Movement = font(25).render("Use the arrow keys to move and up arrow or space bar to jump", True, "Black")
        jumping = font(25).render("You can Double Jump by pressing Jump", True, "Black")
        wallJump = font(25).render("You can wall jump by jumping into a wall and pressing jump (must be on first jump)", True, "Black")
        paus = font(25).render("Press escape to pause", True, "Black")
        Movement_RECT = Movement.get_rect(center=(500, 260))
        jumping_RECT = jumping.get_rect(center=(500, 360))
        wallJump_RECT = wallJump.get_rect(center=(500, 460))
        paus_RECT = paus.get_rect(center=(500, 560))

        window.blit(OPTIONS_TEXT, OPTIONS_RECT)
        window.blit(Movement, Movement_RECT)
        window.blit(jumping, jumping_RECT)
        window.blit(wallJump, wallJump_RECT)
        window.blit(paus, paus_RECT)

        OPTIONS_BACK = Button(image=None, pos=(500, 700), 
                            text_input="BACK", font=font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    running = False
                    
                    

        pygame.display.update()   
    
def pause(window):
    BG = pygame.image.load("assets/Menu/Background.png")
    running = True
    while running:
        
    
        window.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(500, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("assets/Menu/PlayRect.png"), pos=(500, 250), 
                            text_input="PLAY", font=font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("assets/Menu/OptionsRect.png"), pos=(500, 400), 
                            text_input="OPTIONS", font=font(75), base_color="#d7fcd4", hovering_color="White")
        CONTROLS_BUTTON = Button(image=pygame.image.load("assets/Menu/OptionsRect.png"), pos=(500, 550), 
                            text_input="CONTROLS", font=font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Menu/QuitRect.png"), pos=(500, 700), 
                            text_input="QUIT", font=font(75), base_color="#d7fcd4", hovering_color="White")

        window.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, CONTROLS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(window)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    running = False
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if CONTROLS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    controls()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

async def main():

    pause(window)
    global jumpHeight, objects, finishedLevel, run, levelNum
    jumpHeight = -7
    finishedLevel = False
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")
    level = ['tutorialOne.csv','tutorialTwo.csv', 'tutorialThree.csv','levelOne.csv', 'levelTwo.csv']
    levelNum = 0
    block_size = 96
    objects = loadLevel(level, block_size, levelNum)
    player = Player(100, 610, 50, 50)
   
    
    offset_x = 0
    scroll_area_width = 700
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2 or event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()
                if event.key == pygame.K_ESCAPE:    
                    pause(window)               
        player.loop(FPS)

        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)
        
        if player.rect.y > 800:
            player.death()
            player.rect.y = 610
            player.y_vel = 0
            player.rect.x = 100
            offset_x = 30

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
        
        if finishedLevel:
            levelNum += 1
            if levelNum == len(level):
                Black = (0, 0, 0)
                pygame.draw.rect(window, Black, (0, 0, 1000, 800))
                font = pygame.font.Font('freesansbold.ttf', 32)
        
                text = font.render(f'well done you won the game', True, (255, 255, 255))
                textRect = text.get_rect()
                textRect.center = (WIDTH // 2, HEIGHT // 2)
                window.blit(text, textRect)
                pygame.display.update()
                run = False
            else:
                Black = (0, 0, 0)
                pygame.draw.rect(window, Black, (0, 0, 1000, 800))
                font = pygame.font.Font('freesansbold.ttf', 32)
        
                text = font.render(f'loading...', True, (255, 255, 255))
                textRect = text.get_rect()
                textRect.center = (WIDTH // 2, HEIGHT // 2)
                window.blit(text, textRect)
                pygame.display.update()
                

                objects = loadLevel(level, block_size, levelNum)

                finishedLevel = False
                player.rect.y = 610
                player.y_vel = 0
                player.rect.x = 100
                offset_x = 0
    
        
        await asyncio.sleep(0)
        
    
    

      
asyncio.run(main())