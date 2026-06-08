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
- `host`: Host a room. The server returns `room_id` that is a 10 digit number and a list `pools` of available pools of boards to choose from. A single pool is an object with a string `id` and a `display_name`.
- `start_game`: Start the game in a room. Requires a `pool_id` of the chosen pool and integers `seed` (non-negative, up to 2^32) and `rounds` (between 1 and 50) that represent the chosen random seed and number of rounds, respectively. Accepts an optional `round_time` (positive integer, seconds); when set, the answering phase and each respondent's turn auto-advance when the time elapses (treated as the host ending the stage / respondent giving up). Omit or set to `null` for unlimited (manual-only) behaviour.
- `change_state`: Change the game state in the room you are a host of. Sends back an info to the host and the players or an error to the sender if the room doesn't exist or the sender isn't the host. Changing state means ending the time for player's responses, changing the player who shows their answer, advancing to the next round or returning to lobby after the game is finished.
- `skip_round`: Skip the current round. Can only be performed by the host when the players present their solutions. Otherwise sends back an error.
- `join`: Join a room. Requires appropriate `room_id` and `nickname`. Sends back an info to the host and the players or an error to the sender if the room doesn't exist. Sends back the `room_id` of the room.
- `answer`: Give the answer to a game round. Requires `answer` that is an integer. Sends back an error to the sender if they aren't taking a part in a game. Sending a non-positive value clears the answer. Sends back the saved `answer` to the sender and informs the host.
- `respond`: Give a step of your response. Takes `mole` and `direction`. `mole` is the index of the moving mole, i.e. index in the `mole_position` array (see [Board description](#board-description)). `direction` is one of the characters `U`, `R`, `D`, `L`. Sends back an error if the action is not permitted. Sends back the current `board`.
- `give_up`: Give up trying to prove your answer. Sends back an error if the action is not permitted. Sends back the current `board`.
- `revert`: Revert the previous step in your response. Sends back an error if the action is not permitted. Sends back the current `board`.
- `kick`: Kick the player with nickname `nickname` out of your room. The kicked player is fully disconnected (their connection is closed and their `user_id` invalidated) and their nickname is freed immediately, so it can be reused right away (including by the kicked player rejoining).
- `close`: Close the room you are the host of. Sends `room_destroyed` to the players in the room.

#### Training-types
Training mode is a single-player sandbox, completely independent of rooms: a user can practice sliding moles on a board on their own, without hosting, joining, bidding or opponents. It reuses the same board and movement rules as a real game. All training communication is request/response over the same `/ws` connection (the server replies directly to the sender; nothing is broadcast).
- `train_start`: Begin (or restart) a training session. Accepts an optional `pool_id` (defaults to the first catalog pool) and an optional `seed` (non-negative, up to 2^32; a random one is chosen when omitted). Returns a `success` of type `train_start` with the `board`, the chosen `pool_id` and `seed`, and the list of available `pools` (same shape as for `host`).
- `train_move`: Slide a mole. Takes `mole` (the index in `mole_position`) and `direction` (one of `U`, `R`, `D`, `L`), exactly like `respond`. Moves that change nothing (the mole is already against an obstacle) are ignored and do not increase the move counter. Returns a `success` of type `train_move` with the updated `board` (its `moves` field is the move counter) and a boolean `finished` that is `true` once the target has been reached. Sends back an error if the sender has no active training session.
- `train_reset`: Put every mole back to the board's starting layout and reset the move counter, keeping the same target so the same puzzle can be retried. Returns a `success` of type `train_reset` with the `board` and `finished` set to `false`. Sends back an error if the sender has no active training session.
- `train_new`: Hand the user a brand new board. Accepts an optional `pool_id` (defaults to the pool the user is already training on) and an optional `seed` (random when omitted). Returns a `success` of type `train_new` with the new `board`, `pool_id` and `seed`. Use this for the "give me another board" option once a puzzle is `finished`.
- `train_exit`: End the training session. Returns a `success` of type `train_exit`.

A training session is dropped automatically when the user's connection is permanently lost.

#### Server-types (messages)
- `player_disconnected`: A player has disconnected from your room. Sends their `nickname`. This gets sent to the other players and the host.
- `room_destroyed`: The host of your room disconnected or closed the room. This gets sent to the players.
- `game_start`: The round in your room was started. `board` is the current game board. This gets sent to the players and the host.
- `player_joined`: A player with the nickname `nickname` entered your room. This gets sent to the other players and the host.
- `game_end`: The game in your room ended. If you are the host, `ranking` is a sorted list of pairs `(points, nickname)`. You also get the `seed` and `pool_id` you provided in the lobby. If you are a player, `score` is your score and `position` if your position in the ranking (starting with `0`).
- `awaiting_response`: The game awaits a solution from the player with nickname `respondent` who claimed the best solution. This gets sent to the other players and the host.
- `respond`: You are the player who claimed the best solution. You are expected to provide the solution. `board` is the current board.
- `player_answered`: The player `nickname` gave answer `answer`. This gets sent to the host.
- `player_responded`: A step of the response was given by the appropriate player. `board` is the current board. This gets sent to the host.
- `player_gave_up`: The player giving the response gave up. `board` is the current board. This gets sent to the host.
- `player_reverted`: A step of the response was taken back. `board` is the current board. This gets sent to the host.
- `winner`: The player `nickname` won the round. If `nickname` is `null`, no player won. This gets sent to the other players and the host.
- `won`: You won the round.
- `kick`: You were kicked out of your room.
- `return_to_lobby`: The room returned to lobby after the game ended. This gets sent to both the host and the players.

### Board description
The board data is sent as a JSON dictionary that contains the following fields:
- `width [int]`: The width of the board.
- `height [int]`: The height of the board.
- `grid [list[list[Cell]]]`: The cells on the board. This is a two-dimensional list (indexed first by the vertical coordinate and then by the horizontal) of `Cells` - dictionaries with a four-element array `walls` of bools that denote whether the upper, right, lower, and left side of the cell contains a wall.
- `mole_position [list[Position]]`: The five-element list of the positions of the moles. The moles are always referred to by their index in this array. A single entry in this array is a dictionary with int fields `x` and `y` that denote respectively the horizontal and vertical coordinates of the field.
- `moves [int]`: Moves made so far by the player showing their solution.
- `finish [Position]`: The field where one is supposed to lead the mole in order to win. This a dictionary with int fields `x` and `y` that denote respectively the horizontal and vertical coordinates of the field.
- `finish_mole [int]`: The color of the mole that one is supposed to lead to `finish`. This is a mole index (one of `0,1,2,3,4`) or `-1` if `finish` is a multicolor target.

### Reconnection game state
The game state during reconnection can contain the following fields:
- `game_state`: The state of the current game. Can be `no_game` (no room), `awaiting_start` (room exists, game not started), `awaiting_answers` (round started, players are thinking), `settling_round` (players are providing their solutions) or `game_ended` (game ended). In case of `no_game` no other data is provided.
- `host`: Whether the user is a host.
- `room_id`: The room id. Provided when `host` is true.
- `nickname`: The nickname. Provided when `host` is false.
- `answer`: The current answer. Provided when `host` is false and `game_state` is `awaiting_answers` or `settling_round`. Can also be provided when `host` is true and `game_state` is `settling_round`. In this case this is the answer given by the player currently providing a solution.
- `respond`: Whether the user is expected to provide a solution. Provided when `host` is false and `game_state` is `settling_round`.
- `board` The state of the board. Provided when `respond` is true or `host` is true and `game_state` is `awaiting_answers` or `settling_round`.
- `respondent`: The nickname of the player currently providing a solution. Provided when `game_state` is `settling_round`.
- `ranking`: The sorted list of pairs `(points, nickname)` of all players. Provided when `host` is true and `game_state` is `game_ended`.
- `nicknames`: The nicknames of all the players. Provided when `host` is true and `game_state` is `awaiting_start`.
- `answers`: The list of pairs `(answer, nickname)` of all players. Provided when `host` is true and `game_state` is `awaiting_answers`.
- `score`: The player's score. Provided when `host` is false and `game_state` is `game_ended`.
- `position`: The player's position in the ranking (starting with `0`). Provided when `host` is false and `game_state` is `game_ended`.
