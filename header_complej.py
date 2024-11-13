import pygame

# Inicializar Pygame
pygame.init()

# Configuración del Header
HEADER_HEIGHT = 80  # Altura del header
HEADER_COLOR = (30, 30, 30, 137)  # Color #1E1E1E con 54% de transparencia
WHITE = (255, 255, 255)

# Fuente para el header
header_font = pygame.font.SysFont("Helvetica", 24)

# Cargar la imagen del logo y escalarla a un cuarto menos
logo_image = pygame.image.load("img/logoupcc.png")  # Asegúrate de que esta ruta sea correcta
logo_image = pygame.transform.scale(logo_image, (logo_image.get_width() // 2.5, logo_image.get_height() // 2.5))

# Función para dibujar el header
def draw_header(surface, screen_width):
    # Crear superficie para el header
    header_surface = pygame.Surface((screen_width, HEADER_HEIGHT), pygame.SRCALPHA)
    header_surface.fill(HEADER_COLOR)
    
    # Posicionar y dibujar el logo en el header
    logo_position = (40, (HEADER_HEIGHT - logo_image.get_height()) // 2)  # Mover el logo un poco más a la derecha
    header_surface.blit(logo_image, logo_position)
    
    # Texto en el header
    header_text = "Complejidad Algoritmica 2024-2"
    text_surface = header_font.render(header_text, True, WHITE)
    text_rect = text_surface.get_rect(center=(screen_width // 2, HEADER_HEIGHT // 2))
    header_surface.blit(text_surface, text_rect)
    
    # Dibujar el header en la pantalla principal
    surface.blit(header_surface, (0, 0))