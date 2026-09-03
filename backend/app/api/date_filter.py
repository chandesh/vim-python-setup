"""Shared date-range filtering helpers for list/search endpoints."""
from datetime import date, datetime, time

from fastapi import HTTPException, status


def validate_date_range(date_from: date | None, date_to: date | None) -> None:
    """Raise 422 when the provided range is inverted."""
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_from must be on or before date_to",
        )


def apply_created_at_range(query, model, date_from: date | None, date_to: date | None):
    """Filter `model.created_at` to the inclusive day range [date_from, date_to].

    `date_from` matches from 00:00:00; `date_to` matches through 23:59:59.999.
    Naive datetimes are interpreted by Postgres in the session timezone (UTC).
    """
    if date_from:
        query = query.filter(model.created_at >= datetime.combine(date_from, time.min))
    if date_to:
        query = query.filter(model.created_at <= datetime.combine(date_to, time.max))
    return query