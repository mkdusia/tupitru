from app.event_handler.router import internal_event
from app.event_handler.schemas.protocol import EventHandlerProtocol
from app.event_handler.schemas.internal import (
    AnswerEvent,
    AwaitingResponseEvent,
    GiveUpEvent,
    InternalGameEndEvent,
    RespondEvent,
    ResponseReceivedEvent,
    RevertEvent,
    WinnerEvent,
)


@internal_event("game_end", InternalGameEndEvent)
async def internal_game_end(handler: EventHandlerProtocol, event: InternalGameEndEvent) -> None:
    await handler.con_manager.broadcast(
        event.notify, {"type": "info", "message": "game_end", "ranking": event.ranking}
    )


@internal_event("awaiting_response", AwaitingResponseEvent)
async def awaiting_response_event(
    handler: EventHandlerProtocol, event: AwaitingResponseEvent
) -> None:
    await handler.con_manager.broadcast(
        event.notify,
        {"type": "info", "message": "awaiting_response", "respondent": event.respondent},
    )


@internal_event("respond", RespondEvent)
async def respond_event(handler: EventHandlerProtocol, event: RespondEvent) -> None:
    await handler.con_manager.send(
        event.notify, {"type": "info", "message": "respond", "board": event.board.model_dump()}
    )


@internal_event("answer", AnswerEvent)
async def handle_answer_saved(handler: EventHandlerProtocol, event: AnswerEvent) -> None:
    await handler.con_manager.broadcast(
        event.notify,
        {
            "type": "info",
            "message": "player_answered",
            "nickname": event.nickname,
            "answer": event.answer,
        },
    )
    await handler.con_manager.send(
        event.player_id, {"type": "success", "message": "answer", "answer": event.answer}
    )


@internal_event("response_received", ResponseReceivedEvent)
async def response_event(handler: EventHandlerProtocol, event: ResponseReceivedEvent) -> None:
    await handler.con_manager.broadcast(
        event.notify,
        {"type": "info", "message": "player_responded", "board": event.board.model_dump()},
    )
    await handler.con_manager.send(
        event.player_id,
        {"type": "success", "message": "respond", "board": event.board.model_dump()},
    )


@internal_event("give_up", GiveUpEvent)
async def give_up_event(handler: EventHandlerProtocol, event: GiveUpEvent) -> None:
    await handler.con_manager.broadcast(
        event.notify,
        {"type": "info", "message": "player_gave_up", "board": event.board.model_dump()},
    )
    await handler.con_manager.send(
        event.player_id,
        {"type": "success", "message": "give_up", "board": event.board.model_dump()},
    )


@internal_event("revert", RevertEvent)
async def revert_event(handler: EventHandlerProtocol, event: RevertEvent) -> None:
    await handler.con_manager.broadcast(
        event.notify,
        {"type": "info", "message": "player_reverted", "board": event.board.model_dump()},
    )
    await handler.con_manager.send(
        event.player_id, {"type": "success", "message": "revert", "board": event.board.model_dump()}
    )


@internal_event("announce_winner", WinnerEvent)
async def winner_event(handler: EventHandlerProtocol, event: WinnerEvent) -> None:
    await handler.con_manager.broadcast(
        event.notify, {"type": "info", "message": "winner", "nickname": event.nickname}
    )
    await handler.con_manager.send(event.player_id, {"type": "info", "message": "won"})
