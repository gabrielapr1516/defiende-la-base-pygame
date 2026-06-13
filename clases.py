import pygame as pg
import random 
from constantes import *

class GameObject(pg.sprite.Sprite):
    def __init__(self, imagen, width, height, pos_x, pos_y):
        pg.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height
        self.image = pg.transform.scale(pg.image.load(imagen), (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

        self.mask = pg.mask.from_surface(self.image)

class Jugador(GameObject): 
    def __init__(self):
        GameObject.__init__(self, img_player, 60, 50, WINDOW_WIDTH // 2 - 25, WINDOW_HEIGHT - 90)
        self.velocidad = 7
        self.heart = 3
        self.cadencia_disparo = 10
        self.cooldown_balas = 0
    
    def reaparecer(self):
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT - 20

    def update(self):
        if self.cooldown_balas > 0:
            self.cooldown_balas -= 1

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rect.x -= self.velocidad
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rect.x += self.velocidad
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.rect.y -= self.velocidad
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.rect.y += self.velocidad

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH

class Bala(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self, img_bullet1, 10, 20, x, y)
        self.velocidad = -10

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.bottom < 0:
            self.kill()

class Enemy(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self, img_enemy, 40, 40, x, y)
        self.vx = random.choice([-2, 2])
        self.velocidad = 2

    def update(self):
        self.rect.y += self.velocidad
        self.rect.x += self.vx
        if self.rect.left <= 0:
            self.rect.left = 0 
            self.vx *= -1      
        elif self.rect.right >= WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH 
            self.vx *= -1
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class BulletNaveNodriza(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self, img_bullet2, 10, 30, x, y)
        self.velocidad = -5

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.bottom < 0:
            self.kill()

class NaveNodriza(GameObject):
    def __init__(self, allsprites, bulletgroup, ms_nave):
        GameObject.__init__(self,img_nodriza, WINDOW_WIDTH, 450, 0, 400 - 40)

        self.vida_max = 100
        self.vida_actual = 100
        self.allsprites = allsprites
        self.bulletgroup = bulletgroup
        self.desbloqueada = False 
        self.cadencia_disparo =  120
        self.temporizador = self.cadencia_disparo
        self.ms_nave = ms_nave

    def recibir_danio(self, cantidad):
        self.vida_actual -= cantidad
        if self.vida_actual < 0:
            self.vida_actual = 0

    def update(self):
        if self.desbloqueada:
            if self.temporizador > 0:
                self.temporizador -= 1
            else:
                self.disparar_defensas()
                self.temporizador = self.cadencia_disparo

    def disparar_defensas(self, ms_nave = None):
        b_1 = BulletNaveNodriza(120, 510)
        b_2 = BulletNaveNodriza(295, 510)
        b_3 = BulletNaveNodriza(497, 510)
        b_4 = BulletNaveNodriza(670, 515)
        self.allsprites.add(b_1, b_2, b_3, b_4)
        self.bulletgroup.add(b_1, b_2, b_3, b_4)
        self.ms_nave.play()

class BOSS(GameObject):
    def __init__(self, ms_boss):
        GameObject.__init__(self, img_boss, 300, 120, WINDOW_WIDTH // 2 - 150, -150)
        self.vida_max = 50
        self.vida_actual = self.vida_max
        self.velocidad_x = 4
        self.velocidad_y = 1
        self.cadencia_disparo = 30 
        self.temporizador = self.cadencia_disparo
        self.ms_boss = ms_boss
    
    def actualizar_jefe(self, allsprites, boss_bullet_group):
        if self.rect.y < 60:
            self.rect.y += self.velocidad_y
        else:
            self.rect.x += self.velocidad_x
            
            if self.temporizador > 0:
                self.temporizador -= 1
            else:
                self.disparar_proyectil(allsprites, boss_bullet_group)
                self.ms_boss.play()
                self.temporizador = self.cadencia_disparo

            if self.rect.left <= 0:
                self.rect.left = 0
                self.velocidad_x *= -1
            elif self.rect.right >= WINDOW_WIDTH:
                self.rect.right = WINDOW_WIDTH
                self.velocidad_x *= -1

    def disparar_proyectil(self, allsprites, boss_bullet_group):
        bullet_j = BalaJefe(self.rect.centerx - 6, self.rect.bottom)
        allsprites.add(bullet_j)
        boss_bullet_group.add(bullet_j)

class Pieza(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self, img_pieza, 50, 50, x, y)
        self.velocidad = 2
    
    def update(self):
        self.rect.y += self.velocidad
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class BalaJefe(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self, img_bulletboss, 25, 40, x, y)
        self.velocidad = 7

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()