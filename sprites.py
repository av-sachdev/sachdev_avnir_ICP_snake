import pygame as pg
from pygame.sprite import Sprite
from settings import *
from utils import *
from os import path
from random import randint
from math import *

vec = pg.math.Vector2

# create player class with Sprite as super Class

def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


def collide_with_walls(sprite, group, dir):
    # check for x collision
    if dir == 'x':
        # checking to see if we've collided with hitrects
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # this line checks to see if we're to the left of the wall
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                # reposition the player (sprite) to the left side of the wall
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2 
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        # checking to see if we've collided with hitrects
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # this line checks to see if we're above the wall
            if hits[0].rect.centery > sprite.hit_rect.centery:
                # reposition the player (sprite) to the top of the wall
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2 
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)
        # self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        #player motion attributes
        self.rect.x = x
        self.rect.y = y
        # self.vx, self.vy = 0,0
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        # self.x = x * TILESIZE
        # self.y = y * TILESIZE
        self.hit_rect = PLAYER_HIT_RECT
        # animation stuff
        self.current_frame = 0
        self.last_update = 0
        # acccounting for player states
        self.jumping = False
        self.moving = False
        self.cofric = PLAYER_FRIC
        print("player instance created")
        self.load_images()
        self.coins = 0

    # gets player input
    def get_keys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_d]:
            self.acc.x = PLAYER_ACC
        if keys[pg.K_w]:
            self.acc.y = -PLAYER_ACC
        if keys[pg.K_s]:
            self.acc.y = PLAYER_ACC
        if keys[pg.K_f]:
            self.pew()
           
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel*=0.7071
    def pew(self):
        mpos = pg.mouse.get_pos()
        print(mpos)
        targetx = mpos[0]
        targety = mpos[1]
        dx = targetx = self.hit_rect.x
        dy = targety = self.hit_rect.y
        angle = atan2(dx,dy)
        speed_x = 10*sin(angle)
        speed_y = 10*cos(angle)
        PewPew(self.game, self.rect.centerx, self.rect.centery, TILESIZE/4, TILESIZE/4, speed_x, speed_y)
    def jump(self):
        pass
    def load_images(self):
        self.idle_frames = [self.spritesheet.get_image(0,0, TILESIZE,TILESIZE), self.spritesheet.get_image(32,0, TILESIZE,TILESIZE)]
    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.moving:
            # this determines when to display the next frame
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                bottom = self.rect.bottom
                self.image = self.idle_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        elif self.moving:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.moving_frames)
                bottom = self.rect.bottom
                self.image = self.moving_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
            
    def  update(self):
        self.acc = vec(0,0)
        self.get_keys()
        self.animate()
       
        self.acc.x += self.vel.x * self.cofric
        self.vel.x += self.acc.x * self.game.dt
        self.vel.y += self.acc.y * self.game.dt
       
        max_fall_speed = TILESIZE / max(self.game.dt, 0.001)
        self.vel.y = min(self.vel.y, max_fall_speed)
       
        if abs(self.vel.x) < 0.1:
              self.vel.x = 0
        if abs(self.vel.y) < 0.1:
              self.vel.y = 0
       
        # self.pos += self.vel * self.game.dt + 0.5 * self.acc * (self.game.dt ** 2)
        floor_hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
       
        if floor_hits:
            self.jumping = False
        elif floor_hits != True:
            self.jumping = True
       
        self.rect.center = self.pos
       
        # self.pos += self.vel * self.game.dt
       
        self.pos += self.vel + 0.5 * self.acc
       
        if self.vel.y == 0:
            self.jumping = False
           
        hits = pg.sprite.spritecollide(self, self.game.all_coins, True)
        if hits:
            self.coins += 1
            self.game.score += 1
            self.game.collect_snd.play()
            # print(f"I have {self.coins} coins")
            for i in range(20):
                Particle(self.game, hits[0].rect.x, hits[0].rect.y)
                hits[0].kill()
            print(str(len(self.game.all_particles)))
 
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')
        self.rect.center = self.hit_rect.center

        # self.animate()
        # self.acc = vec(0,0)
        # self.get_keys()
        # self.acc.x = self.vel.x*self.cofric
        # self.acc.y = self.vel.y*self.cofric
        # self.vel+=self.acc
        # self.pos+=self.vel + 0.5*self.acc
        # if abs(self.vel.x) < 0.1:
        #     self.vel.x = 0
        # if abs(self.vel.y) < 0.1:
        #     self.vel.y = 0

        # self.rect.center = self.pos
        # self.pos+=self.vel + 0.5*self.acc
        # self.pos += self.vel * self.game.dt
        # tile_hits = pg.sprite.spritecollide(self, self.game.all_tiles, False)
        # if tile_hits:
        #     if tile_hits[0].variant == 'ice':
        #         self.cofric = 0.001
        #     else:
        #         self.cofric = -0.1
        #         self.acc = vec(0,0)

        # hits = pg.sprite.spritecollide(self, self.game.all_coins, True)
        # if hits:
        #     self.coins+=1
        #     self.game.score+=1
        #     print("I collected",str(self.coins),"a coin!!!")
        #     Particle(self.game, hits[0].rect.x, hits[0].rect.y)
        #     hits[0].kill()
        #     print(str(len(self.game.all_particles)))


        # self.hit_rect.centerx = self.pos.x
        # collide_with_walls(self, self.game.all_walls, 'x')
        # self.hit_rect.centery = self.pos.y
        # collide_with_walls(self, self.game.all_walls, 'y')
        # self.rect.center = self.hit_rect.center

class PewPew(Sprite):
    def __init__(self, game, x, y, w, h, sx, sy):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((w,h))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = TILESIZE/8
        pg.draw.circle(self.image, YELLOW, self.rect.center, self.radius)
        self.rect.x = x
        self.rect.y = y
        self.speed_x = sx
        self.speed_y = sy
        self.fired = False
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
       
        if self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()
    




class Mob(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png"))
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image = self.spritesheet.get_image(0,0,TILESIZE, TILESIZE)
        self.image.set_colorkey(BLACK)
        # self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        # self.vx, self.vy = 0,0
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        # self.x = x * TILESIZE
        # self.y = y * TILESIZE
        self.hit_rect = PLAYER_HIT_RECT
        # animation stuff
        self.current_frame = 0
        self.last_update = 0
        # acccounting for player states
        self.jumping = False
        self.moving = False
        print("mob instance created")
        self.load_images()
        # print(self.rect.x, self.rect.y)
    # gets player input
    def jump(self):
        pass
    def load_images(self):
        self.idle_frames = [self.spritesheet.get_image(0,0, TILESIZE,TILESIZE), self.spritesheet.get_image(32,0, TILESIZE,TILESIZE)]
    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.moving:
            # this determines when to display the next frame
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
                bottom = self.rect.bottom
                self.image = self.idle_frames[self.current_frame]
                # self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        elif self.moving:
            if now - self.last_update > 350:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.moving_frames)
                bottom = self.rect.bottom
                self.image = self.moving_frames[self.current_frame]
                # self.rect = self.image.get_rect()
                self.rect.bottom = bottom
            
    def update(self):
        self.animate()

class Particle(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_particles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE/4, TILESIZE/4))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.vel = vec(randint(-180,180),randint(-180,180))
        self.pos = vec(x,y)
        self.rect.center = self.pos
        self.speed = 5
        self.countdown = Cooldown()
        self.countdown.event_time = floor(pg.time.get_ticks()/1000)
        print("I created a particle!")
        print(self.rect.x)
        print(self.rect.y)
   
    def update(self):
        self.countdown.ticking()
        self.pos += self.vel * self.speed * self.game.dt
        if self.countdown.delta > 1:
            self.kill()
            print(str(len(self.game.all_particles)))
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        

class Wall(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx, self.vy = 0,0
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y
        print("wall instance created")


class FloorTile(Sprite):
    def __init__(self, game, x, y, color):
        self.groups = game.all_sprites, game.all_tiles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vx, self.vy = 0,0
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.rect.x = self.x
        self.rect.y = self.y
        print("wall instance created")


class Coin(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        pg.draw.circle(self.image, (GOLD), (TILESIZE/2, TILESIZE/2), TILESIZE/2)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE
        self.rect.center = self.pos

    # new object type Wall that is green