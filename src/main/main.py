import pygame
import random
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from player.player import Player

WIDTH = 800
HEIGHT = 600
FPS = 60
PIPE_WIDTH = 70
PIPE_GAP = 100
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 1500
DEBUG = False

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
BIRD_IMAGE = os.path.join(ASSETS_DIR, 'images', 'FlappyRed.png')
PIPE_UPRIGHT_IMAGE = os.path.join(ASSETS_DIR, 'images', 'pipe-upright.png')
PIPE_UPSIDE_DOWN_IMAGE = os.path.join(ASSETS_DIR, 'images', 'pipe-upside-down.png')
BACKGROUND_IMAGE = os.path.join(ASSETS_DIR, 'images', 'BackgroundFlappy.png')


class Pipe:
    def __init__(self, x, pipe_upright_image=None, pipe_upside_down_image=None):
        self.x = x
        self.gap_y = random.randint(150, HEIGHT - 150 - PIPE_GAP)
        self.color = (0, 200, 0)
        self.passed = False

        # Bottom pipe (upright)
        self.bottom_pipe_body = None
        self.bottom_pipe_cap = None
        # Top pipe (upside down)
        self.top_pipe_body = None
        self.top_pipe_cap = None

        # Load upright pipe for bottom
        if pipe_upright_image and os.path.exists(pipe_upright_image):
            try:
                original = pygame.image.load(pipe_upright_image).convert_alpha()
                original_width, original_height = original.get_size()
                scale_factor = PIPE_WIDTH / original_width
                new_height = int(original_height * scale_factor)
                scaled_pipe = pygame.transform.scale(original, (PIPE_WIDTH, new_height))

                cap_height = new_height // 4
                self.bottom_pipe_cap = scaled_pipe.subsurface((0, 0, PIPE_WIDTH, cap_height)).copy()
                body_height = new_height - cap_height
                self.bottom_pipe_body = scaled_pipe.subsurface((0, cap_height, PIPE_WIDTH, body_height)).copy()
            except pygame.error as e:
                print(f"Could not load upright pipe image: {pipe_upright_image}, {e}")

        # Load upside down pipe for top
        if pipe_upside_down_image and os.path.exists(pipe_upside_down_image):
            try:
                original = pygame.image.load(pipe_upside_down_image).convert_alpha()
                original_width, original_height = original.get_size()
                scale_factor = PIPE_WIDTH / original_width
                new_height = int(original_height * scale_factor)
                scaled_pipe = pygame.transform.scale(original, (PIPE_WIDTH, new_height))

                cap_height = new_height // 4
                self.top_pipe_cap = scaled_pipe.subsurface((0, new_height - cap_height, PIPE_WIDTH, cap_height)).copy()
                body_height = new_height - cap_height
                self.top_pipe_body = scaled_pipe.subsurface((0, 0, PIPE_WIDTH, body_height)).copy()
            except pygame.error as e:
                print(f"Could not load upside down pipe image: {pipe_upside_down_image}, {e}")

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        if self.top_pipe_body and self.top_pipe_cap and self.bottom_pipe_body and self.bottom_pipe_cap:
            # Draw top pipe (upside down)
            top_cap_height = self.top_pipe_cap.get_height()
            top_cap_y = self.gap_y - top_cap_height
            screen.blit(self.top_pipe_cap, (self.x, top_cap_y))

            # Stretch top pipe body from screen top to cap
            top_body_height = top_cap_y
            if top_body_height > 0:
                stretched_top_body = pygame.transform.scale(self.top_pipe_body, (PIPE_WIDTH, top_body_height))
                screen.blit(stretched_top_body, (self.x, 0))

            # Draw bottom pipe (upright)
            bottom_cap_y = self.gap_y + PIPE_GAP
            screen.blit(self.bottom_pipe_cap, (self.x, bottom_cap_y))

            # Stretch bottom pipe body from cap to screen bottom
            bottom_cap_height = self.bottom_pipe_cap.get_height()
            bottom_body_height = HEIGHT - (bottom_cap_y + bottom_cap_height)
            if bottom_body_height > 0:
                stretched_bottom_body = pygame.transform.scale(self.bottom_pipe_body, (PIPE_WIDTH, bottom_body_height))
                screen.blit(stretched_bottom_body, (self.x, bottom_cap_y + bottom_cap_height))

        else:
            # Fallback to colored rectangles if images not loaded
            pygame.draw.rect(screen, self.color,
                            (self.x, 0, PIPE_WIDTH, self.gap_y))
            pygame.draw.rect(screen, (0, 0, 0),
                            (self.x, 0, PIPE_WIDTH, self.gap_y), 3)
            # Bottom pipe
            pygame.draw.rect(screen, self.color,
                            (self.x, self.gap_y + PIPE_GAP, PIPE_WIDTH, HEIGHT))
            pygame.draw.rect(screen, (0, 0, 0),
                            (self.x, self.gap_y + PIPE_GAP, PIPE_WIDTH, HEIGHT), 3)

    def collides_with(self, player):
        player_rect = player.get_rect()
        # Add padding to match visual pipe width and height
        horizontal_padding = 25
        vertical_padding = 20
        top_pipe = pygame.Rect(self.x + horizontal_padding, 0,
                               PIPE_WIDTH - (horizontal_padding * 2),
                               self.gap_y - vertical_padding)
        bottom_pipe = pygame.Rect(self.x + horizontal_padding,
                                  self.gap_y + PIPE_GAP + vertical_padding,
                                  PIPE_WIDTH - (horizontal_padding * 2),
                                  HEIGHT - (self.gap_y + PIPE_GAP + vertical_padding))
        return player_rect.colliderect(top_pipe) or player_rect.colliderect(bottom_pipe)

    def get_collision_rects(self):
        horizontal_padding = 25
        vertical_padding = 20
        top_pipe = pygame.Rect(self.x + horizontal_padding, 0,
                               PIPE_WIDTH - (horizontal_padding * 2),
                               self.gap_y - vertical_padding)
        bottom_pipe = pygame.Rect(self.x + horizontal_padding,
                                  self.gap_y + PIPE_GAP + vertical_padding,
                                  PIPE_WIDTH - (horizontal_padding * 2),
                                  HEIGHT - (self.gap_y + PIPE_GAP + vertical_padding))
        return [top_pipe, bottom_pipe]

    def is_offscreen(self):
        return self.x + PIPE_WIDTH < 0


def draw_score(screen, score, font):
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))


def draw_game_over(screen, score, font):
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    restart_text = font.render("Press SPACE to restart", True, (255, 255, 255))

    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))


def load_background(background_path):
    """Load and scale the background image if it exists."""
    if os.path.exists(background_path):
        try:
            bg = pygame.image.load(background_path).convert()
            bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            return bg
        except pygame.error:
            print(f"Could not load background image: {background_path}")
    return None


def reset_game():
    """Reset the game state for a new game."""
    player = Player(WIDTH // 4, HEIGHT // 2, BIRD_IMAGE)
    pipes = [Pipe(WIDTH + 200, PIPE_UPRIGHT_IMAGE, PIPE_UPSIDE_DOWN_IMAGE)]
    score = 0
    return player, pipes, score


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CS Flappy Bird")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 48)

    background = load_background(BACKGROUND_IMAGE)

    player, pipes, score = reset_game()

    running = True
    game_over = False
    last_pipe_time = pygame.time.get_ticks()

    while running:
        current_time = pygame.time.get_ticks()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # Restart the game
                        player, pipes, score = reset_game()
                        game_over = False
                        last_pipe_time = current_time
                    else:
                        # Make the bird jump
                        player.jump()

        if not game_over:
            player.update()

            if player.y - player.size < 0 or player.y + player.size > HEIGHT:
                game_over = True

            if current_time - last_pipe_time > PIPE_SPAWN_INTERVAL:
                pipes.append(Pipe(WIDTH, PIPE_UPRIGHT_IMAGE, PIPE_UPSIDE_DOWN_IMAGE))
                last_pipe_time = current_time

            for pipe in pipes[:]:
                pipe.update()

                if pipe.collides_with(player):
                    game_over = True

                if pipe.is_offscreen():
                    pipes.remove(pipe)

                if not pipe.passed and pipe.x + PIPE_WIDTH < player.x:
                    pipe.passed = True
                    score += 1

        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((135, 206, 235)) 

        for pipe in pipes:
            pipe.draw(screen)

        player.draw(screen)

        if DEBUG:
            
            pygame.draw.rect(screen, (255, 0, 0), player.get_rect(), 2)
            
            for pipe in pipes:
                for rect in pipe.get_collision_rects():
                    pygame.draw.rect(screen, (255, 0, 0), rect, 2)

        draw_score(screen, score, font)

        if game_over:
            draw_game_over(screen, score, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
