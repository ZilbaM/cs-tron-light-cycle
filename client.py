# Example file showing a circle moving on screen
import pygame
from network import Network, PlayerInfo
from random import randint

# pygame setup
pygame.init()
screenSize = (1280, 720)
screen = pygame.display.set_mode(screenSize)
clock = pygame.time.Clock()
running = True
player_size = 10
player_speed = 10
framerate = 60
movement_threshold = 1.0 / 10.0 # 10 move a second

class Game:
    def __init__(self, network : Network) -> None:
        self.opponents: [User]
        self.player: Player
        self.network = network
        self.opponentsColor = self.randomColor()
        self.dt = 0

    def initPlayer(self, spawnPos: pygame.Vector2):
        self.player = Player(spawnPos.x, spawnPos.y, self.randomColor())

    def connectToServer(self):
        if self.network.clientConnect():
            spawnPos = self.network.receiveMessage(self.network.socket)
            decodedSpawnPos = self.network.decodePos(spawnPos)
            self.initPlayer(decodedSpawnPos)

    def randomColor(self) -> pygame.Color:
        return pygame.Color(randint(100, 255), randint(100, 255), randint(100, 255))
    
    def updateOpponents(self, opponentsInfos: [PlayerInfo]):
        self.opponents = [User(opponent.playerPos.x, opponent.playerPos.y, self.opponentsColor) for opponent in opponentsInfos]

    def getSelfWalls(self) -> [pygame.Rect]:
        walls  = self.player.walls.copy()
        return walls

    def drawOpponents(self):
        for opponent in self.opponents:
            opponent.drawUser()
            opponent.drawWalls()

    def gameLoop(self):
        running = True
        while running:
            print('tick')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill("black")
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.player.changeDir(pygame.Vector2(0, -player_speed))
            elif keys[pygame.K_DOWN]:
                self.player.changeDir(pygame.Vector2(0, player_speed))
            if keys[pygame.K_LEFT]:
                self.player.changeDir(pygame.Vector2(-player_speed, 0))
            if keys[pygame.K_RIGHT]:
                self.player.changeDir(pygame.Vector2(player_speed, 0))
            self.player.move(self.dt)
            encoded = self.network.encodeClientInfo(PlayerInfo(self.player.pos, self.getSelfWalls()))
            print('send current position : ', self.player.pos, self.getSelfWalls())
            self.network.sendMessage(encoded, self.network.socket)
            received = self.network.receiveMessage(self.network.socket)
            print('received game message : ', received)
            if received == 'gameover':
                running = False
            else :
                otherPlayersInfo = self.network.decodeGameInfo(received)
                print('received game message : ', otherPlayersInfo)
                self.updateOpponents(otherPlayersInfo)
                self.drawOpponents()
                pygame.display.flip()
                self.dt = clock.tick(framerate) / 1000
                
            
        self.network.close()
        pygame.quit()

class User:
    def __init__(self, x: int, y: int, color: pygame.Color):
        self.pos = pygame.Vector2(x, y)
        self.color = color
        self.walls = []
        self.rect = pygame.Rect(self.pos.x, self.pos.y, player_size, player_size)
    
    def drawUser(self):
        pygame.draw.rect(screen, self.color, self.rect, 0)

    def drawWalls(self):
        for wall in self.walls or []:
            pygame.draw.rect(screen, self.color, wall, 0)
        if hasattr(self, "currentWall") and self.currentWall:
            pygame.draw.rect(screen, self.color, self.currentWall, 0)

    def updatePos(self, x: int, y: int):
        self.pos.x = x 
        self.pos.y = y

    def updateRect(self):
        self.rect = pygame.Rect(self.pos.x, self.pos.y, player_size, player_size)
        
    
class Player(User):
    def __init__(self, x: int, y: int, color: pygame.Color):
        super().__init__(x, y, color)
        self.acc = pygame.Vector2(player_speed, 0)
        self.accumulator = 0
        self.currentWall = pygame.Rect(self.pos.x, self.pos.y, player_size, player_size)

    def wrapPos(self):
        wrapX = self.pos.x%screenSize[0]
        wrapY = self.pos.y%screenSize[1]
        if wrapX!=self.pos.x or wrapY != self.pos.y:
            self.walls.append(self.currentWall.copy())
            self.currentWall = None
        self.pos.x = wrapX
        self.pos.y = wrapY

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
            self.accumulator -= movement_threshold
        self.drawUser()
        self.drawWalls()

network = Network()
game = Game(network)
game.connectToServer()
game.gameLoop()