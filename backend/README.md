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
- `change_state`: Change the game state in the room you are a host of. Sends back an info to the host and the players or an error to the sender if the room doesn't exist or the sender isn't the host. Changing state means starting the game, ending the time for player's responses or changing the player who shows their answer.
- `join`: Join a room. Requires appropriate `room_id` and `nickname`. Sends back an info to the host and the players or an error to the sender if the room doesn't exist.
- `answer`: Give the answer to a game round. Requires `answer` that is an integer. Sends back an error to the sender if they aren't taking a part in a game. Sending a non-positive value clears the answer. Sends back the saved answer to the sender and informs the host.
- `respond`: Give a step of your response. Takes `mole` and `direction` that are integers representing the move. Sends back an error if the action is not permitted.
- `give_up`: Give up trying to prove your answer. Sends back an error if the action is not permitted.
- `revert`: Revert the previous step in your response. Sends back an error if the action is not permitted.

#### Server-types (messages)
- `player_disconnected`: A player has disconnected from your room. Sends their `nickname`.
- `room_destroyed`: The host of your room has disconnected.
- `game_start`: The game in your room was started.
- `player_joined`: A player with the nickname `nickname` entered your room.
- `game_end`: The game in your room ended.
- `awaiting_response`: The game awaits a solution from the player who claimed the best solution.
- `respond`: You are the player who claimed the best solution. You are expected to provide the solution.
- `player_answered`: The player `nickname` gave answer `answer`.
- `response_received`: A step of the response was given by the appropriate player.
- `player_gave_up`: The player giving the response gave up.
- `player_reverted`: A step of the response was taken back.
