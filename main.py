import pygame
import math
import os

# Initialize pygame
pygame.init()

# Get the screen info for mobile devices
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h - 50  # Account for navigation bar

clock = pygame.time.Clock()
fps = 60

# Load sounds
try:
    pygame.mixer.music.load('assets/sound/level_grzyby.mp3')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, 0.0, 5000)
    move_sound = pygame.mixer.Sound("assets/sound/jump.wav")
    shoot_sound = pygame.mixer.Sound("assets/sound/laser.wav")
except:
    print("Could not load sounds")

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("RBG Battler")

# Load images with error handling
def load_image(name):
    try:
        return pygame.image.load(name).convert_alpha()
    except:
        # Create a placeholder image if loading fails
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        color = (255, 0, 0) if "red" in name else (0, 0, 255) if "blue" in name else (100, 100, 100)
        pygame.draw.rect(surf, color, (0, 0, 50, 50))
        return surf

# Load images
background_img = load_image("assets/img/background image for android.png")
panel_img = load_image("assets/img/panel image for android.png")
icon = load_image("assets/img/the small game icon.png")
pygame.display.set_icon(icon)

health_red_full = load_image("assets/img/full health bar player one red.png")
p1_red = load_image("assets/img/player red one.png")
p2_blue = load_image("assets/img/player blue two.png")
health_blue_full = load_image("assets/img/health full bar blue player two.png")

# Create a simple bullet image if not available
bullet_img = pygame.Surface((8, 8), pygame.SRCALPHA)
pygame.draw.circle(bullet_img, (255, 255, 0), (4, 4), 4)

# Player class
class Player:
    def __init__(self, x, y, image, health_img, controls, color):
        self.x = x
        self.y = y
        self.image = image
        self.health_img = health_img
        self.controls = controls
        self.color = color
        self.width = image.get_width()
        self.height = image.get_height()
        self.vel_y = 0
        self.jumping = False
        self.flip = False
        self.health = 100
        self.shoot_cooldown = 0
        self.bullets = []
        
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        
        # Boundary checking
        if self.x < 0:
            self.x = 0
        if self.x > screen_width - self.width:
            self.x = screen_width - self.width
        if self.y < 0:
            self.y = 0
        if self.y > screen_height - 150 - self.height:
            self.y = screen_height - 150 - self.height
            self.vel_y = 0
            self.jumping = False
            
    def jump(self):
        if not self.jumping:
            self.vel_y = -15
            self.jumping = True
            try:
                move_sound.play()
            except:
                pass
            
    def shoot(self):
        if self.shoot_cooldown == 0:
            direction = -1 if self.flip else 1
            self.bullets.append(Bullet(self.x + self.width//2, self.y + self.height//2, direction, self.color))
            self.shoot_cooldown = 20
            try:
                shoot_sound.play()
            except:
                pass
            
    def update(self):
        # Apply gravity
        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10
        dy = self.vel_y
        
        # Move player
        self.move(0, dy)
        
        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.x < 0 or bullet.x > screen_width:
                self.bullets.remove(bullet)
                
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.x, self.y))
        
        # Draw health bars
        max_width = health_red_full.get_width() if self.color == "red" else health_blue_full.get_width()
        health_width = int(max_width * (self.health / 100))
        if health_width > 0:
            health_surface = pygame.Surface((health_width, 20))
            health_color = (255, 0, 0) if self.color == "red" else (0, 0, 255)
            health_surface.fill(health_color)
            screen.blit(health_surface, (50 if self.color == "red" else screen_width - 200, 20))
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw()

# Bullet class
class Bullet:
    def __init__(self, x, y, direction, color):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 10 * direction
        self.color = color
        self.image = bullet_img
        
    def update(self):
        self.x += self.speed
        
    def draw(self):
        screen.blit(self.image, (self.x, self.y))

# Touch control buttons
class Button:
    def __init__(self, x, y, width, height, color, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.action = action
        
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        font = pygame.font.SysFont(None, 24)
        text_surf = font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surf, (self.rect.x + self.rect.width//2 - text_surf.get_width()//2, 
                               self.rect.y + self.rect.height//2 - text_surf.get_height()//2))
        
    def is_pressed(self, pos):
        return self.rect.collidepoint(pos)

# Create players
player1 = Player(120, 260, p1_red, health_red_full, 
                {"up": pygame.K_w, "left": pygame.K_a, "right": pygame.K_d, "shoot": pygame.K_f}, 
                "red")
player2 = Player(screen_width - 200, 260, p2_blue, health_blue_full, 
                {"up": pygame.K_UP, "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "shoot": pygame.K_RCTRL}, 
                "blue")

# Create touch controls for mobile
buttons = [
    Button(50, screen_height - 100, 80, 80, (100, 100, 100, 150), "LEFT", "p1_left"),
    Button(140, screen_height - 100, 80, 80, (100, 100, 100, 150), "RIGHT", "p1_right"),
    Button(230, screen_height - 100, 80, 80, (100, 100, 100, 150), "JUMP", "p1_jump"),
    Button(320, screen_height - 100, 80, 80, (200, 0, 0, 150), "SHOOT", "p1_shoot"),
    
    Button(screen_width - 130, screen_height - 100, 80, 80, (100, 100, 100, 150), "LEFT", "p2_left"),
    Button(screen_width - 220, screen_height - 100, 80, 80, (100, 100, 100, 150), "RIGHT", "p2_right"),
    Button(screen_width - 310, screen_height - 100, 80, 80, (100, 100, 100, 150), "JUMP", "p2_jump"),
    Button(screen_width - 400, screen_height - 100, 80, 80, (0, 0, 200, 150), "SHOOT", "p2_shoot"),
]

def draw_bg():
    screen.blit(background_img, (0, 0))
    player1.draw()
    player2.draw()

def draw_panel():
    screen.blit(panel_img, (0, screen_height - 150))
    for button in buttons:
        button.draw()
    
def check_bullet_collisions():
    # Check player1's bullets hitting player2
    for bullet in player1.bullets[:]:
        if (bullet.x > player2.x and bullet.x < player2.x + player2.width and
            bullet.y > player2.y and bullet.y < player2.y + player2.height):
            player2.health -= 10
            player1.bullets.remove(bullet)
            
    # Check player2's bullets hitting player1
    for bullet in player2.bullets[:]:
        if (bullet.x > player1.x and bullet.x < player1.x + player1.width and
            bullet.y > player1.y and bullet.y < player1.y + player1.height):
            player1.health -= 10
            player2.bullets.remove(bullet)

# Game loop
run = True
while run:
    clock.tick(fps)
    
    # Draw background
    draw_bg()
    draw_panel()
    
    # Update players
    player1.update()
    player2.update()
    
    # Check for bullet collisions
    check_bullet_collisions()
    
    # Check for game over
    if player1.health <= 0 or player2.health <= 0:
        font = pygame.font.SysFont('Arial', 64)
        if player1.health <= 0 and player2.health <= 0:
            text = font.render("DRAW!", True, (255, 255, 255))
        elif player1.health <= 0:
            text = font.render("BLUE WINS!", True, (0, 0, 255))
        else:
            text = font.render("RED WINS!", True, (255, 0, 0))
        screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2 - text.get_height()//2))
        pygame.display.update()
        pygame.time.delay(3000)
        run = False
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
        # Handle touch events for mobile
        if event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            pos = (event.x * screen_width, event.y * screen_height) if hasattr(event, 'x') else event.pos
            
            for button in buttons:
                if button.is_pressed(pos):
                    if button.action == "p1_left":
                        player1.move(-5, 0)
                        player1.flip = True
                    elif button.action == "p1_right":
                        player1.move(5, 0)
                        player1.flip = False
                    elif button.action == "p1_jump":
                        player1.jump()
                    elif button.action == "p1_shoot":
                        player1.shoot()
                    elif button.action == "p2_left":
                        player2.move(-5, 0)
                        player2.flip = True
                    elif button.action == "p2_right":
                        player2.move(5, 0)
                        player2.flip = False
                    elif button.action == "p2_jump":
                        player2.jump()
                    elif button.action == "p2_shoot":
                        player2.shoot()
            
        if event.type == pygame.KEYDOWN:
            # Player 1 controls
            if event.key == player1.controls["up"]:
                player1.jump()
            if event.key == player1.controls["shoot"]:
                player1.shoot()
                
            # Player 2 controls
            if event.key == player2.controls["up"]:
                player2.jump()
            if event.key == player2.controls["shoot"]:
                player2.shoot()
    
    # Get key presses for continuous movement
    key = pygame.key.get_pressed()
    
    # Player 1 movement
    if key[player1.controls["left"]]:
        player1.move(-5, 0)
        player1.flip = True
    if key[player1.controls["right"]]:
        player1.move(5, 0)
        player1.flip = False
        
    # Player 2 movement
    if key[player2.controls["left"]]:
        player2.move(-5, 0)
        player2.flip = True
    if key[player2.controls["right"]]:
        player2.move(5, 0)
        player2.flip = False
    
    pygame.display.update()

pygame.quit()