import pygame
import sys
from header_complej import draw_header  # Importar la función draw_header

# Inicializar Pygame
pygame.init()

# Configuración de pantalla completa
screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("AcomplePower")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 0, 139)  # Azul oscuro
HOVER_COLOR = (0, 191, 255)  # Azul eléctrico brillante
FONT_COLOR = (255, 255, 255)
BUTTON_BACKGROUND_COLOR = (30, 30, 30)
PAUSE_OVERLAY_COLOR = (0, 0, 0, 150)  # Color para oscurecer el fondo

# Colores para los botones del menú de pausa
RESUME_BUTTON_COLOR = (0, 200, 0)
QUIT_BUTTON_COLOR = (200, 0, 0)

# Cargar imágenes
background_image = pygame.image.load("img/fondoaurora.jpg")  # Cambia por la ruta de tu imagen de fondo
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

logo_image = pygame.image.load("img/logo_acomplejpower.png")  # Cambia por la ruta de tu imagen de logo
logo_image = pygame.transform.scale(logo_image, (200, 200))  # Ajusta el tamaño según el diseño

# Crear una superficie circular para el logo
logo_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
pygame.draw.circle(logo_surface, (255, 255, 255), (100, 100), 100)
logo_surface.blit(logo_image, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

# Fuentes
font = pygame.font.SysFont("Helvetica", 20)
small_font = pygame.font.SysFont("Helvetica", 15)
footer_font = pygame.font.SysFont("Helvetica", 18)  # Fuente más grande para el footer

# Función para mostrar texto en pantalla
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

# Función para dibujar el footer
def draw_footer(surface, screen_width, screen_height):
    footer_height = 80
    footer_surface = pygame.Surface((screen_width, footer_height), pygame.SRCALPHA)
    footer_surface.fill((30, 30, 30, 137))  # Color #1E1E1E con 54% de transparencia
    
    # Texto en el footer
    draw_text("Welcome to AcomplePower (1.0)", footer_font, FONT_COLOR, footer_surface, screen_width // 2, footer_height // 2 - 20)
    draw_text("Astuyauri Calderon, Jherson David", footer_font, FONT_COLOR, footer_surface, screen_width // 4, footer_height // 2 + 10)
    draw_text("Quispe Sivana Torres, Claudio Sandro", footer_font, FONT_COLOR, footer_surface, screen_width // 2, footer_height // 2 + 10)
    draw_text("Talizo Balbín, Joan Jefferson", footer_font, FONT_COLOR, footer_surface, 3 * screen_width // 4, footer_height // 2 + 10)
    
    # Dibujar el footer en la pantalla principal
    surface.blit(footer_surface, (0, screen_height - footer_height))

# Funciones de animación de botón
def animate_button(button_rect):
    return pygame.Rect(button_rect.x - 5, button_rect.y - 5, button_rect.width + 10, button_rect.height + 10)

# Variables de los botones
button_width, button_height = 100, 40
button_padding = 20
button_background_width = 300
button_background_height = 60
start_button_background_rect = pygame.Rect(screen_width // 2 + 100, screen_height // 2 - 60, button_background_width, button_background_height)
exit_button_background_rect = pygame.Rect(screen_width // 2 + 100, screen_height // 2 + 20, button_background_width, button_background_height)
start_button_rect = pygame.Rect(start_button_background_rect.x + 20, start_button_background_rect.y + 10, button_width, button_height)
exit_button_rect = pygame.Rect(exit_button_background_rect.x + 20, exit_button_background_rect.y + 10, button_width, button_height)

# Variables de los botones del menú de pausa
pause_button_width, pause_button_height = 200, 50
pause_button_padding = 20
pause_button_background_rect = pygame.Rect(screen_width // 2 - pause_button_width // 2, screen_height // 2 - 60, pause_button_width, pause_button_height * 2 + pause_button_padding)
resume_button_rect = pygame.Rect(pause_button_background_rect.x, pause_button_background_rect.y, pause_button_width, pause_button_height)
quit_button_rect = pygame.Rect(pause_button_background_rect.x, pause_button_background_rect.y + pause_button_height + pause_button_padding, pause_button_width, pause_button_height)

# Variables de animación
logo_pulse = 1
pulse_direction = 1
logo_clicked = False
logo_x = screen_width // 2 - 100
logo_y = screen_height // 2 - 100
logo_target_x = logo_x
paused = False

# Bucle principal
running = True
while running:
    screen.fill(BLACK)
    screen.blit(background_image, (0, 0))

    # Dibujar el header
    draw_header(screen, screen_width)

    if not paused:
        # Animación de pulsación para el logo
        if not logo_clicked:
            logo_size = 200 + logo_pulse
            logo_pulse += pulse_direction
            if logo_pulse > 10 or logo_pulse < -10:
                pulse_direction *= -1
        else:
            logo_size = 200

        logo_image_scaled = pygame.transform.scale(logo_surface, (logo_size, logo_size))

        if logo_clicked:
            logo_target_x = screen_width // 2 - 300  # Mover el logo a la izquierda
        else:
            logo_target_x = screen_width // 2 - logo_size // 2

        # Deslizar el logo hacia la izquierda
        logo_x += (logo_target_x - logo_x) * 0.1

        screen.blit(logo_image_scaled, (logo_x, logo_y))

        # Dibuja los botones solo si el logo ha sido clicado
        if logo_clicked:
            mx, my = pygame.mouse.get_pos()

            # Fondo detrás de los botones
            start_button_background_rect.x = logo_x + logo_size // 2
            exit_button_background_rect.x = logo_x + logo_size // 2
            pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, start_button_background_rect, border_radius=10)
            pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, exit_button_background_rect, border_radius=10)

            # Botón Start
            start_button_rect.x = start_button_background_rect.x + 20
            if start_button_rect.collidepoint((mx, my)):
                pygame.draw.rect(screen, HOVER_COLOR, animate_button(start_button_rect), border_radius=5)
            else:
                pygame.draw.rect(screen, BUTTON_COLOR, start_button_rect, border_radius=5)
            draw_text("Start", font, FONT_COLOR, screen, start_button_rect.centerx, start_button_rect.centery)

            # Botón Exit
            exit_button_rect.x = exit_button_background_rect.x + 20
            if exit_button_rect.collidepoint((mx, my)):
                pygame.draw.rect(screen, HOVER_COLOR, animate_button(exit_button_rect), border_radius=5)
            else:
                pygame.draw.rect(screen, BUTTON_COLOR, exit_button_rect, border_radius=5)
            draw_text("Exit", font, FONT_COLOR, screen, exit_button_rect.centerx, exit_button_rect.centery)

        # Dibujar el footer
        draw_footer(screen, screen_width, screen_height)
    else:
        # Oscurecer el fondo
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        # Dibuja el menú de pausa
        mx, my = pygame.mouse.get_pos()

        # Fondo detrás de los botones del menú de pausa
        pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, pause_button_background_rect, border_radius=10)

        # Botón Resume
        if resume_button_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, HOVER_COLOR, animate_button(resume_button_rect), border_radius=5)
        else:
            pygame.draw.rect(screen, RESUME_BUTTON_COLOR, resume_button_rect, border_radius=5)
        draw_text("Regresar", font, FONT_COLOR, screen, resume_button_rect.centerx, resume_button_rect.centery)

        # Botón Quit
        if quit_button_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, HOVER_COLOR, animate_button(quit_button_rect), border_radius=5)
        else:
            pygame.draw.rect(screen, QUIT_BUTTON_COLOR, quit_button_rect, border_radius=5)
        draw_text("Salir", font, FONT_COLOR, screen, quit_button_rect.centerx, quit_button_rect.centery)

    # Eventos y control de salida
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if not paused:
                if not logo_clicked and logo_x < mx < logo_x + logo_size and logo_y < my < logo_y + logo_size:
                    logo_clicked = True
                elif logo_clicked:
                    if start_button_rect.collidepoint((mx, my)):
                        print("Start button pressed")
                        # Lógica para iniciar el juego
                    elif exit_button_rect.collidepoint((mx, my)):
                        pygame.quit()
                        sys.exit()
            else:
                if resume_button_rect.collidepoint((mx, my)):
                    paused = False
                elif quit_button_rect.collidepoint((mx, my)):
                    pygame.quit()
                    sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused

    pygame.display.flip()
    pygame.time.Clock().tick(60)