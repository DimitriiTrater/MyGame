import pygame
import os
import random

WIDTH = 480
HEIGHT = 600
FPS = 60

POWERUP_TIME = 5000

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

#initialization
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shoot!")
clock = pygame.time.Clock()

#import folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
snd_folder = os.path.join(game_folder, 'snd')

#import images
player_img = pygame.image.load(os.path.join(img_folder, 'player.png')).convert()
player_life = pygame.image.load(os.path.join(img_folder, 'life.png')).convert()
player_life_bu = pygame.transform.scale(player_life, (25, 19))
player_life_bu.set_colorkey(BLACK)
mob_img = pygame.image.load(os.path.join(img_folder, 'meteorSmall.png')).convert()
blt_img = pygame.image.load(os.path.join(img_folder, 'BLT.png')).convert()
bg_img = pygame.image.load(os.path.join(img_folder, 'bg5.png')).convert()
bg_rect = bg_img.get_rect()
mob_imgs = []

mob_lst = ['meteorSmall.png', 'meteorBrown_big4.png', 'meteorBrown_med1.png', 'meteorBrown_med3.png', 'meteorBrown_small1.png', 'meteorGrey_big3.png', 'meteorGrey_med1.png', 'meteorGrey_med2.png', 'meteorGrey_small1.png']

for img in mob_lst:
	mob_imgs.append(pygame.image.load(os.path.join(img_folder, img)).convert())

power_up_img = {}
power_up_img['shield'] = pygame.image.load(os.path.join(img_folder, 'shield.png')).convert()
power_up_img['bold'] = pygame.image.load(os.path.join(img_folder, 'bold.png')).convert()

#import animations
exp_anim = {}
exp_anim['lg'] = []
exp_anim['sm'] = []
exp_anim['player'] = []

for i in range(9):
	filename = 'regularExplosion0{}.png'.format(i)
	img = pygame.image.load(os.path.join(img_folder, filename)).convert()
	img.set_colorkey(BLACK)
	img_lg = pygame.transform.scale(img,(75,75))
	exp_anim['lg'].append(img_lg)
	img_sm = pygame.transform.scale(img, (32, 32))
	exp_anim['sm'].append(img_sm)
	filename = 'sonicExplosion0{}.png'.format(i)
	img = pygame.image.load(os.path.join(img_folder, filename)).convert()
	img.set_colorkey(BLACK)
	exp_anim['player'].append(img)

#sound & music
blt_snd = pygame.mixer.Sound(os.path.join(snd_folder, 'BLT.mp3'))
epxl_snd = []

for snd in ['expl3.wav', 'expl6.wav']:
	epxl_snd.append(pygame.mixer.Sound(os.path.join(snd_folder, snd)))

pygame.mixer.music.load(os.path.join(snd_folder, 'fon.mp3'))
pygame.mixer.music.set_volume(0.4)
pow_snd = pygame.mixer.Sound(os.path.join(snd_folder, 'FX062.mp3'))

#others
font_name = pygame.font.match_font('arial')

#functions
def draw_text(surf, text, size, x, y):
	font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, True, WHITE)
	text_rect = text_surface.get_rect()
	text_rect.midtop = (x, y)
	surf.blit(text_surface, text_rect)

def newmob():
	mob = Mob()
	all_sprites.add(mob)
	mobs.add(mob)


def draw_shield_bar(surf, x, y, pct):
	if pct < 0:
		pct = 0
	BAR_LENGHT = 100
	BAR_HEIGHT = 10
	fill = (pct / 100) * BAR_LENGHT
	outline_rect = pygame.Rect(x, y, BAR_LENGHT, BAR_HEIGHT)
	fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
	pygame.draw.rect(surf, GREEN, fill_rect)
	pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
	for i in range(lives):
		img_rect = img.get_rect()
		img_rect.x = x + 30 * i
		img_rect.y = y
		surf.blit(img, img_rect)

def show_go_screen():
	screen.blit(bg_img, bg_rect)
	draw_text(screen, 'Shoot!', 64, WIDTH / 2, HEIGHT / 4)
	draw_text(screen, 'Стрелочки двигаться, пробел стрелять, Q - выйти', 22, WIDTH / 2, HEIGHT / 2)
	draw_text(screen, 'Для начала нажмите любую кнопку', 18, WIDTH / 2, HEIGHT * 3 / 4 )
	pygame.display.flip()
	waiting = True
	while waiting:
		clock.tick(FPS)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
			if event.type == pygame.KEYUP:
				waiting = False



#classes
class Player(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.transform.scale(player_img,(50, 38))
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.radius = 20
		self.rect.centerx = WIDTH / 2
		self.rect.bottom = HEIGHT - 10
		self.speedx = 0
		self.speedy = 0
		self.shield = 100
		self.shot_delay = 250
		self.last_shot = pygame.time.get_ticks()
		self.lives = 3
		self.hidden = False
		self.hide_timer = pygame.time.get_ticks()
		self.power = 1
		self.power_time = pygame.time.get_ticks()

	def hide(self):
		self.hidden = True
		self.hide_timer = pygame.time.get_ticks()
		self.rect.center = (WIDTH / 2, HEIGHT + 200)

	def update(self):
		self.speedx = 0
		self.speedy = 0
		keystate = pygame.key.get_pressed()
		if keystate[pygame.K_LEFT]:
			self.speedx = -8
		if keystate[pygame.K_RIGHT]:
			self.speedx = 8
		if keystate[pygame.K_UP]:
			self.speedy = -8
		if keystate[pygame.K_DOWN]:
			self.speedy = 8
		if keystate[pygame.K_SPACE]:
			self.shot()
		self.rect.x += self.speedx
		self.rect.y += self.speedy
		if self.rect.right > WIDTH:
			self.rect.right = WIDTH
		if self.rect.left < 0:
			self.rect.left = 0
		if self.rect.top < 0:
			self.rect.top = 0
		if self.rect.bottom > HEIGHT:
			self.rect.bottom = HEIGHT
		if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
			self.hidden = False
			self.rect.centerx = WIDTH / 2
			self.rect.bottom = HEIGHT - 10
		if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
			self.power -= 1
			self.power_time = pygame.time.get_ticks()

	def shot(self):
		now = pygame.time.get_ticks()
		if now - self.last_shot > self.shot_delay:
			self.last_shot = now
			if self.power == 1:
				bullet = Bullet(self.rect.centerx, self.rect.top)
				all_sprites.add(bullet)
				bullets.add(bullet)
				blt_snd.play()
			if self.power >= 2:
				bullet1 = Bullet(self.rect.left, self.rect.centery)
				bullet2 = Bullet(self.rect.right, self.rect.centery)
				all_sprites.add(bullet1)
				all_sprites.add(bullet2)
				bullets.add(bullet1)
				bullets.add(bullet2)
				blt_snd.play()

	def powerup(self):
		self.power += 1
		self.power_time = pygame.time.get_ticks()

class Mob(pygame.sprite.Sprite):
	def __init__(self):
		pygame.sprite.Sprite.__init__(self)
		self.image_orig = random.choice(mob_imgs)
		self.image_orig.set_colorkey(BLACK)
		self.image = self.image_orig.copy()
		self.rect = self.image.get_rect()
		self.radius = int(self.rect.width * .85 / 2)
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.x = random.randrange(WIDTH - self.rect.width) 
		self.rect.y = random.randrange(-150, -100)
		self.speedy = random.randrange(1, 8)
		self.speedx = random.randrange(-3, 3)
		self.rot = 0
		self.rot_speed = random.randrange(-8, 8)
		self.last_update = pygame.time.get_ticks()

	def rotate(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > 50:
			self.last_update = now
			self.rot = (self.rot + self.rot_speed) % 360
			new_image = pygame.transform.rotate(self.image_orig, self.rot)
			old_center = self.rect.center
			self.image = new_image
			self.rect = self.image.get_rect()
			self.rect.center = old_center

	def update(self):
		self.rotate()
		self.rect.x += self.speedx
		self.rect.y += self.speedy
		if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
			self.rect.x = random.randrange(WIDTH - self.rect.width)
			self.rect.y = random.randrange(-100, -40)
			self.speedy = random.randrange(1, 8) 

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = blt_img
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		#self.radius = 5
		#pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
		self.rect.bottom = y
		self.rect.centerx = x
		self.speedy = -10

	def update(self):
		self.rect.y += self.speedy
		if self.rect.bottom < 0:
			self.kill()	
		
class Explosion(pygame.sprite.Sprite):
	def __init__(self, center, size):
		pygame.sprite.Sprite.__init__(self)
		self.size = size
		self.image = exp_anim[self.size][0]
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.frame = 0 
		self.last_update = pygame .time.get_ticks()
		self.frame_rate =50

	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(exp_anim[self.size]):
				self.kill()
			else:
				center = self.rect.center
				self.image = exp_anim[self.size][self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center

class Power(pygame.sprite.Sprite):
	"""docstring for Power"""
	def __init__(self, center):
		pygame.sprite.Sprite.__init__(self)
		self.type = random.choice(['shield','bold'])
		self.image = power_up_img[self.type]
		self.image.set_colorkey(BLACK)
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.speedy = 2

	def update(self):
		self.rect.y += self.speedy
		if self.rect.top > HEIGHT:
			self.kill()
		

pygame.mixer.music.play(loops=-1)
#game while
game_over = True
running = True
while running:
	if game_over:
		show_go_screen()
		game_over = False
		all_sprites = pygame.sprite.Group()
		mobs = pygame.sprite.Group()
		player = Player()
		all_sprites.add(player)
		bullets = pygame.sprite.Group()
		power_up = pygame.sprite.Group()
		for i in range(8):
			newmob()
		score = 0
	
	clock.tick(FPS)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	all_sprites.update()

	#BULLET AND MOB
	hits = pygame.sprite.groupcollide(mobs, bullets, True, True, pygame.sprite.collide_circle)
	for hit in hits:
		score += 100 - hit.radius
		random.choice(epxl_snd).play()
		expl = Explosion(hit.rect.center, 'lg')
		all_sprites.add(expl)
		if random.random() > 0.9:
			power = Power(hit.rect.center)
			all_sprites.add(power)
			power_up.add(power)
		newmob()

	#MOB AND PLAYER
	hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
	for hit in hits:
		player.shield -= hit.radius * 2
		expl = Explosion(hit.rect.center, 'sm')
		all_sprites.add(expl)
		random.choice(epxl_snd).play()
		newmob()
		if player.shield <= 0:
			deat_exp = Explosion(player.rect.center, 'player')
			all_sprites.add(deat_exp)
			player.hide()
			player.lives -= 1
			player.shield = 100
	if player.lives == 0 and not deat_exp.alive():
		running = False

	#PLAYER AND POWERUP
	hits = pygame.sprite.spritecollide(player, power_up, True)
	for hit in hits:
		if hit.type == 'shield':
			pow_snd.play()
			player.shield += random.randrange(10, 30)
			if player.shield >= 100:
				player.shield = 100
		if hit.type == 'bold':
			player.powerup()
			pow_snd.play()

	
	screen.fill(WHITE)
	screen.blit(bg_img, bg_rect)
	all_sprites.draw(screen)
	draw_text(screen, str(score), 18,WIDTH / 2, 10)
	draw_shield_bar(screen, 5, 5, player.shield)
	draw_lives(screen, WIDTH - 100, 5, player.lives, player_life_bu)
	pygame.display.flip()


pygame.quit()