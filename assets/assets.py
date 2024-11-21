import pygame

def load_assets(screen_width, screen_height):
    assets = {}
    # Cargar imágenes
    assets['background_image'] = pygame.image.load("img/fondoaurora.jpg")
    assets['background_image'] = pygame.transform.scale(assets['background_image'], (screen_width, screen_height))

    assets['logo_image'] = pygame.image.load("img/logopower.png")
    assets['logo_image'] = pygame.transform.scale(assets['logo_image'], (400, 400))

    # Crear una superficie para el logo
    assets['logo_surface'] = pygame.Surface((400, 400), pygame.SRCALPHA)
    assets['logo_surface'].blit(assets['logo_image'], (0, 0))

    # Cargar sonidos
    assets['hover_sound'] = pygame.mixer.Sound("music/tocksound.mp3")

    # Cargar y reproducir música
    pygame.mixer.music.load("music/Mazurka No. 11 in E Minor, Op. 17 No. 2.mp3")
    pygame.mixer.music.play(-1)  # Reproducir en bucle

    return assets