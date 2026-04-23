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
uv run fastapi dev # runs the application in dev environment
```

## Usage
The app uses WebSockets for real-time client-server communication. The client sends JSON with the key `type` (see the list below) and other appropriate parameters. The server sends (back) JSON with the key `type` that can be `error`, `info` or `success`. In all cases the key `message` is specified to give more detailed information. In the case of an `error` `message` is just the error message. `success` is used to communicate a previously sent request has been processed. `info` is used to give asynchronous information about the game state. In both cases `message` is the type of information being passed to the client. In particular when the server responds to a request of a given type, it sends a `success` with `message` set to the type of the request in question. `info`'s and `success`'s can contain other keys, specific to their type.

All communication happens via the `/ws?user_id=<id>` endpoint. If `user_id` is not provided, the server creates a new user connection and returns a `user_id` (in a `success` of type `connect`). If `user_id` is provided, the server assumes user with this id wants to reconnect. If the id is invalid (e.g. the user disconnected more than 30 seconds ago) error 403 is returned. Otherwise a `success` of type `reconnect` is issued. The server also provides the user with their current [game state](#reconnection-game-state).

### List of types
#### Client-types
- `host`: Host a room. The server returns `room_id` that is a 10 digit number.
- `change_state`: Change the game state in the room you are a host of. Sends back an info to the host and the players or an error to the sender if the room doesn't exist or the sender isn't the host. Changing state means starting the game, ending the time for player's responses or changing the player who shows their answer.
- `skip_round`: Skip the current round. Can only be performed by the host when the players present their solutions. Otherwise sends back an error.
- `join`: Join a room. Requires appropriate `room_id` and `nickname`. Sends back an info to the host and the players or an error to the sender if the room doesn't exist. Sends back the `room_id` of the room.
- `answer`: Give the answer to a game round. Requires `answer` that is an integer. Sends back an error to the sender if they aren't taking a part in a game. Sending a non-positive value clears the answer. Sends back the saved `answer` to the sender and informs the host.
- `respond`: Give a step of your response. Takes `mole` and `direction` that are integers representing the move. Sends back an error if the action is not permitted. Sends back the current `board`.
- `give_up`: Give up trying to prove your answer. Sends back an error if the action is not permitted. Sends back the current `board`.
- `revert`: Revert the previous step in your response. Sends back an error if the action is not permitted. Sends back the current `board`.

#### Server-types (messages)
- `player_disconnected`: A player has disconnected from your room. Sends their `nickname`. This gets sent to the other players and the host.
- `room_destroyed`: The host of your room has disconnected. This gets sent to the players.
- `game_start`: The game in your room was started. `board` is the current game board. This gets sent to the players and the host.
- `player_joined`: A player with the nickname `nickname` entered your room. This gets sent to the other players and the host.
- `game_end`: The game in your room ended. This gets sent to the players and the host.
- `awaiting_response`: The game awaits a solution from the player with nickname `respondent` who claimed the best solution. This gets sent to the other players and the host.
- `respond`: You are the player who claimed the best solution. You are expected to provide the solution. `board` is the current board.
- `player_answered`: The player `nickname` gave answer `answer`. This gets sent to the host.
- `player_responded`: A step of the response was given by the appropriate player. `board` is the current board. This gets sent to the host.
- `player_gave_up`: The player giving the response gave up. `board` is the current board. This gets sent to the host.
- `player_reverted`: A step of the response was taken back. `board` is the current board. This gets sent to the host.
- `winner`: The player `nickname` won the round. This gets sent to the host.
- `won`: You won the round.

### Board description
TODO

### Reconnection game state
The game state during reconnection can contain the following fields.
- `game_state`: The state of the current game. Can be `no_game` (no room), `awaiting_start` (room exists, game not started), `awaiting_answers` (round started, players are thinking), `settling_round` (players are providing their solutions) or `game_end` (game ended). In case of `no_game` no other data is provided.
- `host`: Whether the user is a host.
- `room_id`: The room id. Provided when `host` is true.
- `nickname`: The nickname. Provided when `host` is false.
- `answer`: The current answer. Provided when `host` is false and `game_state` is `awaiting_answers` or `settling_round`. Can also be provided when `host` is true and `game_state` is `settling_round`. In this case this is the answer given by the player currently providing a solution.
- `respond`: Whether the user is expected to provide a solution. Provided when `host` is false and `game_state` is `settling_round`.
- `board` The state of the board. Provided when `respond` is true or `host` is true and `game_state` is `awaiting_answers` or `settling_round`.
- `respondent`: The nickname of the player currently providing a solution. Provided when `host` is true and `game_state` is `settling_round`.
