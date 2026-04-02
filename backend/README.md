# Tupitru backend
Written in Python with [FastAPI](https://fastapi.tiangolo.com/), using [uv](https://docs.astral.sh/uv/) as a package manager.

## Setup
Ensure you have `uv` installed and run the following.
```bash
uv sync # loads the dependencies from the uv.lock file and creates a virtual environment at .venv
```

After that you can use:
```bash
uv run mypy . # runs the typechecker mypy on the current directory
uv run ruff check # runs the ruff linter on the project
uv run ruff format # runs the ruff formatter
uv run pytest # runs the pytest testing suite
uv run fastapi dev # run the application in dev environment
```

## Usage
The app uses WebSockets for real-time client-server communication. The client sends JSON with the key `type` (see the list below) and other appropriate parameters. The server sends (back) JSON with the key `type` that can be `error`, `info` or `success`. In all cases the key `message` is specified to give more detailed information. In the case of an `error` `message` is just the error message. `success` is used to communicate a previously sent request has been processed. `info` is used to give asynchronous information about the game state. In both cases `message` is the type of information being passed to the client. In particular when the server responds to a request of a given type, it sends a `success` with `message` set to the type of the request in question. `info`'s and `success`'s can contain other keys, specific to their type.

### List of types
#### Client-types
- `host`: Host a room. The server returns `room_id` that is a 10 digit number.
- `game_start`: Start the game in a room. Requires appropriate `room_id`. Sends back an info to the host and the players or an error to the sender if the room doesn't exist, the sender isn't the host or the game has already started.
- `join`: Join a room. Requires appropriate `room_id` and `nickname`. Sends back an info to the host and the players or an error to the sender if the room doesn't exist.
- `answer`: Give the answer to a game instance. Requires `answer` that is an integer. Sends back an error to the sender if they aren't taking a part in a game. Sending a non-positive value clears the answer.
- `time_up`: Finish a round. Sends back an error to the sender if they aren't a host of an ongoing game.

#### Server-types (messages)
- `player_disconnected`: A player has disconnected from your room. Sends their `nickname`.
- `room_destroyed`: The host of your room has disconnected.
- `winner_announcement`: A winner of a round has been decided. Gets sent to the host and the winner, contains the `nickname` of the winner and their `answer`.
