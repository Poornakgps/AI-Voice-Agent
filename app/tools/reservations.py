from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import Reservation, RestaurantTable, ReservationStatus
from database.repository import ReservationRepository, RestaurantTableRepository

def _parse_datetime(date: str, time: str) -> Optional[datetime]:
    """Parse date and time strings into datetime object."""
    try:
        year, month, day = date.split("-")
        hour, minute = time.split(":")
        return datetime(int(year), int(month), int(day), int(hour), int(minute))
    except ValueError:
        return None

def check_reservation_availability(
    db: Session, date: str, time: str, party_size: int
) -> Dict[str, Any]:
    """Check if there is availability for a reservation."""
    reservation_date = _parse_datetime(date, time)
    if not reservation_date:
        return {
            "available": False,
            "error": "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time."
        }
    
    now = datetime.now()
    if reservation_date < now:
        return {"available": False, "error": "Reservation must be in the future."}
    
    # Restaurant hours check (11 AM to 10 PM)
    if reservation_date.hour < 11 or reservation_date.hour >= 22:
        return {
            "available": False,
            "error": "The restaurant is only open from 11:00 to 22:00."
        }
    
    repo = ReservationRepository(db)
    available = repo.check_availability(reservation_date, party_size)
    
    if not available:
        # Find alternative times
        alternatives = []
        for hour_offset in [-1, 1, -2, 2]:
            alt_time = reservation_date + timedelta(hours=hour_offset)
            if 11 <= alt_time.hour < 22 and repo.check_availability(alt_time, party_size):
                alternatives.append(alt_time.strftime("%Y-%m-%d %H:%M"))
        
        return {
            "available": False,
            "error": "No availability for the requested time and party size.",
            "alternatives": alternatives
        }
    
    table_repo = RestaurantTableRepository(db)
    available_tables = table_repo.get_available_tables(reservation_date, party_size)
    
    return {
        "available": True,
        "date": reservation_date.strftime("%Y-%m-%d"),
        "time": reservation_date.strftime("%H:%M"),
        "party_size": party_size,
        "available_tables": [
            {"id": table.id, "table_number": table.table_number, "capacity": table.capacity}
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
    """Create a new reservation."""
    reservation_date = _parse_datetime(date, time)
    if not reservation_date:
        return {"success": False, "error": "Invalid date or time format."}
    
    # Check availability
    availability = check_reservation_availability(db, date, time, party_size)
    if not availability["available"]:
        return {
            "success": False,
            "error": availability.get("error"),
            "alternatives": availability.get("alternatives", [])
        }
    
    # Create the reservation
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
    
    # Find optimal table assignment
    assigned_tables = []
    remaining_capacity = party_size
    
    for table in sorted(available_tables, key=lambda t: t.capacity):
        if remaining_capacity <= 0:
            break
        assigned_tables.append(table)
        remaining_capacity -= table.capacity
    
    reservation.tables = assigned_tables
    db.commit()
    
    return {
        "success": True,
        "reservation_id": reservation.id,
        "customer_name": reservation.customer_name,
        "date": reservation.reservation_date.strftime("%Y-%m-%d"),
        "time": reservation.reservation_date.strftime("%H:%M"),
        "party_size": reservation.party_size,
        "tables": [{"table_number": t.table_number, "capacity": t.capacity} for t in reservation.tables],
        "status": reservation.status.value
    }
    
def get_upcoming_reservations(db: Session, customer_phone: str) -> List[Dict[str, Any]]:
    """Get upcoming reservations for a customer."""
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
            "tables": [{"table_number": t.table_number} for t in r.tables]
        }
        for r in upcoming_reservations
    ]

def cancel_reservation(db: Session, reservation_id: int) -> Dict[str, Any]:
    """Cancel a reservation."""
    repo = ReservationRepository(db)
    reservation = repo.get_by_id(reservation_id)
    
    if not reservation:
        return {"success": False, "error": f"Reservation with ID {reservation_id} not found."}
    
    if reservation.status == ReservationStatus.CANCELED:
        return {"success": False, "error": "Reservation is already canceled."}
    
    if reservation.reservation_date < datetime.now():
        return {"success": False, "error": "Cannot cancel a past reservation."}
    
    reservation.cancel()
    db.commit()
    
    return {
        "success": True,
        "reservation_id": reservation.id,
        "status": reservation.status.value
    }