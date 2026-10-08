import random
import pygame
from game.block import Block, Debris


PERFECT_TOLERANCE = 12.0
PERFECT_BONUS = 3
PERFECT_RESTORE_WIDTH = 12.0
PERFECT_POPUP_DURATION = 800

BACKGROUND_STAGE_COLORS = [
    (45, 85, 145),    # Evening blue
    (220, 105, 75),   # Dusk orange
    (185, 85, 135),   # Dusk pink
    (65, 45, 105),    # Deep purple night
    (8, 10, 20),      # Near-black space
]
BACKGROUND_TRANSITION_BLOCKS = 40


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.block_height = 28
        self.base_width = 180

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 28)
        self.font_big = pygame.font.SysFont(None, 46)

        random.seed(7)
        self.stars = [
            (random.randint(10, self.width - 10), random.randint(10, self.height - 10))
            for _ in range(45)
        ]

        self.reset()

    def get_color(self, index):
        palette = [
            (230, 75, 75),   # Crimson
            (240, 140, 45),  # Orange
            (245, 210, 50),  # Gold
            (60, 195, 110),  # Green
            (50, 150, 240),  # Blue
            (165, 80, 225),  # Purple
        ]
        return palette[index % len(palette)]

    def reset(self):
        self.score = 0
        self.game_over = False
        self.perfect_streak = 0
        self.perfect_popup_start = None
        self.perfect_popup_x = 0
        self.perfect_popup_y = 0
        self.debris = []

        base_x = (self.width - self.base_width) // 2
        base_y = self.height - 60
        base_block = Block(
            base_x,
            base_y,
            self.base_width,
            self.block_height,
            self.get_color(0),
            speed=0
        )
        self.stack = [base_block]

        self.spawn_active_block()

    def spawn_active_block(self):
        top_block = self.stack[-1]
        next_y = top_block.y - self.block_height - 4
        speed = min(10.0, 4.5 + (len(self.stack) * 0.35))
        color = self.get_color(len(self.stack))

        start_x = 25 if random.choice([True, False]) else self.width - 25 - top_block.width
        self.active_block = Block(
            start_x,
            next_y,
            top_block.width,
            self.block_height,
            color,
            speed=speed
        )

    def get_background_colors(self):
        progress = min(1.0, self.score / BACKGROUND_TRANSITION_BLOCKS)
        stage_count = len(BACKGROUND_STAGE_COLORS) - 1

        scaled_progress = progress * stage_count
        stage_index = min(int(scaled_progress), stage_count - 1)
        stage_progress = scaled_progress - stage_index

        color_a = BACKGROUND_STAGE_COLORS[stage_index]
        color_b = BACKGROUND_STAGE_COLORS[stage_index + 1]

        current_color = tuple(
            int(color_a[i] + (color_b[i] - color_a[i]) * stage_progress)
            for i in range(3)
        )

        top_color = tuple(
            min(255, int(value * 1.18))
            for value in current_color
        )
        bottom_color = tuple(
            max(0, int(value * 0.62))
            for value in current_color
        )

        return top_color, bottom_color, progress

    def render_background(self, screen):
        top_color, bottom_color, progress = self.get_background_colors()

        gradient_height = 80

        for band in range(gradient_height):
            t = band / (gradient_height - 1)
            color = tuple(
                int(top_color[i] + (bottom_color[i] - top_color[i]) * t)
                for i in range(3)
            )
            y = band * self.height // gradient_height
            next_y = (band + 1) * self.height // gradient_height
            pygame.draw.rect(
                screen,
                color,
                (0, y, self.width, next_y - y + 1)
            )

        if progress >= 0.72:
            star_alpha = int(255 * ((progress - 0.72) / 0.28))
            star_surface = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            for x, y in self.stars:
                pygame.draw.circle(
                    star_surface,
                    (255, 255, 255, star_alpha),
                    (x, y),
                    1
                )

            screen.blit(star_surface, (0, 0))

    def drop_block(self):
        if self.game_over:
            return

        top_block = self.stack[-1]
        act = self.active_block

        left = max(act.x, top_block.x)
        right = min(act.x + act.width, top_block.x + top_block.width)
        overlap = right - left

        is_successful_drop = overlap > 0

        if is_successful_drop:
            is_perfect = abs(act.x - top_block.x) <= PERFECT_TOLERANCE

            if is_perfect:
                self.perfect_streak += 1

                new_width = top_block.width

                if self.perfect_streak >= 2:
                    new_width = min(
                        self.base_width,
                        top_block.width + PERFECT_RESTORE_WIDTH
                    )

                new_x = top_block.x - (new_width - top_block.width) / 2
                new_x = max(0, min(new_x, self.width - new_width))

                new_block = Block(
                    new_x,
                    act.y,
                    new_width,
                    self.block_height,
                    act.color,
                    speed=0
                )

                self.score += 1 + PERFECT_BONUS

                self.perfect_popup_start = pygame.time.get_ticks()
                self.perfect_popup_x = new_x + new_width / 2
                self.perfect_popup_y = act.y - 8
            else:
                self.perfect_streak = 0

                if act.x < top_block.x:
                    debris_x = act.x
                    debris_width = top_block.x - act.x
                else:
                    debris_x = top_block.x + top_block.width
                    debris_width = (act.x + act.width) - debris_x

                if debris_width > 0:
                    self.debris.append(
                        Debris(
                            debris_x,
                            act.y,
                            debris_width,
                            self.block_height,
                            act.color
                        )
                    )

                trimmed_width = max(10.0, overlap)
                new_block = Block(
                    left,
                    act.y,
                    trimmed_width,
                    self.block_height,
                    act.color,
                    speed=0
                )
                self.score += 1

            self.stack.append(new_block)

            if new_block.y < 180:
                shift_amount = self.block_height + 4
                for b in self.stack:
                    b.y += shift_amount
                for debris in self.debris:
                    debris.shift(shift_amount)

            self.spawn_active_block()
        else:
            self.perfect_streak = 0
            self.game_over = True

    def handle_event(self, event):
        if self.game_over:
            if (event.type == pygame.KEYDOWN and
                event.key in (pygame.K_SPACE, pygame.K_r)) or \
               (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.reset()
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.drop_block()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drop_block()

    def update(self):
        if not self.game_over:
            self.active_block.update(self.width)

        for debris in self.debris:
            debris.update()

        self.debris = [
            debris
            for debris in self.debris
            if not debris.is_off_screen(self.height)
        ]

    def render(self, screen):
        self.render_background(screen)

        title_shadow = self.font_title.render(
            "Skyscraper Stack",
            True,
            (0, 0, 0)
        )
        title_surf = self.font_title.render(
            "Skyscraper Stack",
            True,
            (245, 245, 245)
        )

        title_x = self.width // 2 - title_surf.get_width() // 2
        screen.blit(title_shadow, (title_x + 2, 18))
        screen.blit(title_surf, (title_x, 16))

        score_text = f"Height: {self.score}"
        score_shadow = self.font_hud.render(
            score_text,
            True,
            (0, 0, 0)
        )
        score_surf = self.font_hud.render(
            score_text,
            True,
            (255, 220, 80)
        )

        score_x = self.width // 2 - score_surf.get_width() // 2
        screen.blit(score_shadow, (score_x + 2, 56))
        screen.blit(score_surf, (score_x, 54))

        for b in self.stack:
            b.render(screen)

        for debris in self.debris:
            debris.render(screen)

        if not self.game_over:
            self.active_block.render(screen)

        if self.perfect_popup_start is not None:
            elapsed = pygame.time.get_ticks() - self.perfect_popup_start

            if elapsed < PERFECT_POPUP_DURATION:
                alpha = int(255 * (1 - elapsed / PERFECT_POPUP_DURATION))

                popup_shadow = self.font_big.render(
                    "PERFECT!",
                    True,
                    (0, 0, 0)
                )
                popup_surf = self.font_big.render(
                    "PERFECT!",
                    True,
                    (255, 220, 80)
                )

                popup_shadow.set_alpha(alpha)
                popup_surf.set_alpha(alpha)

                popup_rect = popup_surf.get_rect(
                    center=(
                        int(self.perfect_popup_x),
                        int(self.perfect_popup_y - elapsed * 0.04)
                    )
                )

                shadow_rect = popup_rect.copy()
                shadow_rect.x += 2
                shadow_rect.y += 2

                screen.blit(popup_shadow, shadow_rect)
                screen.blit(popup_surf, popup_rect)
            else:
                self.perfect_popup_start = None

        if self.game_over:
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )
            overlay.fill((0, 0, 0, 195))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_big.render(
                "TOWER COLLAPSED!",
                True,
                (240, 75, 75)
            )
            screen.blit(
                over_surf,
                (
                    self.width // 2 - over_surf.get_width() // 2,
                    self.height // 2 - 40
                )
            )

            final_surf = self.font_hud.render(
                f"Final Height: {self.score}",
                True,
                (255, 255, 255)
            )
            screen.blit(
                final_surf,
                (
                    self.width // 2 - final_surf.get_width() // 2,
                    self.height // 2 + 10
                )
            )

            restart_surf = self.font_hud.render(
                "Press [Space] or [R] to Play Again",
                True,
                (200, 200, 200)
            )
            screen.blit(
                restart_surf,
                (
                    self.width // 2 - restart_surf.get_width() // 2,
                    self.height // 2 + 50
                )
            )