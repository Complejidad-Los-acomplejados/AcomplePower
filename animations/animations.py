import pygame
from config.config import BLACK, WHITE
from ui.ui import draw_text


def pre_home_animation(screen, screen_width, screen_height):
    font = pygame.font.SysFont("Helvetica", 80)
    alpha = 255
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < 3000:  # 3 segundos
        screen.fill(BLACK)
        draw_text("Welcome", font, WHITE, screen, screen_width // 2, screen_height // 2)
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
        alpha = max(100, alpha - 5)  # Reducir la transparencia, pero no desaparecer completamente
        pygame.display.flip()
        clock.tick(60)

def animate_button(button_rect):
    return pygame.Rect(button_rect.x - 5, button_rect.y - 5, button_rect.width + 10, button_rect.height + 10)


