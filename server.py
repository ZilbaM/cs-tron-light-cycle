import socket
import pygame
import threading
from network import Network, PlayerInfo
import random


lock = threading.Lock()
HOST = ''    # The remote host
PORT = 5007     # The same port as used by the server



class Game:
    def __init__(self) -> None:
        self.players: [PlayerInfo] = []
    
    def player_connect(self, playerSocket: socket.socket):
        spawnPos = self.getSpawnPos()
        player = PlayerInfo(spawnPos)
        playerInfoMessage = network.encodePos(spawnPos)
        lock.acquire()
        self.players.append(player)
        lock.release()
        network.sendMessage(playerInfoMessage, playerSocket)
        self.player_info_loop(player, playerSocket)

    def getPlayerIndex(self, playerInfo = PlayerInfo) -> int:
        for index, player in enumerate(self.players):
            if player.playerPos.x == playerInfo.playerPos.x and player.playerPos.y == playerInfo.playerPos.y:
                return index

    def player_info_loop(self, playerInfo: PlayerInfo, playerSocket : socket.socket):
        playerIndex: int
        while True:
            data = network.receiveMessage(playerSocket)
            if not data:
                print("Disconnected")
                break
            decoded = network.decodeClientInfo(data)
            collided = pygame.Rect(decoded.playerPos.x, decoded.playerPos.y, 10, 10).collidelist(self.getWalls(self.getPlayerIndex(playerInfo)))
            lock.acquire()
            if collided != -1:
                reply = 'gameover'
                self.players = self.players[:self.getPlayerIndex(playerInfo)] + self.players[self.getPlayerIndex(playerInfo)+1:]
            else :
                self.players[self.getPlayerIndex(playerInfo)] = decoded
                playerInfo = decoded
                reply = network.encodeGameInfo(self.players[:self.getPlayerIndex(playerInfo)] + self.players[(self.getPlayerIndex(playerInfo)+1):])
            lock.release()
            network.sendMessage(reply, playerSocket)
        playerSocket.close()

    def getWalls(self, playerIndex: int = None) -> [pygame.Rect]:
        walls = []
        for index, player in enumerate(self.players):
            walls += player.playerWalls
            if playerIndex != None and playerIndex==index:
                walls = walls[:-1]
        return walls

    def getSpawnPos(self):
        walls = self.getWalls()
        while True:
            randomPosX = random.randrange(start=1, stop=127, step=1) * 10
            randomPosY = random.randrange(start=1, stop=71, step=1) * 10
            randomSpawnRect = pygame.Rect(randomPosX, randomPosY, 10, 10)

            if randomSpawnRect.collidelist(walls) == -1:
                return pygame.Vector2(randomPosX, randomPosY)

network = Network()
network.serverBind()
network.serverListen()
game = Game()

while True:
    client, addr = network.serverAcceptClient()
    print('New connection : ', addr)
    thread = threading.Thread(target=game.player_connect, args=[client])
    thread.start()