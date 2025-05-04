# app/tools/reservations.py
"""
Reservation tools for the Voice AI Restaurant Agent.

This module provides functions to manage reservations.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import Reservation, RestaurantTable, ReservationStatus
from database.repository import ReservationRepository, RestaurantTableRepository

def check_reservation_availability(
    db: Session, date: str, time: str, party_size: int
) -> Dict[str, Any]:
    """
    Check if there is availability for a reservation.
    
    Args:
        db: Database session
        date: Reservation date (YYYY-MM-DD)
        time: Reservation time (HH:MM)
        party_size: Party size
        
    Returns:
        Availability information
    """
    # Parse date and time
    try:
        year, month, day = date.split("-")
        hour, minute = time.split(":")
        reservation_date = datetime(int(year), int(month), int(day), int(hour), int(minute))
    except ValueError:
        return {
            "available": False,
            "error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."
        }
    
    # Check if the reservation is in the future
    now = datetime.now()
    if reservation_date < now:
        return {
            "available": False,
            "error": "Reservation must be in the future."
        }
    
    # Check if the restaurant is open at the requested time
    # Assuming the restaurant is open from 11:00 to 22:00
    opening_hour = 11
    closing_hour = 22
    if reservation_date.hour < opening_hour or reservation_date.hour >= closing_hour:
        return {
            "available": False,
            "error": f"The restaurant is only open from {opening_hour}:00 to {closing_hour}:00."
        }
    
    # Check availability
    repo = ReservationRepository(db)
    available = repo.check_availability(reservation_date, party_size)
    
    if not available:
        # Find alternative times
        alternatives = []
        for hour_offset in [-1, 1, -2, 2]:
            alt_time = reservation_date + timedelta(hours=hour_offset)
            if opening_hour <= alt_time.hour < closing_hour and repo.check_availability(alt_time, party_size):
                alternatives.append(alt_time.strftime("%Y-%m-%d %H:%M"))
        
        return {
            "available": False,
            "error": "No availability for the requested time and party size.",
            "alternatives": alternatives
        }
    
    # Get available tables
    table_repo = RestaurantTableRepository(db)
    available_tables = table_repo.get_available_tables(reservation_date, party_size)
    
    return {
        "available": True,
        "date": reservation_date.strftime("%Y-%m-%d"),
        "time": reservation_date.strftime("%H:%M"),
        "party_size": party_size,
        "available_tables": [
            {
                "id": table.id,
                "table_number": table.table_number,
                "capacity": table.capacity,
                "location": table.location
            }
            for table in available_tables
        ]
    }

def create_reservation(
    db: Session,
    date: str,
    time: str,
    party_size: int,
    customer_name: str,
    customer_phone: str,
    customer_email: Optional[str] = None,
    special_requests: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new reservation.
    
    Args:
        db: Database session
        date: Reservation date (YYYY-MM-DD)
        time: Reservation time (HH:MM)
        party_size: Party size
        customer_name: Customer name
        customer_phone: Customer phone
        customer_email: Customer email (optional)
        special_requests: Special requests (optional)
        
    Returns:
        Reservation information
    """
    # Parse date and time
    try:
        year, month, day = date.split("-")
        hour, minute = time.split(":")
        reservation_date = datetime(int(year), int(month), int(day), int(hour), int(minute))
    except ValueError:
        return {
            "success": False,
            "error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."
        }
    
    # Check availability
    availability = check_reservation_availability(db, date, time, party_size)
    if not availability["available"]:
        return {
            "success": False,
            "error": availability.get("error", "No availability for the requested time and party size."),
            "alternatives": availability.get("alternatives", [])
        }
    
    # Create reservation
    reservation_repo = ReservationRepository(db)
    reservation = reservation_repo.create(
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        party_size=party_size,
        reservation_date=reservation_date,
        special_requests=special_requests,
        status=ReservationStatus.CONFIRMED
    )
    
    # Assign tables
    table_repo = RestaurantTableRepository(db)
    available_tables = table_repo.get_available_tables(reservation_date, party_size)
    
    # Assign appropriate tables
    assigned_tables = []
    remaining_capacity = party_size
    
    for table in sorted(available_tables, key=lambda t: t.capacity):
        if remaining_capacity <= 0:
            break
        
        assigned_tables.append(table)
        remaining_capacity -= table.capacity
    
    # Update reservation with assigned tables
    reservation.tables = assigned_tables
    db.commit()
    
    return {
        "success": True,
        "reservation_id": reservation.id,
        "customer_name": reservation.customer_name,
        "date": reservation.reservation_date.strftime("%Y-%m-%d"),
        "time": reservation.reservation_date.strftime("%H:%M"),
        "party_size": reservation.party_size,
        "tables": [
            {
                "table_number": table.table_number,
                "capacity": table.capacity,
                "location": table.location
            }
            for table in reservation.tables
        ],
        "status": reservation.status.value
    }
    
def get_upcoming_reservations(db: Session, customer_phone: str) -> List[Dict[str, Any]]:
    """
    Get upcoming reservations for a customer.
    
    Args:
        db: Database session
        customer_phone: Customer phone number
        
    Returns:
        List of upcoming reservations
    """
    repo = ReservationRepository(db)
    reservations = repo.get_by_phone(customer_phone)
    
    now = datetime.now()
    upcoming_reservations = [
        r for r in reservations
        if r.reservation_date > now and r.status == ReservationStatus.CONFIRMED
    ]
    
    return [
        {
            "id": r.id,
            "date": r.reservation_date.strftime("%Y-%m-%d"),
            "time": r.reservation_date.strftime("%H:%M"),
            "party_size": r.party_size,
            "special_requests": r.special_requests,
            "tables": [
                {
                    "table_number": table.table_number,
                    "location": table.location
                }
                for table in r.tables
            ]
        }
        for r in upcoming_reservations
    ]

def cancel_reservation(db: Session, reservation_id: int) -> Dict[str, Any]:
    """
    Cancel a reservation.
    
    Args:
        db: Database session
        reservation_id: Reservation ID
        
    Returns:
        Cancellation result
    """
    repo = ReservationRepository(db)
    reservation = repo.get_by_id(reservation_id)
    
    if not reservation:
        return {
            "success": False,
            "error": f"Reservation with ID {reservation_id} not found."
        }
    
    # Check if the reservation is already canceled
    if reservation.status == ReservationStatus.CANCELED:
        return {
            "success": False,
            "error": "Reservation is already canceled."
        }
    
    # Check if the reservation is in the past
    now = datetime.now()
    if reservation.reservation_date < now:
        return {
            "success": False,
            "error": "Cannot cancel a reservation that is in the past."
        }
    
    # Cancel the reservation
    reservation.cancel()
    db.commit()
    
    return {
        "success": True,
        "reservation_id": reservation.id,
        "customer_name": reservation.customer_name,
        "date": reservation.reservation_date.strftime("%Y-%m-%d"),
        "time": reservation.reservation_date.strftime("%H:%M"),
        "status": reservation.status.value
    }

def get_reservation_by_id(db: Session, reservation_id: int) -> Optional[Dict[str, Any]]:
    """
    Get details of a specific reservation.
    
    Args:
        db: Database session
        reservation_id: Reservation ID
        
    Returns:
        Reservation details or None if not found
    """
    repo = ReservationRepository(db)
    reservation = repo.get_by_id(reservation_id)
    
    if not reservation:
        return None
    
    return {
        "id": reservation.id,
        "customer_name": reservation.customer_name,
        "customer_phone": reservation.customer_phone,
        "customer_email": reservation.customer_email,
        "party_size": reservation.party_size,
        "date": reservation.reservation_date.strftime("%Y-%m-%d"),
        "time": reservation.reservation_date.strftime("%H:%M"),
        "special_requests": reservation.special_requests,
        "status": reservation.status.value,
        "tables": [
            {
                "id": table.id,
                "table_number": table.table_number,
                "capacity": table.capacity,
                "location": table.location
            }
            for table in reservation.tables
        ],
        "created_at": reservation.created_at.isoformat(),
        "updated_at": reservation.updated_at.isoformat()
    }