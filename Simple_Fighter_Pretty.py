import pygame
import os
import random

pygame.mixer.pre_init(44100,-16,2,2048)
pygame.init()

screen = pygame.display.set_mode((640,480))
screenrect = screen.get_rect()

#all of our pictures we load in
try:
    fighter_spritesheet = pygame.image.load(os.path.join("fighter", "C_Idle_strip4.png"))
    walking_spritesheet = pygame.image.load(os.path.join("fighter", "C_Walk_Up_strip4.png"))
    walking_down_spritesheet = pygame.image.load(os.path.join("fighter", "C_Walk_Down_strip4.png"))

    fighter_knife_spritesheet = pygame.image.load(os.path.join("fighter", "C_Knife_Idle_strip4.png"))
    walking_knife_spritesheet = pygame.image.load(os.path.join("fighter", "C_Knife_Walk_strip4.png"))
    walking_down_knife_spritesheet = pygame.image.load(os.path.join("fighter", "C_Knife_Walk_Down_strip4.png"))

    enemy_spritesheet = pygame.image.load(os.path.join("fighter" , "enemy_set.png"))
    street_walk = pygame.image.load(os.path.join("fighter", "background_fighter.png"))
    start_screen = pygame.image.load(os.path.join("fighter", "Title_Screen_Sheet.png"))
except:
    raise( UserWarning, "no work")

#helper function to erase the part of the screen starting at x,y to x + width , y + height
def dirtyrect(x,y,w,h):
    dirtyrect = street_walk.subsurface((x, y, w, h))
    screen.blit(dirtyrect, (x, y))

#helper function that returns a surface with text
def write(msg="pygame is cool", colour=(0,0,0), fontsize=24):
    """returns a surface with text"""
    myfont = pygame.font.SysFont("None", fontsize)
    mytext = myfont.render(msg, True, colour)
    mytext = mytext.convert_alpha()
    return mytext
def endscreen(screen, score):

    screen.fill((255, 255, 255))
    screen.blit(start_screen, (0, 0))
    screen.blit(write("GAME OVER", fontsize=36), (15, 15))
    screen.blit(write("You lose"), (15, 60))
    screen.blit(write("Final score: "), (15,75))
    screen.blit(write(str(score)), (120,75))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()


def startscreen(screen):
    screen.fill((255,255,255))
    screen.blit(start_screen, (0,0))
    screen.blit(write("Mega Ultra Super Punching Man Instructions", fontsize=36), (15,15))
    screen.blit(write("Step one punch"), (15,60))
    screen.blit(write("Step two win"), (15,75))
    screen.blit(write("Click the left mouse button to start"), (15,105))

    screen.blit(write("Instructions"), (15, 150))
    screen.blit(write("Press Q to punch to the left"), (15, 165))
    screen.blit(write("Press E to punch to the right"), (15, 180))
    screen.blit(write("Enemies can drop items press space to pick up"), (15, 195))
    screen.blit(write("Healthpacks heal you"), (15, 210))
    screen.blit(write("Brown box makes you equip a knife"), (15, 225))
    screen.blit(write("The knife does double damage"), (15, 240))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
        if pygame.mouse.get_pressed()[0]:
            return





startscreen(screen)
#Constants
FPS = 60                        #max fps
clock = pygame.time.Clock()     #to track time
playtime = 0                    #amount of time played
interval = 0.15                 #how long to switch between the pictures for animation
cycle_time = 0                  #how long it has been since switching pictures
speed = 100                     #default speed for the fighter
mainloop = True                 #game loop
FRAGMENT_MAX_SPEED = 150
spawn_interval = 2
spawn_time     = 0
max_enemies_on_screen = 7
game_over = False
#




class Fighter(pygame.sprite.Sprite):
    
    punch_image = pygame.image.load(os.path.join("fighter", "C_Right_Punch.png"))
    punch_image = punch_image.convert_alpha()

    left_punch_image = pygame.image.load(os.path.join("fighter", "C_Left_Punch.png"))
    left_punch_image = left_punch_image.convert_alpha()

    punch_sound = pygame.mixer.Sound(os.path.join("fighter", "punch.wav"))
    idle_fighter = []
    walking_fighter = []
    walking_down_fighter = []

    idle_fighter_knife = []
    walking_fighter_knife = []
    walking_down_fighter_knife = []

    def __init__(self,screen):
        self.groups = fighter_group, all_group, people_group
        self._layer = 5
        pygame.sprite.Sprite.__init__(self, self.groups) #always need this for sprite class
        self.screen = screen
        self.screenrect = screen.get_rect()
        self.image = Fighter.idle_fighter[0]
        self.rect = self.image.get_rect()

        self.x = 0       #init position
        self.y = 300     #init position
        self.vx = 0      #init speed
        self.vy = 0      #init speed

        self.rect.x = self.x
        self.rect.y = self.y

        #healthbar
        self.max_hitpoints = 100
        self.hitpoints     = 100
        Hitpointbar(self)

        #for movement
        self.up = False
        self.right = False
        self.down = False
        self.left = False

        #for animation
        self.pic_number = 0

        #for punching
        self.punching = False
        self.punching_interval = .3
        self.punching_end_time = 0
        self.punching_start_time = 0

        self.game_over = False
        self.score = 0

        self.knife = False
        self.damage = 50

    # punches in front of the fighter will add collision eventually
    # have no idea how this works currently
    def punch(self,playtime,enemies,direction):
        #so when we punch we want to stop moving and delay any updating of our fighter
        elapsed_time = playtime  #this is so we can see the difference between our current time and our palytime
        self.punching_end_time = playtime + self.punching_interval
        self.punching_start_time = playtime
        self.punching = True


        if(direction):
            self.image = Fighter.punch_image
            self.rect = self.image.get_rect()
            self.rect.x = self.x
            self.rect.y = self.y
        else:
            self.image = Fighter.left_punch_image
            self.rect = self.image.get_rect()
            #the punch image is 12 pixels longer in width than the fighter image we want these 12 pixels
            #to be on the left side of the fighter so we move the rect over 12
            self.rect.x = self.x - 12
            self.rect.y = self.y

        milliseconds = clock.tick(FPS)
        curr_seconds = milliseconds / 1000.0



        crashgroup = pygame.sprite.spritecollide(self, enemy_group, False, pygame.sprite.collide_rect)
        enemies = []
        for enemy in crashgroup:
            enemy.hitpoints -= self.damage
            enemies.append(enemy)

        all_group.clear(screen, street_walk)
        all_group.update(curr_seconds)
        all_group.draw(screen)



        
    #this moves our fighter around
    def update(self, seconds):

        if self.knife:
            self.damage = 100
        #if our punching flag is true we don't do anything until we hit the punching_end_time
        #if we are past the punching_end_time we set the image and rect back to our idle_fighter
        if(self.punching):
            self.punching_start_time += seconds
            if not self.punching_start_time >= self.punching_end_time:
                return
            else:
                self.image = Fighter.idle_fighter[self.pic_number]
                self.rect = self.image.get_rect()
                self.rect.x = self.x
                self.rect.y = self.y

        self.vx = 0     # reset speed before we recalculate it
        self.vy = 0

        # we check and see what buttons are being pressed and determine the speed based on that
        if self.left:
            self.vx -= speed
        if self.right:
            self.vx += speed
        if self.up:
            self.vy -= speed
        if self.down:
            self.vy += speed

        # temp x and y so we can test and see if this new location is okay
        tempx = self.x + self.vx * seconds
        tempy = self.y + self.vy * seconds

        self.rect.x = tempx
        self.rect.y = tempy

        testcrash = pygame.sprite.spritecollide(self, enemy_group, False, pygame.sprite.collide_rect)

        # if testcrash has any elements our new location already has an enemy so we change back our variables and return
        if len(testcrash) > 0:
            self.rect.x = self.x
            self.rect.y = self.y
            return

        # if tempcrash is empty our new location is good so we change the location and make sure its inside the screen
        self.x = tempx
        self.y = tempy

        self.rect.x = round(self.x, 0)
        self.rect.y = round(self.y, 0)

        # this sets the bounds to make sure our fighter doesnt leave the screen
        if self.x < 0:
            self.x = 0
            self.vx = 0
        elif self.x + self.rect.width > self.screenrect.width:
            self.x = self.screenrect.width - self.rect.width
            self.vx = 0

        if self.y < 170:  # note this is 170 because the top 170 pixels of our background is the skyline
            self.y = 170
            self.vy = 0
        elif self.y + self.rect.height > self.screenrect.height:
            self.y = self.screenrect.height - self.rect.height
            self.vy = 0

        # we check the direction our fighter is moving and pick the correct animation based on that
        if (self.vy < 0 and self.vx >= 0)  or (self.vy > 0 and self.vx < 0):
            if not self.knife:
                self.image = Fighter.walking_down_fighter[self.pic_number]
            else:
                self.image = Fighter.walking_down_fighter_knife[self.pic_number]

        elif self.vx != 0 or self.vy != 0:
            if not self.knife:
                self.image = Fighter.walking_fighter[self.pic_number]
            else:
                self.image = Fighter.walking_fighter_knife[self.pic_number]

        else:
            if not self.knife:
                self.image = Fighter.idle_fighter[self.pic_number]
            else:
                self.image = Fighter.idle_fighter_knife[self.pic_number]

        if self.hitpoints <= 0:
            self.game_over = True


class Hitpointbar(pygame.sprite.Sprite):
    def __init__(self, fighter, ydistance = 10):
        self.groups = bar_group, all_group
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.owner = fighter
        self.height = 7
        self.color = (0,255,0)
        self.ydistance  = ydistance
        self.image = pygame.Surface((self.owner.rect.width, self.height))
        self.image.set_colorkey((0,0,0))
        pygame.draw.rect(self.image, self.color, (0,0,self.owner.rect.width, self.height), 1)
        self.rect = self.image.get_rect()
        self.oldpercent = 0


    def update(self, seconds):
        self.percent = self.owner.hitpoints / self.owner.max_hitpoints * 1.0
        if self.percent != self.oldpercent:
            pygame.draw.rect(self.image, (0,0,0), (1,1,self.owner.rect.width - 2,5))
            pygame.draw.rect(self.image, (0,255,0), (1,1, int(self.owner.rect.width * self.percent),5),0)
        self.oldpercent = self.percent
        # so to get our new x and y location we take the x location and add half the width and for the y we take the y
        # and subtract the ydistance(distance from fighter to healthbar)
        self.rect.centerx = self.owner.rect.x + self.owner.rect.width / 2
        self.rect.centery = self.owner.rect.y - self.ydistance

        if self.percent <= 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):

    idle_enemy = []

    enemies = {}  # a dictionary of all enemies
    number = 0
    waittime = 1.0

    def __init__(self,screen,fighter, bullet_pattern, x = 400, y = 300):
        self.groups = enemy_group, all_group, people_group
        self._layer = 4
        pygame.sprite.Sprite.__init__(self, self.groups) #always need this for sprite class

        self.screen = screen
        self.screenrect = screen.get_rect()
        self.image = Enemy.idle_enemy[0]
        self.rect = self.image.get_rect()
        self.pic_number = 0
        self.fighter = fighter

        #for spawning
        self.lifetime = 0
        self.waittime = Enemy.waittime
        self.spawning = True

        self.x = x  # init position will change later when many enemies are made
        self.y = y  # init position
        self.vx = random.randint(-speed,speed)  # init speed
        self.vy = random.randint(-speed,speed)  # init speed

        # how long before recalculating speed
        self.movement_time = 0
        self.movement_interval = 2 + random.randint(-1,1)

        self.rect.x = self.x
        self.rect.y = self.y

        # healthbar
        self.max_hitpoints = 100
        self.hitpoints = 100
        Hitpointbar(self)
        self.bullet_pattern = bullet_pattern

        # for tracking
        self.number = Enemy.number
        Enemy.number += 1
        Enemy.enemies[self.number] = self

        self.frags = 25

        #this spawns blue particles around our robot before it spawns
        for _ in range(8):
            Spawn_Fragment(self.x,self.y)

    def update(self, seconds):

        self.lifetime += seconds

        #if the lifetime is longer than the spawn time we set spawning to false and change back the rect location
        if self.lifetime > self.spawning and self.spawning:
            self.spawning = False
            self.rect.x = self.x
            self.rect.y = self.y

        #if spawning we just move it off screen temporarily
        if self.spawning:
            self.rect.x = -100
            self.rect.y = -100

        else:
            self.movement_time += seconds

            # movement_time tracks how long the enemy has had this movement
            # after movement_interval seconds get a new random speed and direction
            if self.movement_time > self.movement_interval:
                self.vx = random.randint(-speed, speed)
                self.vy = random.randint(-speed, speed)
                self.movement_time = 0
                #different enemies have a random shooting pattern to make things interesting
                if self.bullet_pattern == 0:
                    Bullet(self.fighter, self, -100, 0)
                    Bullet(self.fighter, self, 100, 0)
                elif self.bullet_pattern == 1:
                    Bullet(self.fighter, self, 0, -100)
                    Bullet(self.fighter, self, 0, 100)
                elif self.bullet_pattern == 2:
                    Bullet(self.fighter, self, -100, -100)
                    Bullet(self.fighter, self, 100, 100)
                elif self.bullet_pattern ==3:
                    Bullet(self.fighter, self, 100, -100)
                    Bullet(self.fighter, self, -100, 100)

            tempx = self.x + self.vx * seconds
            tempy = self.y + self.vy * seconds

            self.rect.x = tempx
            self.rect.y = tempy

            # gonna have to change this to all_group and make sure it isnt colliding with itself
            testcrash = pygame.sprite.spritecollide(self, people_group, False, pygame.sprite.collide_rect)

            # len of testcrash will always be at least 1 because the enemy collides with itself
            # since these aren't controlled by humans we can just have them swap directions
            # so if 2 enemys are about to collide they both just switch directions
            if len(testcrash) > 1:
                self.vx *= -1
                self.vy *= -1

            self.x = tempx
            self.y = tempy

            # this sets the bounds to make sure our fighter doesnt leave the screen
            if self.x < 0:
                self.x = 0
                self.vx *= -1
            elif self.x + self.rect.width > self.screenrect.width:
                self.x = self.screenrect.width - self.rect.width
                self.vx *= -1

            if self.y < 170:  # note this is 170 because the top 170 pixels of our background is the skyline
                self.y = 170
                self.vy *= -1
            elif self.y + self.rect.height > self.screenrect.height:
                self.y = self.screenrect.height - self.rect.height
                self.vy *= -1

            self.image = Enemy.idle_enemy[self.pic_number]

            self.rect.x = round(self.x, 0)
            self.rect.y = round(self.y, 0)

            if self.hitpoints <= 0:
                self.fighter.score += 1
                self.drops()
                self.kill()


    def kill(self):
        for _ in range(self.frags):
            Explosion_Fragment(self.x, self.y)
        pygame.sprite.Sprite.kill(self)

    def drops(self):
        #10% chance to drop a knife and 10% to drop a healthpack
        drop = random.randint(1,10)
        if drop == 1:
            Healthpack(self)
        elif drop == 2:
            Knifedrop(self)



class Fragment(pygame.sprite.Sprite):
    def __init__(self,x,y):
        self._layer = 8
        pygame.sprite.Sprite.__init__(self,self.groups)
        self.x = x
        self.y = y
        self.max_speed = FRAGMENT_MAX_SPEED

    def init2(self):
        self.image = pygame.Surface((10,10))
        self.image.set_colorkey((0,0,0,))
        pygame.draw.circle(self.image, self.color, (5,5), random.randint(2,5))
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.time = 0.0

    def update(self,seconds):
        self.time += seconds
        if self.time > self.lifetime:
            self.kill()
        self.x += self.dx * seconds
        self.y += self.dy * seconds
        self.rect.centerx = round(self.x, 0)
        self.rect.centery = round(self.y, 0)

class Explosion_Fragment(Fragment):

    def __init__(self,x,y):
        self.groups = all_group, explosion_group
        Fragment.__init__(self,x,y)

        self.color = (random.randint(25, 255), 0, 0)
        self.x = x
        self.y = y

        self.dx = random.randint(-self.max_speed, self.max_speed)
        self.dy = random.randint(-self.max_speed, self.max_speed)

        self.lifetime = 1 + random.random() * 3  # max 3 seconds
        self.init2()  # continue with generic Fragment class

class Spawn_Fragment(Fragment):

    def __init__(self,x,y):
        self.groups = all_group, spawn_group
        Fragment.__init__(self,x,y)

        self.color = (0,0, random.randint(25, 255))

        #which side of the enemy to spawn on
        self.side = random.randint(1,4)

        if self.side == 1:  # left side
            self.x = x - 20
            self.y = y+ random.randint(-5,5)
        elif self.side == 2:  # top
            self.x = x+ random.randint(-5,5)
            self.y = y - 20
        elif self.side == 3:  # right
            self.x = x + 20
            self.y = y+ random.randint(-5,5)
        else:  # bottom
            self.x = x+ random.randint(-5,5)
            self.y = y + 20

        self.dx = (x - self.x) * 1.0 / Enemy.waittime
        self.dy = (y - self.y) * 1.0 / Enemy.waittime
        self.lifetime = Enemy.waittime + random.random() * .5

        self.init2()


class Bullet(pygame.sprite.Sprite):

    def __init__(self,fighter,enemy,dx,dy):
        self.groups = all_group, bullet_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = enemy.x
        self.y = enemy.y

        self.lifetime = 3
        self.color = ((255,0,0))
        self.image = pygame.Surface((10,10))
        self.image.set_colorkey((0,0,0))
        pygame.draw.circle(self.image,self.color, (5,5), 5)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.time = 0

        #self.dx, self.dy = self.get_shooting_pattern()
        self.dx = dx
        self.dy = dy

    def update(self,seconds):
        self.time += seconds
        if self.time > self.lifetime:
            self.kill()
        self.x += self.dx * seconds
        self.y += self.dy * seconds
        self.rect.centerx = round(self.x, 0)
        self.rect.centery = round(self.y, 0)


class Drops(pygame.sprite.Sprite):
    def __init__(self,enemy):

        self.layer = 11
        pygame.sprite.Sprite.__init__(self, self.groups) #always need this for sprite class

        self.x = enemy.x
        self.y = enemy.y

    def init2(self):
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Healthpack(Drops):
    def __init__(self,enemy):
        self.groups = all_group, drop_group
        Drops.__init__(self,enemy)

        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 0, 0))
        # make a red cross for the health pack
        pygame.draw.line(self.image, (255, 0, 0), (10, 4), (10, 16), 4)
        pygame.draw.line(self.image, (255, 0, 0), (4, 10), (16, 10), 4)
        self.image = self.image.convert()
        self.type = 0 #0 for healthpack 1 for knife

        self.time = 0
        self.lifetime = 5

        self.init2()

    def update(self,seconds):
        self.time += seconds
        if self.time >= self.lifetime:
            self.kill()

class Knifedrop(Drops):
    def __init__(self,enemy):
        self.groups = all_group, drop_group
        Drops.__init__(self,enemy)

        self.image = pygame.Surface((20,20))
        self.image.fill((139,69,19))#brown
        self.image = self.image.convert()
        self.type = 1 #1 for knife 0 for healthpack

        self.init2()


background = pygame.Surface((screen.get_width(), screen.get_height()))
background.fill((255,255,255))
background = background.convert()
screen.blit(background, (0,0))

street_walk = street_walk.convert()
screen.blit(street_walk, (0,0))

temp_idle = []
temp_walking = []
temp_walking_down = []

temp_idle_knife = []
temp_walking_knife = []
temp_walking_down_knife = []

enemy_width, enemy_height = 24,30 #144,60 total size
#convert spritesheet to image array in fighter class
width, height = 32, 64
for i in range(4):
    temp_idle.append(fighter_spritesheet.subsurface(width * i, 0, width, height))
    temp_walking.append(walking_spritesheet.subsurface(width * i, 0, width, height))
    temp_walking_down.append(walking_down_spritesheet.subsurface(width * i, 0, width, height))

    temp_idle_knife.append(fighter_knife_spritesheet.subsurface(width * i, 0, width, height))
    temp_walking_knife.append(walking_knife_spritesheet.subsurface(width * i, 0, width, height))
    temp_walking_down_knife.append(walking_down_knife_spritesheet.subsurface(width * i, 0, width, height))

for i in range(4):
    temp_idle[i].set_colorkey((255, 255, 255))
    temp_idle[i] = temp_idle[i].convert_alpha()
    Fighter.idle_fighter.append(temp_idle[i])

    temp_walking[i].set_colorkey((255, 255, 255))
    temp_walking[i] = temp_walking[i].convert_alpha()
    Fighter.walking_fighter.append(temp_walking[i])

    temp_walking_down[i].set_colorkey((255, 255, 255))
    temp_walking_down[i] = temp_walking_down[i].convert_alpha()
    Fighter.walking_down_fighter.append(temp_walking_down[i])


    temp_idle_knife[i].set_colorkey((255, 255, 255))
    temp_idle_knife[i] = temp_idle_knife[i].convert_alpha()
    Fighter.idle_fighter_knife.append(temp_idle_knife[i])

    temp_walking_knife[i].set_colorkey((255, 255, 255))
    temp_walking_knife[i] = temp_walking_knife[i].convert_alpha()
    Fighter.walking_fighter_knife.append(temp_walking_knife[i])

    temp_walking_down_knife[i].set_colorkey((255, 255, 255))
    temp_walking_down_knife[i] = temp_walking_down_knife[i].convert_alpha()
    Fighter.walking_down_fighter_knife.append(temp_walking_down_knife[i])

for i in range(6):
    temp_enemy = enemy_spritesheet.subsurface(enemy_width * i, 30, enemy_width, enemy_height)
    temp_enemy.set_colorkey((255,255,255))
    temp_enemy = temp_enemy.convert_alpha()
    Enemy.idle_enemy.append(temp_enemy)

#pygame group setup
fighter_group = pygame.sprite.Group()
bar_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
people_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
spawn_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
drop_group = pygame.sprite.Group()
all_group = pygame.sprite.LayeredUpdates()

#create the fighter
fighter = Fighter(screen)

screen.blit(street_walk, (0,0))

end_score = 0
num_enemies = 1

while mainloop:

    if fighter.game_over:
        end_score = fighter.score
        mainloop = False
    milliseconds = clock.tick(FPS)
    seconds = milliseconds / 1000.0

    playtime += seconds
    cycle_time += seconds
    spawn_time += seconds

    #whenever you run out of enemies you spawn more and more each time until you reach the max amount of enemies
    if len(enemy_group) == 0:
        for i in range(num_enemies):
            firing_pattern = random.randint(0,3)
            Enemy(screen, fighter, firing_pattern, 250 + i * 40, 200 + i * 40)
        if num_enemies < max_enemies_on_screen:
            num_enemies += 2


    pygame.display.set_caption("FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
        clock.get_fps(), " " * 5, playtime))


    #every .15 seconds we update what buttons are being pressed and continue or animation
    if cycle_time > interval:
        fighter.up = pygame.key.get_pressed()[pygame.K_UP]
        fighter.down = pygame.key.get_pressed()[pygame.K_DOWN]
        fighter.left = pygame.key.get_pressed()[pygame.K_LEFT]
        fighter.right = pygame.key.get_pressed()[pygame.K_RIGHT]

        fighter.pic_number += 1
        if fighter.pic_number > 3:
            fighter.pic_number = 0
        cycle_time = 0

        for i in range(len(Enemy.enemies)):
            Enemy.enemies[i].pic_number += 1
            if Enemy.enemies[i].pic_number > 3:
                Enemy.enemies[i].pic_number = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end_score = fighter.score
            mainloop = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                end_score = fighter.score
                mainloop = False
            elif event.key == pygame.K_e:
                fighter.punch(playtime,enemy_group,True)
            elif event.key == pygame.K_q:
                fighter.punch(playtime,enemy_group,False)


    hitbybullet = pygame.sprite.spritecollide(fighter, bullet_group, False, pygame.sprite.collide_rect)
    for bullet in hitbybullet:
        fighter.hitpoints -= 20
        bullet.kill()

    hitbydrop = pygame.sprite.spritecollide(fighter, drop_group, False, pygame.sprite.collide_rect)
    for drop in hitbydrop:
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            if drop.type == 0:
                fighter.hitpoints += 50
                drop.kill()
            elif drop.type == 1:
                fighter.knife = True
                drop.kill()


    #clear everything update it and redraw it
    all_group.clear(screen, street_walk)
    all_group.update(seconds)
    all_group.draw(screen)

    pygame.display.flip()

endscreen(screen,end_score)