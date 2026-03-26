# Tupitru backend
Written in Python with FastAPI.

## Setup
```bash
python3 -m venv .venv # create the virtual environment
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.tex
fastapi dev
```

## Usage
The app uses WebSockets for real-time client-server communication. The client sends JSON with the key `type` (see the list below) and other appropriate parameters. The server sends (back) JSON with the key `type` that can be either `error` or `info`. In both cases the key `message` is specified to give more detailed information. In the case of an `error` `message` is just the error message. For `info` `message` is the type of information being passed to the client. In particular when the server responds to a request of a given type, it sends an `info` with `message` set to the type of the request in question. `info`'s can contain other keys, specific to their type.

### List of types
#### Client-types
- `host`: Host a room. The server returns `room_id` that is a 10 digit number.
- `game_start`: Start the game in a room. Requires appropriate `room_id`. Sends back an info to the host and the players.
