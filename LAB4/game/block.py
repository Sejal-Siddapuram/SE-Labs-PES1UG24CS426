import pygame


class Block:
    def __init__(self, x, y, width, height, color, speed=0):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.color = color
        self.speed = speed
        self.direction = 1

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def update(self, screen_width):
        if self.speed == 0:
            return

        self.x += self.speed * self.direction
        if self.x <= 20:
            self.x = 20
            self.direction = 1
        elif self.x + self.width >= screen_width - 20:
            self.x = screen_width - 20 - self.width
            self.direction = -1

    def render(self, surface):
        draw_rect = self.rect
        pygame.draw.rect(surface, self.color, draw_rect, border_radius=4)
        pygame.draw.rect(surface, (245, 245, 250), draw_rect, width=2, border_radius=4)


class Debris:
    def __init__(self, x, y, width, height, color):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.color = color
        self.velocity_y = -1.5
        self.gravity = 0.35
        self.angle = 0.0
        self.rotation_speed = 5.0 if x < 240 else -5.0

    def update(self):
        self.velocity_y += self.gravity
        self.y += self.velocity_y
        self.angle += self.rotation_speed

    def shift(self, amount):
        self.y += amount

    def is_off_screen(self, screen_height):
        return self.y > screen_height + self.width

    def render(self, surface):
        debris_surface = pygame.Surface(
            (max(1, int(self.width)), max(1, int(self.height))),
            pygame.SRCALPHA
        )
        pygame.draw.rect(
            debris_surface,
            self.color,
            debris_surface.get_rect(),
            border_radius=4
        )
        pygame.draw.rect(
            debris_surface,
            (245, 245, 250),
            debris_surface.get_rect(),
            width=2,
            border_radius=4
        )

        rotated_surface = pygame.transform.rotate(debris_surface, self.angle)
        rect = rotated_surface.get_rect(
            center=(
                int(self.x + self.width / 2),
                int(self.y + self.height / 2)
            )
        )
        surface.blit(rotated_surface, rect)