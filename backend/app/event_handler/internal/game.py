from app.event_handler.router import internal_event
from app.event_handler.schemas.internal import WinnerAnnouncementEvent
from app.event_handler.schemas.protocol import EventHandlerProtocol


@internal_event("winner_announcement", WinnerAnnouncementEvent)
async def internal_winner_announcement(
    handler: EventHandlerProtocol, event: WinnerAnnouncementEvent
) -> None:
    await handler.con_manager.broadcast(
        event.notify,
        {
            "type": "info",
            "message": "winner_announcement",
            "nickname": event.nickname,
            "answer": str(event.answer),
        },
    )
