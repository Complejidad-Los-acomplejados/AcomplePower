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


pygame.init()
pygame.mixer.init()


font = pygame.font.SysFont("Helvetica", 40) 
small_font = pygame.font.SysFont("Helvetica", 30)
footer_font = pygame.font.SysFont("Helvetica", 34)  


window_width, window_height = 900, 600
os.environ['SDL_VIDEO_CENTERED'] = '1'
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("AcomplePower")


assets = load_assets(window_width, window_height)


audio_icon = pygame.image.load("img/audio_icon.png")
audio_icon = pygame.transform.scale(audio_icon, (50, 50))
audio_button_rect = audio_icon.get_rect(topleft=(window_width - 60, 10))


pre_home_animation(screen, window_width, window_height)


logo_pulse = 1
pulse_direction = 1
logo_clicked = False
logo_x = window_width // 2 - 200
logo_y = window_height // 2 - 200
logo_target_x = logo_x
paused = False
music_muted = False


root = tk.Tk()
root.withdraw()  


running = True
hovered_start = False
hovered_exit = False
hovered_resume = False

while running:
    screen.fill(BLACK)
    screen.blit(assets['background_image'], (0, 0))


    draw_header(screen, window_width)


    screen.blit(audio_icon, audio_button_rect.topleft)

    if not paused:

        if not logo_clicked:
            logo_size = 400 + logo_pulse
            logo_pulse += pulse_direction
            if logo_pulse > 20 or logo_pulse < -20:
                pulse_direction *= -1
        else:
            logo_size = 400

        logo_image_scaled = pygame.transform.scale(assets['logo_surface'], (logo_size, logo_size))

        if logo_clicked:
            logo_target_x = window_width // 2 - 350  
        else:
            logo_target_x = window_width // 2 - logo_size // 2

        logo_x += (logo_target_x - logo_x) * 0.1

        if logo_clicked:
            mx, my = pygame.mouse.get_pos()

            start_button_rect.x = logo_x + logo_size // 2
            start_button_rect.y = logo_y + logo_size // 2 - 95  
            if start_button_rect.collidepoint((mx, my)):
                pygame.draw.rect(screen, HOVER_COLOR, animate_button(start_button_rect), border_radius=5)
                if not hovered_start:
                    assets['hover_sound'].play()
                    hovered_start = True
            else:
                pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, start_button_rect, border_radius=5)
                hovered_start = False
            draw_text("Start", font, FONT_COLOR, screen, start_button_rect.centerx + 100, start_button_rect.centery)

    
            exit_button_rect.x = logo_x + logo_size // 2
            exit_button_rect.y = logo_y + logo_size // 2 + 15  
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

        draw_footer(screen, window_width, window_height)
    else:
        overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        mx, my = pygame.mouse.get_pos()

        pygame.draw.rect(screen, BUTTON_BACKGROUND_COLOR, pause_button_background_rect, border_radius=10)

        if resume_button_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, HOVER_COLOR, animate_button(resume_button_rect), border_radius=5)
            if not hovered_resume:
                assets['hover_sound'].play()
                hovered_resume = True
        else:
            pygame.draw.rect(screen, RESUME_BUTTON_COLOR, resume_button_rect, border_radius=5)
            hovered_resume = False
        draw_text("Regresar", font, FONT_COLOR, screen, resume_button_rect.centerx, resume_button_rect.centery)

   
        if quit_button_rect.collidepoint((mx, my)):
            pygame.draw.rect(screen, HOVER_COLOR, animate_button(quit_button_rect), border_radius=5)
            if not hovered_quit:
                assets['hover_sound'].play()
                hovered_quit = True
        else:
            pygame.draw.rect(screen, QUIT_BUTTON_COLOR, quit_button_rect, border_radius=5)
            hovered_quit = False
        draw_text("Salir", font, FONT_COLOR, screen, quit_button_rect.centerx, quit_button_rect.centery)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if audio_button_rect.collidepoint((mx, my)):
                if music_muted:
                    pygame.mixer.music.unpause()
                    music_muted = False
                else:
                    pygame.mixer.music.pause()
                    music_muted = True
            elif not paused:
                if not logo_clicked and logo_x < mx < logo_x + logo_size and logo_y < my < logo_y + logo_size:
                    logo_clicked = True
                elif logo_clicked:
                    if start_button_rect.collidepoint((mx, my)):
                        print("Start button pressed")
                        root.deiconify() 
                        setup_tkinter(root)
                        root.update() 
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
    root.update()  