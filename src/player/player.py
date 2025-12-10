import pygame
import os

class Player:

    def __init__(self, x, y, image_path=None):
        self.x = x
        self.y = y
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.size = 30
        self.collision_size = 12
        self.color = (255, 255, 0)
        self.rotation = 0

        self.image = None
        if image_path and os.path.exists(image_path):
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.size * 2, self.size * 2))
            except pygame.error:
                print(f"Could not load bird image: {image_path}")
                self.image = None

    def jump(self):
        self.velocity = self.jump_strength

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rotation = max(-25, min(25, -self.velocity * 3))

    def draw(self, screen):
        if self.image:
            rotated_image = pygame.transform.rotate(self.image, self.rotation)
            rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_image, rect)
        else:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def get_rect(self):
        return pygame.Rect(self.x - self.collision_size, self.y - self.collision_size,
                          self.collision_size * 2, self.collision_size * 2)
