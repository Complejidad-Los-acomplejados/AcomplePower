import pygame
from config.config import *

# Configuración del Header
HEADER_HEIGHT = 80  # Altura del header
HEADER_COLOR = (30, 30, 30, 137)  # Color #1E1E1E con 54% de transparencia
WHITE = (255, 255, 255)

# Cargar la imagen del logo y escalarla a un cuarto menos
logo_image = pygame.image.load("img/logoupcc.png")  # Asegúrate de que esta ruta sea correcta
logo_image = pygame.transform.scale(logo_image, (logo_image.get_width() // 2.5, logo_image.get_height() // 2.5))

def draw_header(surface, screen_width):
    # Inicializar la fuente para el header
    header_font = pygame.font.SysFont("Helvetica", 34)
    
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

def draw_footer(surface, screen_width, screen_height):
    # Inicializar la fuente para el footer
    footer_font = pygame.font.SysFont("Helvetica", 24)
    
    footer_height = 80
    footer_surface = pygame.Surface((screen_width, footer_height), pygame.SRCALPHA)
    footer_surface.fill((30, 30, 30, 137))  # Color #1E1E1E con 54% de transparencia
    
    # Texto en el footer
    draw_text("Welcome to AcomplePower (1.0)", footer_font, FONT_COLOR, footer_surface, screen_width // 2, footer_height // 2 - 20)
    draw_text("Astuyauri Calderon, Jherson David", footer_font, FONT_COLOR, footer_surface, screen_width // 4.5, footer_height // 2 + 10)
    draw_text("Quispesivana Torres, Claudio Sandro", footer_font, FONT_COLOR, footer_surface, screen_width // 2, footer_height // 2 + 10)
    draw_text("Talizo Balbín, Joan Jefferson", footer_font, FONT_COLOR, footer_surface, 3 * screen_width // 4, footer_height // 2 + 10)
    
    # Dibujar el footer en la pantalla principal
    surface.blit(footer_surface, (0, screen_height - footer_height))

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)