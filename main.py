import pygame as pg
import sys 
import random
from constantes import *
from clases import Jugador, Bala, Enemy, NaveNodriza, BOSS, Pieza

pg.init()
pg.mixer.init()
pg.font.init()

titulo = pg.font.Font(font, 40)
oleada = pg.font.Font(font, 16)
instrucc = pg.font.Font(font, 13)

ms_player = pg.mixer.Sound("sounds/laser1.mp3")
ms_nave = pg.mixer.Sound("sounds/laser2.mp3")
ms_boss = pg.mixer.Sound("sounds/laser3.mp3")
ms_gameover = pg.mixer.Sound("sounds/gameover.mp3")
ms_choque = pg.mixer.Sound("sounds/crash.mp3")
ms_pieza = pg.mixer.Sound("sounds/pieza.mp3")
ms_alerta = pg.mixer.Sound("sounds/warning.mp3")
ms_win = pg.mixer.Sound("sounds/win.mp3")

ms_player.set_volume(vol_player)
ms_nave.set_volume(vol_nave)
ms_choque.set_volume(vol_choque)
ms_alerta.set_volume(vol_alerta)
ms_boss.set_volume(vol_boss)
ms_pieza.set_volume(vol_pieza)
ms_gameover.set_volume(vol_gameover)
ms_win.set_volume(vol_win)

pg.mixer.music.load("sounds/background.mp3")
pg.mixer.music.set_volume(0.2)
pg.mixer.music.play(-1)

window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Defensor de la Base - Modo Oleadas")
reloj = pg.time.Clock()

# Grupos de Sprites
allsprites = pg.sprite.Group()
bulletgroup = pg.sprite.Group()
enemygroup = pg.sprite.Group() 
bossgroup = pg.sprite.Group() 
piezagroup = pg.sprite.Group()
bossbulletgroup = pg.sprite.Group()

# Creación de entidades 
nodriza = NaveNodriza(allsprites, bulletgroup, ms_nave)
player = Jugador()
allsprites.add(nodriza, player)
# VARIABLES DEL SISTEMA DE OLEADAS 
oleada_actual = 1
enemigos_por_oleada = [20, 30, 50, 1] 
enemigos_creados = 0  

temporizador_spawn = 0
cadencia_spawn = 45 

background = pg.image.load("images/background.jpg").convert()
FONDO = pg.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

youwin = pg.image.load("images/win.jpg").convert()
imgwin = pg.transform.scale(youwin, (WINDOW_WIDTH, WINDOW_HEIGHT))

youover = pg.image.load("images/gameover.jpg").convert()
gameover = pg.transform.scale(youover, (WINDOW_WIDTH, WINDOW_HEIGHT))

fondo_y1 = 0
fondo_y2 = -WINDOW_HEIGHT 
velocidad_fondo = 3

def menu():
    vari = True
    while vari:
        reloj.tick(FPS)
        window.blit(FONDO, (0,0))
        text_titulo = titulo.render("¡Defiende la Base!", True, AMARILLO)
        text_sub1 = oleada.render("Sobrevive a las 3 oleadas", True, BLANCO)
        text_sub2 = oleada.render("y al jefe final", True, BLANCO)
        text_jugar = instrucc.render("Presione ESPACIO para comenzar", True, VERDE)
        text_vidas = oleada.render(f"Vidas: {player.heart}", True, BLANCO)

        window.blit(text_titulo, (WINDOW_WIDTH // 2 - text_titulo.get_width() // 2, 180))
        window.blit(text_sub1, (WINDOW_WIDTH // 2 - text_sub1.get_width() // 2, 270))
        window.blit(text_sub2, (WINDOW_WIDTH // 2 - text_sub2.get_width() // 2, 310))
        window.blit(text_jugar, (WINDOW_WIDTH // 2 - text_jugar.get_width() // 2, 450))
        window.blit(text_vidas, (WINDOW_WIDTH - text_vidas.get_width() - 20, 15))
        
        pg.display.flip()
        
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif evento.type == pg.KEYDOWN:
                if evento.key == pg.K_SPACE:
                    vari = False

def final(img_final, victory):
    varb = True
    while varb:
        reloj.tick(FPS)
        window.blit(img_final, (0, 0))
        
        if victory:
            text_reinicio = instrucc.render("¡Victoria! Presione 'R' para jugar de nuevo o 'ESC' para salir", True, VERDE)
        else:
            text_reinicio = instrucc.render("Presione 'R' para volver a jugar o 'ESC' para salir", True, AMARILLO)
            
        pos_x = WINDOW_WIDTH // 2 - text_reinicio.get_width() // 2
        pos_y = 520 
        window.blit(text_reinicio, (pos_x, pos_y))

        pg.display.flip()

        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif evento.type == pg.KEYDOWN:
                if evento.key == pg.K_r: 
                    return True
                elif evento.key == pg.K_ESCAPE: 
                    return False


#BUCLE GENERAL DEL JUEGO

juego_activo = True
primer_inicio = True 

while juego_activo:
    if primer_inicio:
        menu()  
        primer_inicio = False
    
    for grupo in [allsprites, bulletgroup, enemygroup, bossgroup, piezagroup, bossbulletgroup]:
        grupo.empty()
    
    nodriza = NaveNodriza(allsprites, bulletgroup, ms_nave)
    player = Jugador()
    allsprites.add(nodriza, player)
    
    piezas_recolectadas = 0
    oleada_actual = 1
    enemigos_creados = 0  
    temporizador_spawn = 0
    win = False
    run = True # ACTIVACIÓN DEL COMBATE EN CADA VUELTA

    pg.mixer.music.load("sounds/background.mp3")
    pg.mixer.music.set_volume(0.2)
    pg.mixer.music.play(-1)

    while run:
        reloj.tick(FPS)
        
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                run = False
                juego_activo = False
            elif evento.type == pg.KEYDOWN and evento.key == pg.K_SPACE:
                if player.cooldown_balas == 0:
                    bala = Bala(player.rect.centerx, player.rect.top)
                    allsprites.add(bala)
                    bulletgroup.add(bala)
                    ms_player.play()
                    player.cooldown_balas = player.cadencia_disparo

        enemigos_en_pantalla = len(enemygroup) + len(bossgroup)

        if oleada_actual <= 3:
            if enemigos_en_pantalla == 0 and enemigos_creados >= enemigos_por_oleada[oleada_actual - 1]:
                oleada_actual += 1
                enemigos_creados = 0  
                print(f"¡INICIANDO OLEADA {oleada_actual}!")
            
            elif enemigos_creados < enemigos_por_oleada[oleada_actual - 1]:
                temporizador_spawn += 1
                if temporizador_spawn >= cadencia_spawn:
                    enemigo = Enemy(random.randint(0, WINDOW_WIDTH - 40), -40)
                    allsprites.add(enemigo)
                    enemygroup.add(enemigo)
                    enemigos_creados += 1
                    
                    if piezas_recolectadas < 10 and random.random() < 0.3:
                        new_pieza = Pieza(random.randint(0, WINDOW_WIDTH - 20), -20)
                        allsprites.add(new_pieza)
                        piezagroup.add(new_pieza)
                    temporizador_spawn = 0

        elif oleada_actual == 4:
            if enemigos_creados == 0:
                jefe_entidad = BOSS(ms_boss)
                allsprites.add(jefe_entidad)
                bossgroup.add(jefe_entidad)
                enemigos_creados = 1
                ms_alerta.play()
                print("ALERTA: El Jefe ha entrado al campo de batalla")
            
            elif enemigos_en_pantalla == 0:
                pg.mixer.music.stop() 
                win = True
                run = False

        allsprites.update()
        for jefe in bossgroup:
            jefe.actualizar_jefe(allsprites, bossbulletgroup)
        
        # COLISIONES
        for bala in bulletgroup:
            if pg.sprite.spritecollide(bala, enemygroup, True):
                bala.kill()
                ms_choque.play()
                
            for j in pg.sprite.spritecollide(bala, bossgroup, False):
                bala.kill()
                j.vida_actual -= 1
                print(f"Vida del Jefe: {j.vida_actual}")
                if j.vida_actual <= 0:
                    j.kill()

        if pg.sprite.spritecollide(player, enemygroup, True):
            player.heart -= 1
            nodriza.recibir_danio(10)
            ms_choque.play()
            player.reaparecer()
            
        if pg.sprite.spritecollide(nodriza, enemygroup, True, pg.sprite.collide_mask):
            nodriza.recibir_danio(20)
            ms_choque.play()
            
        if pg.sprite.spritecollide(player, bossbulletgroup, True):
            ms_choque.play()
            player.heart -= 1 
            player.reaparecer()
            print(f"¡IMPACTO CRÍTICO! Vidas restantes: {player.heart}")

        if pg.sprite.spritecollide(player, bossgroup, False) or pg.sprite.spritecollide(nodriza, bossgroup, False, pg.sprite.collide_mask):
            nodriza.vida_actual = 0
                     
        for pieza in pg.sprite.spritecollide(player, piezagroup, True):
            if not nodriza.desbloqueada:
                piezas_recolectadas += 1
                ms_pieza.play()
                print(f"Piezas: {piezas_recolectadas}/10")
                if piezas_recolectadas >= 10: 
                    nodriza.desbloqueada = True 
                    nodriza.disparar_defensas()  
                    print("¡SISTEMA DEFENSIVO DESBLOQUEADO PERMANENTEMENTE!")
                    piezagroup.empty()

        if nodriza.vida_actual <= 0 or player.heart <= 0:
            pg.mixer.music.stop() 
            run = False

        # Actualización de fondo
        fondo_y1 += velocidad_fondo
        fondo_y2 += velocidad_fondo
        if fondo_y1 >= WINDOW_HEIGHT: fondo_y1 = -WINDOW_HEIGHT
        if fondo_y2 >= WINDOW_HEIGHT: fondo_y2 = -WINDOW_HEIGHT

        window.blit(FONDO, (0, fondo_y1))
        window.blit(FONDO, (0, fondo_y2)) 
        allsprites.draw(window)
        
        # HUD 
        pg.draw.rect(window, ROJO, (10, 10, 200, 20))
        pg.draw.rect(window, VERDE, (10, 10, 200 * (nodriza.vida_actual / nodriza.vida_max), 20))

        text_pantalla_vidas = oleada.render(f"Vidas: {player.heart}", True, BLANCO)
        window.blit(text_pantalla_vidas, (WINDOW_WIDTH - text_pantalla_vidas.get_width() - 20, 15))

        text_piezas = oleada.render(f"Piezas: {piezas_recolectadas}/10", True, AMARILLO)
        window.blit(text_piezas, (WINDOW_WIDTH - text_piezas.get_width() - 20, 40))
        
        if oleada_actual == 4 and len(bossgroup) > 0:
            jefe_actual = bossgroup.sprites()[0]
            pg.draw.rect(window, ROJO, (WINDOW_WIDTH // 2 - 150, 10, 300, 15))
            pg.draw.rect(window, MAGENTA, (WINDOW_WIDTH // 2 - 150, 10, 300 * (jefe_actual.vida_actual / jefe_actual.vida_max), 15))
        
        pg.display.flip()

    # 4. CAPTURA DE DECISIÓN 
    if juego_activo:
        pg.mixer.music.stop() 
        
        if win:
            print("¡FELICIDADES! Salvaste la Base Aérea y destruiste al Jefe.")
            ms_win.set_volume(0.8)
            ms_win.play()
            reinicio = final(imgwin, True)
        else:
            print("GAME OVER - La base fue destruida...")
            ms_gameover.set_volume(0.8)
            ms_gameover.play()
            reinicio = final(gameover, False)

        # Si el jugador presiona ESC
        if not reinicio:
            juego_activo = False


pg.quit()
sys.exit()