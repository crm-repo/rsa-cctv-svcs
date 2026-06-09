from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.customer import Customer, CustomerListResponse
from app.services.customer_service import get_mock_customer_by_id, list_mock_customers

router = APIRouter()


@router.get("/customers", response_model=CustomerListResponse)
def get_customers(
    customer_status: Optional[str] = Query(default=None),
    customer_from: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    # Temporary local testing endpoint.
    # Later this should become a protected admin route.
    return list_mock_customers(
        customer_status=customer_status,
        customer_from=customer_from,
        search=search,
    )


@router.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str):
    # Temporary local testing endpoint.
    # Later this should become a protected admin route.
    customer = get_mock_customer_by_id(customer_id)

    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer
