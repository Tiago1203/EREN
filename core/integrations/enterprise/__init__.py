"""Enterprise System Adapters - ServiceNow, SAP, Maximo, Azure AD."""
from dataclasses import dataclass
from enum import Enum


class EnterpriseSystem(str, Enum):
    SERVICENOW = "servicenow"
    SAP = "sap"
    MAXIMO = "maximo"
    AZURE_AD = "azure_ad"


@dataclass
class Ticket:
    """Service/ITSM ticket."""
    id: str
    system: EnterpriseSystem
    title: str
    description: str
    priority: str
    status: str


@dataclass
class WorkOrder:
    """Enterprise work order."""
    id: str
    system: EnterpriseSystem
    asset_id: str
    description: str
    assigned_to: str | None


@dataclass
class EnterpriseConfig:
    """Configuration for enterprise system."""
    system: EnterpriseSystem
    base_url: str
    client_id: str | None = None
    client_secret: str | None = None
