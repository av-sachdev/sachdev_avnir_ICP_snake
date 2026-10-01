# This file was created by: Avnir Sachdev
# Content inspired by Chris Bradfield
# I do solemnly swear to create concise and informative comments

'''The game engine consists of three (four) basic components:
Input - keys, buttons, voice, mouse, touch, breath, movement, control stick
Process - input process (direction of control, magnitude)
Output - draw new frames pixel, sound, haptics, 
(Store)
'''

import pygame as pg
from os import path
from settings import *
from sprites import *
from utils import *


# the game class is a blueprint for the whole game
class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH,HEIGHT))
        print('game class initialized')
        self.clock = pg.time.Clock()
        self.running = True
        self.playing = True

    def load_data(self, map):
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir,'images')
        self.snd_dir = path.join(self.game_dir,'sounds')
        self.map = Map(path.join(self.game_dir,map))

    def new(self):
        self.load_data('level1.txt')
        print(self.map.data)
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()


        # self.wall = Wall(self,100,100)
        # self.wall = Wall(self,200,200)
        # self.wall = Wall(self,300,300)
        # self.wall = Wall(self,400,400)
        print(self.map.data)
        for row,tiles in enumerate(self.map.data):
            for col,tile in enumerate(tiles):
                if tile == '1':
                    Wall(self,col,row)
        for row,tiles in enumerate(self.map.data):
            for col,tile in enumerate(tiles):
                if tile == 'P':
                    Player(self,col,row)



    def run(self):
        while self.running:
            # sets the delta time property and runs the tick function at FPS/1000
            self.dt = self.clock.tick(FPS) /1000
            self.events() # this gets player input
            self.update() # this updates the game
            self.draw() # this draws sprites
    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
    def update(self):
        self.all_sprites.update()
    def draw(self):
        self.screen.fill(BLUE)
        self.all_sprites.draw(self.screen)
        # 
        pg.display.flip()


if __name__ == "__main__":
    g = Game()


while g.running:
    g.new()
    g.run()

pg.quit()