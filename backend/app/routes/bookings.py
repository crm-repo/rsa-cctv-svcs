from fastapi import APIRouter, status

from app.models.booking import Booking, BookingCreate
from app.services.booking_service import create_public_booking

router = APIRouter()


@router.post("/bookings", response_model=Booking, status_code=status.HTTP_201_CREATED)
def submit_booking(booking_data: BookingCreate):
    return create_public_booking(booking_data)