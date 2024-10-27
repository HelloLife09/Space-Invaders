import pygame
import random
import sys

pygame.init()

WIDTH = 600
HEIGHT = 600
FPS = 20
BACKGROUND = (80, 165, 255)
PLAYER_VEL = 12
INVADER_VEL = 5
INVADER_BULLET_CHANCE = 0.8

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")


class Player:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.vel = 0

    def move(self, dx):
        self.x += dx
        self.rect.x = self.x

    def move_left(self):
        self.vel = -PLAYER_VEL

    def move_right(self):
        self.vel = PLAYER_VEL

    def update(self):
        if self.vel < 0 and self.rect.x > 0:
            self.move(self.vel)
        elif self.vel > 0 and (self.rect.x + self.rect.width) < WIDTH:
            self.move(self.vel)
        else:
            self.vel = 0

    def check_collision(self, other_rect):
        return self.rect.colliderect(other_rect)


class Invader:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.direction = "right"
        self.moving_down = False

    def move_right(self):
        self.x += INVADER_VEL
        self.rect.x = self.x

    def move_left(self):
        self.x -= INVADER_VEL
        self.rect.x = self.x

    def move_down(self):
        self.y += self.rect.height + 5
        self.rect.y = self.y
        self.moving_down = False

    def update(self, invader_bullet_cooldown, new_invader_bullet):
        if self.moving_down:
            self.move_down()
            if self.direction == "right":
                self.move_right()
            else:
                self.move_left()
        else:
            if self.rect.x >= WIDTH - self.rect.width:
                self.direction = "left"
                self.moving_down = True
            elif self.rect.x <= 0:
                self.direction = "right"
                self.moving_down = True
            else:
                if self.direction == "right":
                    self.move_right()
                elif self.direction == "left":
                    self.move_left()

        if random.random() > INVADER_BULLET_CHANCE and new_invader_bullet:
            self.new_bullet_ = Bullet(self.rect.centerx, self.rect.bottom, "down")
            return self.new_bullet_
        else:
            return None


class Bullet:
    def __init__(self, x, y, direction):
        self.rect = pygame.Rect(x, y, 5, 10)
        self.x = x
        self.y = y
        self.direction = direction
        self.vel = 5

    def move_up(self):
        self.y -= self.vel
        self.rect.y = self.y

    def move_down(self):
        self.y += self.vel
        self.rect.y = self.y

    def update(self):
        if self.direction == "up":
            self.move_up()
        elif self.direction == "down":
            self.move_down()

    def check_collision(self, other_rect):
        return self.rect.colliderect(other_rect)


def draw(player, invaders, bullets):
    screen.fill(BACKGROUND)

    pygame.draw.rect(screen, (25, 230, 40), player.rect)

    for invader in invaders:
        pygame.draw.rect(screen, (255, 0, 0), invader.rect)

    for bullet in bullets:
        pygame.draw.rect(screen, (0, 0, 255), bullet.rect)

    pygame.display.update()


def main():
    clock = pygame.time.Clock()

    player = Player(WIDTH / 2, HEIGHT - 40, 60, 40)

    player_health = 5

    invaders = []
    for i in range(8):
        invaders.append(Invader(10 + i * 70, 10, 60, 40))

    bullets = []

    invader_bullet_cooldown = 500
    player_bullet_cooldown = 500
    prev_player_bullet = 100
    prev_invader_bullet = 1000
    new_invader_bullet = False
    new_player_bullet = False

    running = True
    while running:
        clock.tick(FPS)

        running_time = pygame.time.get_ticks()

        if running_time - prev_invader_bullet >= invader_bullet_cooldown:
            new_invader_bullet = True
            prev_invader_bullet = running_time

        if running_time - prev_player_bullet >= player_bullet_cooldown:
            new_player_bullet = True
            prev_player_bullet = running_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.move_left()
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.move_right()
                elif event.key == pygame.K_SPACE and new_player_bullet:
                    bullets.append(Bullet(player.rect.centerx, player.rect.top, "up"))
                    new_player_bullet = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.vel = 0
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.vel = 0

        for invader in invaders:
            bullet_new = invader.update(invader_bullet_cooldown, new_invader_bullet)
            if bullet_new:
                bullets.append(bullet_new)
                new_invader_bullet = False

        for bullet in bullets:
            if bullet.direction == "up":
                bullet.move_up()

                if bullet.rect.bottom < 0:
                    bullets.remove(bullet)

                for invader in invaders:
                    if bullet.check_collision(invader.rect):
                        invaders.remove(invader)
                        bullets.remove(bullet)
                        break
            elif bullet.direction == "down":
                bullet.move_down()

                if bullet.rect.top > HEIGHT:
                    bullets.remove(bullet)

                if bullet.check_collision(player.rect):
                    player_health -= 1
                    bullets.remove(bullet)

        if player_health <= 0:
            running = False
            break

        player.update()
        for invader in invaders:
            invader.update(invader_bullet_cooldown, new_invader_bullet)
        for bullet in bullets:
            bullet.update()
        draw(player, invaders, bullets)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
