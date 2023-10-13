# CS Tron Light Cycle
A multiplayer Tron light cycle game implemented in Python, inspired by the classic arcade game Tron. Players control light cycles that leave a trail behind them. The objective is to avoid colliding with these trails while trying to make your opponents collide with them.

## Features
- Multiplayer Gameplay: Play with multiple players in real-time.
- Client-Server Architecture: Uses a client-server model to manage and synchronize game states.
- Dynamic Game Walls: Each player's movement creates walls in the game, making the gameplay challenging and exciting.
- Randomized Spawn Positions: Players are spawned at random positions on the game grid.

## Requirements
- Python 3.x
- Pygame

## Setup & Installation

1. Clone the repository:

```bash
git clone https://github.com/ZilbaM/cs-tron-light-cycle.git
cd cs-tron-light-cycle
```

2. Install the required packages:

```bash
pip install pygame
```

3. If you're planning to play with someone on another computer, you'll need to set up the server's IP address and port:

    - Open network.py.
    - Change the default argument of the Network class to the IPv4 address of the server (the computer where the server script will run).
    - Set the port number if it's different from the default.

4. Start the server:

```bash
python server.py
```

5. Start the client(s) in separate terminal windows:

```bash
python client.py
```

## Gameplay

1. Use arrow keys to control the direction of your light cycle.
2. Avoid colliding with the walls created by the movement of light cycles.
3. Try to make your opponents collide with the walls to eliminate them.
4. The last player remaining wins!

## Playing Over a Network
To play with someone on another computer:

1. Ensure both computers are connected to the same network.
2. The server should run the server.py script.
3. Clients should run the client.py script. Make sure the IP address and port in network.py on the client's side are set to the server's IPv4 address and port.

## Overview of the Code
### 1. _server.py_
This is the main server script responsible for managing the game state and handling player connections.

- __Game Class__: Represents the game state.
    - _player_connect_: Handles a new player connection, assigns a spawn position, and starts the player info loop.
    - _getPlayerIndex_: Finds the index of a player in the players list.
    - _player_info_loop_: Continuously receives player movement data, checks for collisions, and sends game state updates.
    - _getWalls_: Retrieves all the walls created by players.
    - _getSpawnPos_: Determines a random spawn position for a new player.

### 2. network.py
This script handles the networking aspect of the game, both for the server and the client.

- __Network Class__: Manages the socket connections and data transmission.
    - _serverBind_, _serverListen_, _serverAcceptClient_: Functions for the server to bind, listen, and accept client connections.
    - _clientConnect_: Allows the client to connect to the server.
    - _sendMessage_, _receiveMessage_: Send and receive data over the socket.
    - Encoding and decoding functions to convert game data to strings and vice versa.

### 3. client.py
This is the client script where players control their light cycles.

- __Game Class__: Represents the client-side game state.
    - _initPlayer_: Initializes the player with a spawn position.
    - _connectToServer_: Connects to the game server and initializes the player.
    - _gameLoop_: Main game loop where player input is processed, and game state updates are received.
    
- __User Class__: Represents every players in the game.
- __Player Class__: Represents the current player. Inherits from the User class and adds functionality for calculating next position, direction changes and walls.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.