from app.database.base import SessionLocal
from app.schemas.api import TicketCreate
from app.services.ticket_service import create_ticket

SAMPLES = [
    TicketCreate(
        title="VPN connection fails",
        description="Remote user cannot establish the corporate VPN tunnel.",
        category="network",
        priority="high",
    ),
    TicketCreate(
        title="ERP password expired",
        description="Finance analyst needs ERP access restored.",
        category="erp",
        priority="medium",
    ),
    TicketCreate(
        title="Laptop overheating",
        description="Fan is loud and device shuts down under load.",
        category="hardware",
        priority="medium",
    ),
]
with SessionLocal() as db:
    for sample in SAMPLES:
        create_ticket(db, sample)
print(f"Seeded {len(SAMPLES)} tickets")
