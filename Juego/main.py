import ctypes
import random
import sys
from pathlib import Path

import pygame


# pygame-ce 2.5.8 puede necesitar que estos codecs se precarguen en Windows.
_DLL_HANDLES = []
if sys.platform == "win32":
    _PYGAME_DLL_DIR = Path(pygame.__file__).parent
    for _dll_name in ("libpng16-16.dll", "libjpeg-62.dll"):
        _DLL_HANDLES.append(ctypes.WinDLL(str(_PYGAME_DLL_DIR / _dll_name)))


from constantes import ASSETS_PATH, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from explosiones import Explosion
from personaje import Enemigo, Personaje


def cargar_imagen(*partes, alpha=False):
    ruta = ASSETS_PATH.joinpath(*partes)
    imagen = pygame.image.load(str(ruta))
    return imagen.convert_alpha() if alpha else imagen.convert()


def mostrar_imagen_inicial(screen, imagen_path, duracion):
    imagen = pygame.image.load(str(imagen_path)).convert()
    imagen = pygame.transform.scale(imagen, (SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    tiempo_inicial = pygame.time.get_ticks()

    while pygame.time.get_ticks() - tiempo_inicial < duracion:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        tiempo_transcurrido = pygame.time.get_ticks() - tiempo_inicial
        alpha = max(0, 255 - int(255 * tiempo_transcurrido / duracion))
        imagen.set_alpha(alpha)

        screen.fill((0, 0, 0))
        screen.blit(imagen, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)

    return True


def mostrar_game_over(screen):
    pygame.mixer.music.stop()
    screen.fill((0, 0, 0))

    font_large = pygame.font.Font(None, 74)
    font_small = pygame.font.Font(None, 36)
    texto_game_over = font_large.render("GAME OVER", True, (255, 0, 0))
    texto_mensaje = font_small.render(
        "Que la Fuerza te acompane", True, (255, 255, 255)
    )

    rect_game_over = texto_game_over.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30)
    )
    rect_mensaje = texto_mensaje.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45)
    )
    screen.blit(texto_game_over, rect_game_over)
    screen.blit(texto_mensaje, rect_mensaje)
    pygame.display.flip()
    pygame.time.wait(2000)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Amenaza Fantasma")

    imagen_inicial = ASSETS_PATH / "images" / "inicio" / "Star.png"
    if not mostrar_imagen_inicial(screen, imagen_inicial, 5000):
        pygame.quit()
        return

    icono = cargar_imagen("images", "001.jfif")
    pygame.display.set_icon(icono)

    fondo2 = pygame.transform.scale(
        cargar_imagen("images", "fondo2.jfif"),
        (SCREEN_WIDTH, SCREEN_HEIGHT),
    )
    fondo3 = pygame.transform.scale(
        cargar_imagen("images", "fondo3.jpg"),
        (SCREEN_WIDTH, SCREEN_HEIGHT),
    )
    fondos = (fondo2, fondo3)

    sonido_laser = pygame.mixer.Sound(
        str(ASSETS_PATH / "sounds" / "laserdis.mp3")
    )
    sonido_explosion = pygame.mixer.Sound(
        str(ASSETS_PATH / "sounds" / "explosion.mp3")
    )
    pygame.mixer.music.load(str(ASSETS_PATH / "sounds" / "efectos.mp3"))
    pygame.mixer.music.play(-1)

    personaje = Personaje(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 140)
    enemigos = []
    explosiones = []
    puntos = 0
    nivel = 1

    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 5
        personaje.mover(dx, dy)

        if keys[pygame.K_SPACE] and personaje.lanzar_laser():
            sonido_laser.play()

        personaje.actualizar_lasers()

        for enemigo in enemigos[:]:
            enemigo.mover()
            if enemigo.rect.top > SCREEN_HEIGHT:
                enemigos.remove(enemigo)
                continue

            laser_impacto = next(
                (
                    laser
                    for laser in personaje.lasers
                    if enemigo.rect.colliderect(laser.rect)
                ),
                None,
            )
            if laser_impacto is not None:
                explosiones.append(Explosion(*enemigo.rect.center))
                enemigos.remove(enemigo)
                personaje.lasers.remove(laser_impacto)
                sonido_explosion.play()
                puntos += 10
                continue

            if enemigo.rect.colliderect(personaje.shape):
                explosiones.append(Explosion(*enemigo.rect.center))
                enemigos.remove(enemigo)
                if not personaje.recibir_dano():
                    running = False
                    break

        if random.random() < 0.02:
            x = random.randint(0, SCREEN_WIDTH - 80)
            enemigos.append(Enemigo(x, -80))

        explosiones = [
            explosion for explosion in explosiones if explosion.actualizar()
        ]

        nivel = puntos // 250 + 1
        fondo_actual = fondos[(nivel - 1) % len(fondos)]

        screen.blit(fondo_actual, (0, 0))
        personaje.dibujar(screen)
        for enemigo in enemigos:
            enemigo.dibujar(screen)
        for explosion in explosiones:
            explosion.dibujar(screen)

        texto_puntos = font.render(f"Puntos: {puntos}", True, (255, 255, 255))
        texto_nivel = font.render(f"Nivel: {nivel}", True, (255, 255, 255))
        screen.blit(texto_puntos, (10, 40))
        screen.blit(texto_nivel, (10, 80))

        pygame.display.flip()
        clock.tick(FPS)

    mostrar_game_over(screen)
    pygame.quit()


if __name__ == "__main__":
    main()
