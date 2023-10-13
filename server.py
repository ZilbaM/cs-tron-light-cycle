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

    def player_info_loop(self, playerInfo: PlayerInfo, playerSocket : socket.socket):
        playerIndex: int
        for index, player in enumerate(self.players):
            if player.playerPos.x == playerInfo.playerPos.x and player.playerPos.y == playerInfo.playerPos.y:
                playerIndex = index
        print('player index : ', playerIndex)
        while True:
            data = network.receiveMessage(playerSocket)
            if not data:
                print("Disconnected")
                break
            decoded = network.decodeClientInfo(data)
            print('player position', decoded.playerPos)
            print('game walls : ', self.getWalls())
            collided = pygame.Rect(decoded.playerPos.x, decoded.playerPos.y, 10, 10).collidelist(self.getWalls())
            lock.acquire()
            if collided != -1:
                print('gameover for player ', playerIndex)
                reply = 'gameover'
                self.players = self.players[:playerIndex] + self.players[playerIndex+1:]
            else :
                print('before changes')
                for player in self.players:
                    print(player.playerPos)
                self.players[playerIndex] = decoded
                print('after changes')
                for player in self.players:
                    print(player.playerPos)
                reply = network.encodeGameInfo(self.players[:playerIndex] + self.players[playerIndex+1:])
            lock.release()
            network.sendMessage(reply, playerSocket)
        print("Lost connection")
        playerSocket.close()

    def getWalls(self) -> [pygame.Rect]:
        walls = []
        for player in self.players:
            walls += player.playerWalls
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