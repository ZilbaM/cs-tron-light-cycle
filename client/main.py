# Example file showing a circle moving on screen
import pygame
import copy


# pygame setup
pygame.init()
screenSize = (1280, 720)
screen = pygame.display.set_mode(screenSize)
clock = pygame.time.Clock()
running = True
dt = 0
player_size = 10
player_speed = 10
framerate = 60
movement_threshold = 1.0 / 10.0 # 10 moves a second

class Player:
    def __init__(self, x: int, y: int, color : pygame.Color):
        self.pos = pygame.Vector2(x, y)
        self.color = color
        self.wallColor = pygame.Color(color.r, color.g, color.b, color.a-50 if color.a>50 else color.a)
        self.walls = []
        self.rect = pygame.Rect(self.pos.x, self.pos.y, player_size, player_size)
        self.acc = pygame.Vector2(player_speed, 0)
        self.accumulator = 0
        self.currentWall = pygame.Rect(self.pos.x, self.pos.y, player_size, player_size)

    def drawPlayer(self):
        pygame.draw.rect(screen, self.color, self.rect, 0)

    def drawWalls(self):
        for wall in self.walls or []:
            pygame.draw.rect(screen, self.wallColor, wall, 0)
        if self.currentWall:
            pygame.draw.rect(screen, self.wallColor, self.currentWall, 0)
            

    def updatePos(self, x: int, y: int):
        self.pos.x = x 
        self.pos.y = y

    def wrapPos(self):
        wrapX = self.pos.x%screenSize[0]
        wrapY = self.pos.y%screenSize[1]
        if wrapX!=self.pos.x or wrapY != self.pos.y:
            self.walls.append(self.currentWall.copy())
            self.currentWall = None
        self.pos.x = wrapX
        self.pos.y = wrapY

    def updateRect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, player_size, player_size)
    
    def changeDir(self, newAcc: pygame.Vector2):
        if (newAcc != -self.acc):
            self.acc = newAcc

    def newWall(self):
        self.walls.append(self.currentWall.copy())
        self.currentWall = pygame.Rect(self.pos.x, self.pos.y, player_size, player_size)

    def collide(self) -> bool :
        return self.rect.collidelist(self.walls) != -1
        
    
    def updateWall(self, playerCopy: pygame.Rect):
        if self.currentWall:
            updatedWall = pygame.Rect.union(self.currentWall, playerCopy)
        else:
            updatedWall = playerCopy
        if updatedWall.w > player_size and updatedWall.h > player_size:
            self.walls.append(self.currentWall.copy())
            self.currentWall = playerCopy
        else:
            self.currentWall = updatedWall

    def move(self, dt):
        self.accumulator += dt
        if self.accumulator >= movement_threshold:
            oldPos = self.rect.copy()
            self.updateWall(oldPos)
            self.updatePos(x=self.pos.x + self.acc[0], y= self.pos.y + self.acc[1])
            self.wrapPos()
            self.updateRect()
            if self.collide():
                return False
            self.accumulator -= movement_threshold
        self.drawPlayer()
        self.drawWalls()
        return True





selfPlayer = Player(0, 0, pygame.Color(255, 0, 0))

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        selfPlayer.changeDir(pygame.Vector2(0, -player_speed))
    elif keys[pygame.K_DOWN]:
        selfPlayer.changeDir(pygame.Vector2(0, player_speed))
    if keys[pygame.K_LEFT]:
        selfPlayer.changeDir(pygame.Vector2(-player_speed, 0))
    if keys[pygame.K_RIGHT]:
        selfPlayer.changeDir(pygame.Vector2(player_speed, 0))

    if not selfPlayer.move(dt):
        running = False
    

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(framerate) / 1000

pygame.quit()