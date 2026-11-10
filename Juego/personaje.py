import pygame

from constantes import ASSETS_PATH, SCREEN_HEIGHT, SCREEN_WIDTH


class Personaje:
    def __init__(self, x, y):
        ruta = ASSETS_PATH / "images" / "Speeder.png"
        self.image = pygame.image.load(str(ruta)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (95, 95))
        self.shape = self.image.get_rect(center=(x, y))
        self.lasers = []
        self.energia = 100
        self.intervalo_disparo = 250
        self.ultimo_disparo = -self.intervalo_disparo

    def mover(self, dx, dy):
        self.shape.x += dx
        self.shape.y += dy
        self.shape.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def lanzar_laser(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_disparo < self.intervalo_disparo:
            return False

        self.lasers.append(Laser(self.shape.centerx, self.shape.top))
        self.ultimo_disparo = ahora
        return True

    def actualizar_lasers(self):
        for laser in self.lasers[:]:
            laser.mover()
            if laser.rect.bottom < 0:
                self.lasers.remove(laser)

    def recibir_dano(self):
        self.energia = max(0, self.energia - 10)
        return self.energia > 0

    def dibujar(self, screen):
        screen.blit(self.image, self.shape)
        for laser in self.lasers:
            laser.dibujar(screen)

        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 100, 12))
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, self.energia, 12))


class Enemigo:
    def __init__(self, x, y):
        ruta = ASSETS_PATH / "images" / "enemigo1.png"
        self.image = pygame.image.load(str(ruta)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.image.get_rect(topleft=(x, y))

    def mover(self):
        self.rect.y += 5

    def dibujar(self, screen):
        screen.blit(self.image, self.rect)


class Laser:
    def __init__(self, x, y):
        ruta = ASSETS_PATH / "images" / "lase1.png"
        self.image = pygame.image.load(str(ruta)).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self):
        self.rect.y -= 10

    def dibujar(self, screen):
        screen.blit(self.image, self.rect)
