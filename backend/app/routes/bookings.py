from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.models.booking import Booking, BookingCreate, BookingListResponse, BookingUpdate
from app.services.booking_service import (
    create_public_booking,
    get_mock_booking_by_id,
    list_mock_bookings,
    update_mock_booking,
)

router = APIRouter()


@router.post("/bookings", response_model=Booking, status_code=status.HTTP_201_CREATED)
def submit_booking(booking_data: BookingCreate):
    return create_public_booking(booking_data)


@router.get("/bookings", response_model=BookingListResponse)
def get_bookings(
    status: Optional[str] = Query(default=None),
    assigned_person: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    # Temporary local testing endpoint.
    # Later this should become a protected admin route.
    return list_mock_bookings(
        status=status,
        assigned_person=assigned_person,
        search=search,
    )


@router.get("/bookings/{booking_id}", response_model=Booking)
def get_booking(booking_id: str):
    # Temporary local testing endpoint.
    # Later this should become a protected admin route.
    booking = get_mock_booking_by_id(booking_id)

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    return booking


@router.put("/bookings/{booking_id}", response_model=Booking)
def update_booking(booking_id: str, update_data: BookingUpdate):
    # Temporary local testing endpoint.
    # Later this should become a protected admin route.
    booking = update_mock_booking(booking_id=booking_id, update_data=update_data)

    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    return booking
