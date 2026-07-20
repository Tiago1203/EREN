"""
Support Module

Enterprise support and SLA management.
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum


class SupportTier(str, Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Severity(str, Enum):
    CRITICAL = "critical"  # System down
    HIGH = "high"          # Major feature broken
    MEDIUM = "medium"      # Feature degraded
    LOW = "low"            # Minor issue


class SLADefinition(BaseModel):
    """SLA definition."""
    tier: SupportTier
    severity: Severity
    response_time: timedelta
    resolution_time: timedelta
    availability: float  # Percentage
    support_channels: List[str]


class SupportTicket(BaseModel):
    """Support ticket."""
    id: str
    customer_id: str
    tier: SupportTier
    severity: Severity
    subject: str
    description: str
    status: str = "open"
    created_at: datetime
    response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


class EscalationLevel(BaseModel):
    """Escalation level."""
    level: int
    role: str
    response_time: timedelta


class EscalationMatrix:
    """Support escalation matrix."""
    
    MATRIX = {
        SupportTier.COMMUNITY: [
            EscalationLevel(level=1, role="Community Forum", response_time=timedelta(days=7)),
        ],
        SupportTier.PROFESSIONAL: [
            EscalationLevel(level=1, role="Email Support", response_time=timedelta(hours=24)),
            EscalationLevel(level=2, role="Senior Support", response_time=timedelta(days=3)),
        ],
        SupportTier.ENTERPRISE: [
            EscalationLevel(level=1, role="Dedicated Support", response_time=timedelta(hours=4)),
            EscalationLevel(level=2, role="Engineering Team", response_time=timedelta(hours=8)),
            EscalationLevel(level=3, role="CTO/VP", response_time=timedelta(hours=24)),
        ],
    }
    
    @classmethod
    def get_escalation_path(cls, tier: SupportTier) -> List[EscalationLevel]:
        """Get escalation path for tier."""
        return cls.MATRIX.get(tier, [])


class SLAManager:
    """Manages SLAs."""
    
    SLAS = {
        (SupportTier.PROFESSIONAL, Severity.CRITICAL): SLADefinition(
            tier=SupportTier.PROFESSIONAL,
            severity=Severity.CRITICAL,
            response_time=timedelta(hours=24),
            resolution_time=timedelta(days=5),
            availability=0.99,
            support_channels=["email"]
        ),
        (SupportTier.PROFESSIONAL, Severity.HIGH): SLADefinition(
            tier=SupportTier.PROFESSIONAL,
            severity=Severity.HIGH,
            response_time=timedelta(days=2),
            resolution_time=timedelta(days=10),
            availability=0.99,
            support_channels=["email"]
        ),
        (SupportTier.ENTERPRISE, Severity.CRITICAL): SLADefinition(
            tier=SupportTier.ENTERPRISE,
            severity=Severity.CRITICAL,
            response_time=timedelta(hours=4),
            resolution_time=timedelta(hours=24),
            availability=0.999,
            support_channels=["phone", "email", "slack"]
        ),
        (SupportTier.ENTERPRISE, Severity.HIGH): SLADefinition(
            tier=SupportTier.ENTERPRISE,
            severity=Severity.HIGH,
            response_time=timedelta(hours=8),
            resolution_time=timedelta(days=3),
            availability=0.999,
            support_channels=["phone", "email"]
        ),
        (SupportTier.ENTERPRISE, Severity.MEDIUM): SLADefinition(
            tier=SupportTier.ENTERPRISE,
            severity=Severity.MEDIUM,
            response_time=timedelta(days=1),
            resolution_time=timedelta(days=7),
            availability=0.999,
            support_channels=["email", "slack"]
        ),
        (SupportTier.ENTERPRISE, Severity.LOW): SLADefinition(
            tier=SupportTier.ENTERPRISE,
            severity=Severity.LOW,
            response_time=timedelta(days=3),
            resolution_time=timedelta(days=14),
            availability=0.999,
            support_channels=["email"]
        ),
    }
    
    def get_sla(self, tier: SupportTier, severity: Severity) -> SLADefinition:
        """Get SLA for tier and severity."""
        return self.SLAS.get((tier, severity))
    
    def check_sla_compliance(self, ticket: SupportTicket, sla: SLADefinition) -> Dict[str, Any]:
        """Check SLA compliance."""
        now = datetime.utcnow()
        
        response_time_met = (
            ticket.response_at and 
            ticket.response_at - ticket.created_at <= sla.response_time
        )
        
        resolution_time_met = (
            ticket.resolved_at and
            ticket.resolved_at - ticket.created_at <= sla.resolution_time
        )
        
        return {
            "response_time_met": response_time_met,
            "resolution_time_met": resolution_time_met,
            "compliant": response_time_met and resolution_time_met,
        }


class SupportManager:
    """Manages support operations."""
    
    def __init__(self):
        self.tickets: Dict[str, SupportTicket] = {}
        self.sla_manager = SLAManager()
        self.escalation_matrix = EscalationMatrix()
    
    async def create_ticket(
        self,
        customer_id: str,
        tier: SupportTier,
        severity: Severity,
        subject: str,
        description: str
    ) -> SupportTicket:
        """Create support ticket."""
        ticket = SupportTicket(
            id=f"TICKET-{datetime.utcnow().timestamp()}",
            customer_id=customer_id,
            tier=tier,
            severity=severity,
            subject=subject,
            description=description,
            created_at=datetime.utcnow()
        )
        self.tickets[ticket.id] = ticket
        return ticket
    
    async def respond_to_ticket(self, ticket_id: str) -> bool:
        """Record ticket response."""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        
        ticket.response_at = datetime.utcnow()
        return True
    
    async def resolve_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Resolve ticket."""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return {"success": False}
        
        ticket.resolved_at = datetime.utcnow()
        ticket.status = "resolved"
        
        sla = self.sla_manager.get_sla(ticket.tier, ticket.severity)
        compliance = self.sla_manager.check_sla_compliance(ticket, sla)
        
        return {
            "success": True,
            "ticket_id": ticket_id,
            "resolved_at": ticket.resolved_at,
            "sla_compliant": compliance["compliant"],
        }
    
    async def get_escalation_path(self, tier: SupportTier) -> List[Dict]:
        """Get escalation path."""
        path = self.escalation_matrix.get_escalation_path(tier)
        return [
            {
                "level": e.level,
                "role": e.role,
                "response_time": str(e.response_time),
            }
            for e in path
        ]
