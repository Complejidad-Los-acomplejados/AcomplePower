import pygame

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 0, 139)  # Azul oscuro
HOVER_COLOR = (0, 191, 255)  # Azul eléctrico brillante
FONT_COLOR = (255, 255, 255)
BUTTON_BACKGROUND_COLOR = (30, 30, 30, 100)  # Color #1E1E1E con 54% de transparencia
PAUSE_OVERLAY_COLOR = (0, 0, 0, 150)  # Color para oscurecer el fondo

# Colores para los botones del menú de pausa
RESUME_BUTTON_COLOR = (0, 200, 0)
QUIT_BUTTON_COLOR = (200, 0, 0)

# Variables de los botones
button_width, button_height = 400, 80  # Aumentar el tamaño de los botones al doble
button_padding = 50
start_button_rect = pygame.Rect(0, 0, button_width, button_height)
exit_button_rect = pygame.Rect(0, 0, button_width, button_height)

# Variables de los botones del menú de pausa
pause_button_width, pause_button_height = 400, 100
pause_button_padding = 20
pause_button_background_rect = pygame.Rect(0, 0, pause_button_width, pause_button_height * 2 + pause_button_padding)
resume_button_rect = pygame.Rect(0, 0, pause_button_width, pause_button_height)
quit_button_rect = pygame.Rect(0, 0, pause_button_width, pause_button_height)