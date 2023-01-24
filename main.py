import json

from pygame import *
from random import *
from math import *
from time import time as timer

with open('data.json', 'r', encoding='utf=8') as file:
    best_score = json.load(file)

score = 0
num_fire = 0
rel_time = False
last_time = 0
max_fire = 10
wave = 2
p_score = 0
reloading_time = 3
bullets_per_firing = 1
faster_bullet = 5
bonusing = 0

rocket = transform.scale(image.load('res/sprites/rocket.png'), (20, 25))
font.init()
font1 = font.SysFont('Arial', 36)
font2 = font.SysFont('Arial', 72)
font3 = font.SysFont('Arial', 20)


# Классы
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, directionx, directiony, angle,
                 health):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.player_image = image.load(player_image)
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.height / 2)
        self.rect.x += player_x
        self.rect.y += player_y
        self.size = [size_x, size_y]
        self.directionx = directionx
        self.directiony = directiony
        self.angle = angle
        self.health = health

    def reset(self):
        self.image_a = transform.rotate(self.image, self.angle - 90)
        window.blit(self.image_a, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def fire(self):
        fire.play()
        for i in range(bullets_per_firing):
            bullet = Bullet('res/sprites/bullet.png', self.rect.centerx, self.rect.centery, randint(5, 10),
                            randint(7, 14),
                            randint(faster_bullet, faster_bullet * 2), 0, 0, self.angle + (randint(0, 10) - 5), 1)
            bullets.add(bullet)

    def update(self):
        keys = key.get_pressed()
        if (keys[K_LEFT] or keys[K_a]) and self.rect.x >= self.speed:
            self.rect.x -= self.speed
        if (keys[K_RIGHT] or keys[K_d]) and self.rect.x <= (win_width - self.speed - self.size[0]):
            self.rect.x += self.speed
        if (keys[K_UP] or keys[K_w]) and self.rect.y >= self.speed:
            self.rect.y -= self.speed
        if (keys[K_DOWN] or keys[K_s]) and self.rect.y <= win_height - self.speed - self.size[1]:
            self.rect.y += self.speed
        if keys[K_z]:
            self.angle += 4
        if keys[K_x]:
            self.angle -= 4
        if keys[K_c]:
            self.angle = 90


class Enemy(GameSprite):
    def update(self):
        if self.rect.x < 0:
            self.directionx = 2
        elif self.rect.x > win_width - self.size[0]:
            self.directionx = 1
        if self.rect.y < 0:
            self.directiony = 2
        elif self.rect.y > win_height - self.size[1]:
            self.directiony = 1
        if self.directiony == 2:
            self.rect.y += randint(int(self.speed * 0.1), int(self.speed * 1.6)) / 10
        elif self.directiony == 1:
            self.rect.y -= randint(int(self.speed * 0.1), int(self.speed * 1.6)) / 10
        if self.directionx == 1:
            self.rect.x -= randint(int(self.speed * 0.1), int(self.speed * 1.6)) / 10
        elif self.directionx == 2:
            self.rect.x += randint(int(self.speed * 0.1), int(self.speed * 1.6)) / 10


class Bullet(GameSprite):
    def update(self):
        self.rect.y -= sin(radians(self.angle)) * randint(int(self.speed * 0.8), int(self.speed * 1.6))
        self.rect.x += cos(radians(self.angle)) * randint(int(self.speed * 0.8), int(self.speed * 1.6))
        if (self.rect.x < 0) or (self.rect.y < 0) or (self.rect.x > win_width) or (self.rect.y > win_height):
            self.kill()


class Bonus(GameSprite):
    def update(self):
        self.rect.y += randint(int(self.speed * 0.1), int(self.speed * 1.6)) / 10
        if self.rect.x < 0:
            self.directionx = 2
        elif self.rect.x > win_width - self.size[0]:
            self.directionx = 1
        if self.directionx == 1:
            self.rect.x -= randint(int(self.speed * 0.1), int(self.speed * 1.6)) / 10
        elif self.directionx == 2:
            self.rect.x += randint(int(self.speed * 0.1), int(self.speed * 1.6)) / 10
        if self.rect.y > win_height:
            self.kill()


# Музыка
mixer.init()
mixer.music.load('res/sound/space.ogg')
mixer.music.play()
fire = mixer.Sound('res/sound/fire.ogg')

# Фон
win_width, win_height = 700, 500
window = display.set_mode((win_width, win_height))
display.set_caption('Eternal Space MeatGrinder XXL')
background = transform.scale(image.load('res/sprites/galaxy.jpg'), (win_width, win_height))
background_menu = transform.scale(image.load('res/sprites/galaxy.jpg'), (win_width, win_height))
settings = transform.scale(image.load('res/sprites/settings.png'), (int(win_width / 20), int(win_width / 20)))
play = transform.scale(image.load('res/sprites/rocket.png'), (int(win_width / 10), int(win_width / 5)))

# Пре-игровые даные
run = True
finish = False
menu = False
setting = False
clock = time.Clock()
FPS = 60

# Выигрыши и проигрыши:
lose = font2.render('Вы проиграли!', True, (255, 255, 255))
win = font2.render('Вы выиграли!', True, (255, 255, 255))

bullets = sprite.Group()
monsters = sprite.Group()
asteroids = sprite.Group()
bonus_double_bullets = sprite.Group()
bonus_more_bullets = sprite.Group()
bonus_faster_reloading = sprite.Group()
bonus_health = sprite.Group()
bonus_less_wave = sprite.Group()
bonus_faster_bullet = sprite.Group()

player = Player('res/sprites/rocket.png', 80, win_height - 100, 80, 100, 10, 0, 0, 90, 5)

# Игровой цикл
while run:
    if not finish:
        window.blit(background, (0, 0))
        clock.tick(FPS)

        player.update()
        monsters.update()
        bullets.update()
        player.reset()
        monsters.draw(window)
        bullets.draw(window)
        # bonuses drawing:
        bonus_faster_bullet.update()
        bonus_double_bullets.update()
        bonus_faster_reloading.update()
        bonus_health.update()
        bonus_less_wave.update()
        bonus_more_bullets.update()
        bonus_faster_bullet.draw(window)
        bonus_double_bullets.draw(window)
        bonus_faster_reloading.draw(window)
        bonus_health.draw(window)
        bonus_less_wave.draw(window)
        bonus_more_bullets.draw(window)

        if (len(monsters) < wave) and (p_score > 0):
            enemy = Enemy('res/sprites/ufo.png', randint(0, win_width - 75), -50, 75, 50, 20, randint(1, 2), 1, 90, 1)
            monsters.add(enemy)

        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            p_score -= 1
            bonusing = randint(1, 100)
            if bonusing == 1:
                bonus = Bonus('res/bonuses/bonus_less_wave.png', randint(0, win_width - 75), -50, 25, 25, 40,
                              randint(1, 2), 1, 90,
                              1)
                bonus_less_wave.add(bonus)
            elif (bonusing <= 5) and (bonusing != 1):
                bonus = Bonus('res/bonuses/bonus_double_bullets.png', randint(0, win_width - 75), -50, 25, 25, 40,
                              randint(1, 2), 1,
                              90, 1)
                bonus_double_bullets.add(bonus)
            elif bonusing >= 90:
                bonus = Bonus('res/bonuses/bonus_more_bullets.png', randint(0, win_width - 75), -50, 25, 25, 40,
                              randint(1, 2), 1,
                              90, 1)
                bonus_more_bullets.add(bonus)
            elif (bonusing >= 85) and (bonusing < 90):
                bonus = Bonus('res/bonuses/bonus_faster_reloading.png', randint(0, win_width - 75), -50, 25, 25, 40,
                              randint(1, 2),
                              1, 90, 1)
                bonus_faster_reloading.add(bonus)
            elif (bonusing >= 80) and (bonusing < 85):
                bonus = Bonus('res/bonuses/bonus_faster_bullet.png', randint(0, win_width - 75), -50, 25, 25, 40,
                              randint(1, 2), 1,
                              90, 1)
                bonus_faster_bullet.add(bonus)
            elif (bonusing >= 76) and (bonusing < 80):
                bonus = Bonus('res/bonuses/bonus_health.png', randint(0, win_width - 75), -50, 25, 25, 40,
                              randint(1, 2), 1, 90, 1)
                bonus_health.add(bonus)
            if score > best_score:
                best_score = score
                with open('data.json', 'w', encoding='utf=8') as file:
                    json.dump(best_score, file)

        if sprite.spritecollide(player, monsters, True):
            player.health -= 1
        if sprite.spritecollide(player, asteroids, True):
            player.health -= 2

        # bonuses
        if sprite.spritecollide(player, bonus_less_wave, True):
            wave = int((wave - 0.2) / 1.4)
        if sprite.spritecollide(player, bonus_double_bullets, True):
            bullets_per_firing += 1
        if sprite.spritecollide(player, bonus_health, True):
            player.health += 1
        if sprite.spritecollide(player, bonus_faster_bullet, True):
            faster_bullet += 2
        if sprite.spritecollide(player, bonus_more_bullets, True):
            max_fire *= 1.2
        if sprite.spritecollide(player, bonus_faster_reloading, True):
            reloading_time /= 1.5

        # scoring and other things
        if player.health <= 0:
            finish = True
            window.blit(lose, (200, 200))
        if p_score <= 0:
            wave = int(wave * 1.4 + 0.2)
            p_score = int(wave ** 2)

        for i in range(player.health):
            window.blit(rocket, (1 + 22 * i, 5))

        text_max_killed = font1.render('Лучший счёт:    ' + str(best_score), True, (255, 255, 255))
        text_killed = font1.render('Счёт:    ' + str(score), True, (255, 255, 255))
        window.blit(text_max_killed, (10, 66))
        window.blit(text_killed, (10, 30))

        if rel_time:
            now_time = timer()
            reloading = font3.render('Перезарядка', True, (255, 255, 0))
            window.blit(reloading, (player.rect.centerx - 90, player.rect.centery))
            if now_time - last_time >= reloading_time:
                rel_time = False
                num_fire = 0

    for e in event.get():
        # Обработка выхода
        if e.type == QUIT:
            run = False

        # обработка стрельбы
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < max_fire and not rel_time:
                    num_fire += 1
                    player.fire()
                if num_fire >= max_fire and not rel_time:
                    last_time = timer()
                    rel_time = True

    display.update()
