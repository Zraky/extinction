import pygame, sys, random

pygame.init()

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FPS = 60
gravity = 1
clock = pygame.time.Clock()
spawn_time = random.randint(150, 300)
last_spawn = pygame.time.get_ticks()

pygame.display.set_caption("extinction")
icon = pygame.image.load('image/dinosaure/dinosaure.png')
pygame.display.set_icon(icon)

class Map:
    def __init__(self):
        self.map = pygame.image.load('image/map/map1.png').convert()
        self.map = pygame.transform.scale(self.map, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.map.get_rect(topleft=(0, 0))

    def draw(self):
        screen.blit(self.map, self.rect.topleft)

    def update(self):
        self.draw()

maps = Map()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = random.randint(100, 300)
        self.x = random.randint(0, SCREEN_WIDTH - self.size)
        self.speed = random.randint(70, 140)
        self.image = pygame.image.load('image/asteroid/asteroid.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.mask = pygame.mask.from_surface(self.image)
        self.paf = pygame.image.load('image/asteroid/explosion.png').convert_alpha()
        self.paf = pygame.transform.scale(self.paf, (self.size, self.size))
        self.rect = self.image.get_rect(topleft=(self.x, -300))
        self.exploded = False
        self.explosion_time = 0

    def explosion(self):
        self.image = self.paf
        self.mask = pygame.mask.from_surface(self.paf)
        self.exploded = True
        current_time = pygame.time.get_ticks()
        if current_time - self.fall > 700:
            asteroid_group.remove(self)

    def move(self, dt):
        if not self.exploded and self.rect.bottom < 520:
            self.rect.y += self.speed * dt
            self.fall = pygame.time.get_ticks()
        else:
            self.explosion()

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self, dt):
        self.move(dt)
        self.draw()

    def is_exploded(self):
        return self.exploded and pygame.time.get_ticks() - self.explosion_time > 700

asteroid_group = pygame.sprite.Group()

def asteroid_list():
    global spawn_time
    global last_spawn

    current_time = pygame.time.get_ticks()
    if current_time - last_spawn > spawn_time:
        asteroid = Asteroid()
        asteroid_group.add(asteroid)
        spawn_time = random.randint(150, 300)
        last_spawn = pygame.time.get_ticks()

class Game:
    def __init__(self):
        self.play = True
        self.x = 400
        self.y = 200

        self.restart = pygame.image.load('image/game/restart.png').convert_alpha()
        self.restart = pygame.transform.scale(self.restart, (self.x, self.y))
        self.rect_restart = self.restart.get_rect(center=((SCREEN_WIDTH - self.x) / 4, (SCREEN_HEIGHT - self.y) / 2))

        self.exit = pygame.image.load('image/game/button-exit.png').convert_alpha()
        self.exit = pygame.transform.scale(self.exit, (self.x, self.y))
        self.rect_exit = self.exit.get_rect(center=((SCREEN_WIDTH - self.x) * 3 / 4, (SCREEN_HEIGHT - self.y) / 2))

        self.police = pygame.font.SysFont(str(None), 50)
        self.eggs = 0
        self.omelet = 0

    def score(self):
        screen.blit((self.police.render(f"eggs save : {self.eggs}", 1, (0, 0, 0))), (10, 0))

    def game_end(self):
        if pygame.sprite.spritecollide(player, asteroid_group, False, pygame.sprite.collide_mask):
            self.play = False

    def game_restart(self):
        screen.fill((0, 0, 0))
        screen.blit(self.restart, self.rect_restart.center)
        screen.blit(self.exit, self.rect_exit.center)
        screen.blit((self.police.render(f"you save {self.eggs} eggs,  {self.omelet} is omelet now, GG", 1, (255, 255, 255))), (580, 500))


        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0] and self.rect_restart.colliderect(pygame.Rect(pygame.mouse.get_pos(), (1, 1))):
            asteroid_group.empty()
            self.eggs = 0
            self.play = True

        elif mouse_buttons[0] and self.rect_exit.colliderect(pygame.Rect(pygame.mouse.get_pos(), (1, 1))):
            pygame.quit()
            sys.exit()

    def update(self):
        self.score()
        self.game_end()

game = Game()

class Player:
    def __init__(self, player_x, player_y, w, h, jump, speed):
        self.speed = speed
        self.jump_height = jump
        self.velocity = jump
        self.gravity = gravity
        self.jump = False

        self.image_L = pygame.image.load('image/dinosaure/dinosaure.png').convert_alpha()
        self.image_L = pygame.transform.scale(self.image_L, (w, h))

        self.image_R = pygame.transform.flip(self.image_L, True, False)

        self.mask = pygame.mask.from_surface(self.image_L)

        self.rect = self.image_L.get_rect(center=(player_x, player_y))
        self.direction = "right"

    def move(self, dt):
        key = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        if key[pygame.K_RIGHT] and not key[pygame.K_LEFT]:
            self.rect.x += self.speed * dt
            self.direction = "right"
        elif key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
            self.rect.x -= self.speed * dt
            self.direction = "left"

        if self.rect.centerx > SCREEN_WIDTH:
            self.rect.centerx = 0
        elif self.rect.centerx < 0:
            self.rect.centerx = SCREEN_WIDTH

        if mouse_buttons[0] or key[pygame.K_SPACE]:
            self.jump = True

        if self.jump:
            self.rect.y -= self.velocity
            self.velocity -= self.gravity
            if self.velocity < -self.jump_height:
                self.jump = False
                self.velocity = self.jump_height

    def draw(self):
        if self.direction == "right":
            screen.blit(self.image_L, (self.rect.x, self.rect.y))
            self.mask = pygame.mask.from_surface(self.image_L)
        else:
            screen.blit(self.image_R, (self.rect.x, self.rect.y))
            self.mask = pygame.mask.from_surface(self.image_R)

    def update(self, dt):
        self.move(dt)
        self.draw()

player = Player(510, 490, 60, 60, 20, 170)

class Eggs:
    def __init__(self):
        self.size = 50
        self.exist = True
        self.image = pygame.image.load('image/eggs/egg.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH), 520 - self.size, self.size, self.size)

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self):
        if self.rect.colliderect(player.rect):
            game.eggs += 1
            self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH), 520 - self.size, self.size, self.size)

        if pygame.sprite.spritecollide(self, asteroid_group, False, pygame.sprite.collide_mask):
            game.omelet +=1
            self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH), 520 - self.size, self.size, self.size)


    def run(self):
        self.update()
        self.draw()

eggs = Eggs()


while True:
    if game.play == True:
        dt = clock.get_fps() / 1000
        asteroid_list()
        maps.update()
        eggs.run()
        game.update()
        player.update(dt)
        asteroid_group.update(dt)

    else:
        game.game_restart()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.flip()
    clock.tick(FPS)