from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Response, status

from app.schemas import EventCreate, EventResponse, EventUpdate

router = APIRouter(prefix="/events", tags=["Events"])

# Temporary storage. PostgreSQL will replace this in Phase 2.
events: dict[UUID, EventResponse] = {}


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(payload: EventCreate) -> EventResponse:
    event = EventResponse(
        id=uuid4(),
        created_at=datetime.now(timezone.utc),
        **payload.model_dump(),
    )

    events[event.id] = event
    return event


@router.get("", response_model=list[EventResponse])
def list_events() -> list[EventResponse]:
    return list(events.values())


@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: UUID) -> EventResponse:
    event = events.get(event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


@router.patch("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: UUID,
    payload: EventUpdate,
) -> EventResponse:
    existing = events.get(event_id)

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    changes = payload.model_dump(exclude_unset=True)
    updated_data = existing.model_dump() | changes

    # Revalidate the complete event, including schedule consistency.
    event_fields = EventCreate.model_fields.keys()
    try:
      validated = EventCreate.model_validate(
        {
            field: updated_data[field]
            for field in event_fields
        }
    )
    except ValueError as exc:
      raise HTTPException(
        status_code=422,
        detail=str(exc),
    ) from exc

    updated = EventResponse(
        id=existing.id,
        created_at=existing.created_at,
        **validated.model_dump(),
    )

    events[event_id] = updated
    return updated


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(event_id: UUID) -> Response:
    if event_id not in events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    del events[event_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)