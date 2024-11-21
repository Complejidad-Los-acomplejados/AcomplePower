import pygame
import sys
import os
import subprocess
from config.config import *
from assets.assets import load_assets
from animations.animations import pre_home_animation, animate_button
from ui.ui import draw_header, draw_footer, draw_text
from acomplexpower import setup_tkinter
import tkinter as tk

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Inicializar fuentes después de inicializar Pygame
font = pygame.font.SysFont("Helvetica", 40)  # Aumentar el tamaño de la fuente
small_font = pygame.font.SysFont("Helvetica", 30)
footer_font = pygame.font.SysFont("Helvetica", 34)  # Fuente más grande para el footer

# Configuración de pantalla más pequeña y centrada
window_width, window_height = 900, 600
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("AcomplePower")

# Cargar recursos
assets = load_assets(window_width, window_height)

# Ejecutar la animación de pre-home
pre_home_animation(screen, window_width, window_height)

# Variables de animación y estado
logo_pulse = 1
pulse_direction = 1
logo_clicked = False
logo_x = window_width // 2 - 200
logo_y = window_height // 2 - 200
logo_target_x = logo_x
paused = False

# Crear la ventana de Tkinter
root = tk.Tk()
root.withdraw()  # Ocultar la ventana de Tkinter hasta que se necesite

# Bucle principal
running = True
hovered_start = False
hovered_exit = False
hovered_resume = False

while running:
    screen.fill(BLACK)
    screen.blit(assets['background_image'], (0, 0))

    # Dibujar el header
    draw_header(screen, window_width)

    if not paused:
        # Animación de pulsación para el logo
        if not logo_clicked:
            logo_size = 400 + logo_pulse
            logo_pulse += pulse_direction
            if logo_pulse > 20 or logo_pulse < -20:
                pulse_direction *= -1
        else:
            logo_size = 400

        logo_image_scaled = pygame.transform.scale(assets['logo_surface'], (logo_size, logo_size))

        if logo_clicked:
            logo_target_x = window_width // 2 - 350  # Mover el logo a la izquierda
        else:
            logo_target_x = window_width // 2 - logo_size // 2

        # Deslizar el logo hacia la izquierda
        logo_x += (logo_target_x - logo_x) * 0.1

        # Dibuja los botones solo si el logo ha sido clicado
        if logo_clicked:
            mx, my = pygame.mouse.get_pos()

            # Botón Start
            start_button_rect.x = logo_x + logo_size // 2
            start_button_rect.y = logo_y + logo_size // 2 - 95  # Ajusta esta línea para cambiar la altura del botón Start
            if start_button_rect.collidepoint((mx, my)):
                pygame.draw.rect(screen, HOVER_COLOR, animate_button(start_button_rect), border_radius=5)
                if not hovered_start:
                    assets['hover_sound'].play()
                    hovered_start = True
            else:
                pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, start_button_rect, border_radius=5)
                hovered_start = False
            draw_text("Start", font, FONT_COLOR, screen, start_button_rect.centerx + 100, start_button_rect.centery)

            # Botón Exit
            exit_button_rect.x = logo_x + logo_size // 2
            exit_button_rect.y = logo_y + logo_size // 2 + 15  # Ajusta esta línea para cambiar la altura del botón Exit
            if exit_button_rect.collidepoint((mx, my)):
                pygame.draw.rect(screen, HOVER_COLOR, animate_button(exit_button_rect), border_radius=5)
                if not hovered_exit:
                    assets['hover_sound'].play()
                    hovered_exit = True
            else:
                pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, exit_button_rect, border_radius=5)
                hovered_exit = False
            draw_text("Exit", font, FONT_COLOR, screen, exit_button_rect.centerx + 100, exit_button_rect.centery)

        screen.blit(logo_image_scaled, (logo_x, logo_y))

        # Dibujar el footer
        draw_footer(screen, window_width, window_height)
    else:
        # Oscurecer el fondo
        overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        # Dibuja el menú de pausa
        mx, my = pygame.mouse.get_pos()

        # Fondo detrás de los botones del menú de pausa
        pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, pause_button_background_rect, border_radius=10)

        # Botón Resume
        if resume_button_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, HOVER_COLOR, animate_button(resume_button_rect), border_radius=5)
            if not hovered_resume:
                assets['hover_sound'].play()
                hovered_resume = True
        else:
            pygame.draw.rect(screen, RESUME_BUTTON_COLOR, resume_button_rect, border_radius=5)
            hovered_resume = False
        draw_text("Regresar", font, FONT_COLOR, screen, resume_button_rect.centerx, resume_button_rect.centery)

        # Botón Quit
        if quit_button_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, HOVER_COLOR, animate_button(quit_button_rect), border_radius=5)
            if not hovered_quit:
                assets['hover_sound'].play()
                hovered_quit = True
        else:
            pygame.draw.rect(screen, QUIT_BUTTON_COLOR, quit_button_rect, border_radius=5)
            hovered_quit = False
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
                        root.deiconify()  # Mostrar la ventana de Tkinter
                        setup_tkinter(root)
                        root.update()  # Actualizar la ventana de Tkinter
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
    root.update()  # Mantener la ventana de Tkinter actualizada