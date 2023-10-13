import socket
from pygame import Rect, Vector2

SEPARATORS = {
    'WALLS' : '<W>',
    'PLAYER_INFO' : '<P>',
    'COORDINATES': '<C>',
    'DEFAULT' : '<S>'
}

class PlayerInfo:
    def __init__(self, playerPos: Vector2, playerWalls: [Rect] = []) -> None:
        self.playerPos = playerPos
        self.playerWalls = playerWalls

class Network:
    def __init__(self, HOST='', PORT=5007) -> None:
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = HOST
        self.port = PORT
        self.addr = (self.host, self.port)

    def serverBind(self) -> bool:
        try:
            self.socket.bind(self.addr)
            return True
        except socket.error as e:
            print(f"Server bind failed: {e}")
            return False
    
    def serverListen(self):
        self.socket.listen()

    def serverAcceptClient(self):
        client, address = self.socket.accept()
        return client, address
    
    def clientConnect(self) -> bool:
        try:
            self.socket.connect(self.addr)
            return True
        except socket.error as e:
            print(f"Client connection failed: {e}")
            return False
    
    def sendMessage(self, message: str, contactSocket: socket.socket) -> None:
        message_length = len(message)
        contactSocket.send(message_length.to_bytes(4, byteorder='big'))
        contactSocket.send(message.encode(encoding="utf-8"))
    
    def receiveMessage(self, contactSocket: socket.socket) -> str:
        length_data = contactSocket.recv(4)
        message_length = int.from_bytes(length_data, byteorder='big')
        message = contactSocket.recv(message_length).decode('utf-8')
        return message

    def encodePos(self, pos: Vector2) -> str:
        return SEPARATORS["COORDINATES"].join([str(pos.x), str(pos.y)])
    
    def decodePos(self, pos: str) -> Vector2:
        x, y = [float(i) for i in pos.split(SEPARATORS["COORDINATES"])]
        return Vector2(x, y)
    
    def encodeWalls(self, walls: [Rect]) -> str:
        encode = SEPARATORS["WALLS"].join([f'{wall.x},{wall.y},{wall.w},{wall.h}' for wall in walls])
        return encode
    
    def decodeWalls(self, message: str) -> [Rect]:
        if message == '':
            return []
        decode = message.split(SEPARATORS["WALLS"])
        walls = []
        for mass in decode:
            x,y,w,h = [int(c) for c in mass.split(',')]
            walls.append(Rect(x,y,w,h))
        return walls
    
    def encodeClientInfo(self, playerInfos: PlayerInfo) -> str:
        return SEPARATORS['PLAYER_INFO'].join([self.encodePos(playerInfos.playerPos), self.encodeWalls(playerInfos.playerWalls)])

    def decodeClientInfo(self, message: str) -> PlayerInfo:
        playerPos, playerWalls = message.split(SEPARATORS["PLAYER_INFO"])
        return PlayerInfo(self.decodePos(playerPos), self.decodeWalls(playerWalls))
    
    def encodeGameInfo(self, playersInfos: [PlayerInfo]) -> str:
        return SEPARATORS["DEFAULT"].join([self.encodeClientInfo(player) for player in playersInfos])
    
    def decodeGameInfo(self, message: str) -> [PlayerInfo]:
        if message == '':
            return []
        return [self.decodeClientInfo(playerMessage) for playerMessage in message.split(SEPARATORS["DEFAULT"])]

    def close(self):
        self.socket.close()
   