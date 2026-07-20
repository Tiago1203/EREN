"""
HL7 Listener for EREN

Receives HL7 messages from medical devices.
"""
from typing import Dict, Any, Callable, Optional
from datetime import datetime
import asyncio


class HL7Message:
    """Represents an HL7 message."""
    def __init__(self, raw_message: str):
        self.raw = raw_message
        self.message_type = self._parse_field("MSH", "9")
        self.patient_id = self._parse_field("PID", "3")
    
    def _parse_field(self, segment: str, field: str) -> Optional[str]:
        """Parse HL7 field."""
        return None


class HL7Listener:
    """Listens for HL7 messages."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 2575):
        self.host = host
        self.port = port
        self.handlers: Dict[str, Callable] = {}
        self._running = False
    
    async def start(self):
        """Start listening for HL7 messages."""
        self._running = True
        # In production: use HL7apy or similar
    
    async def stop(self):
        """Stop listening."""
        self._running = False
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register handler for message type."""
        self.handlers[message_type] = handler
    
    async def process_message(self, message: HL7Message):
        """Process received HL7 message."""
        handler = self.handlers.get(message.message_type)
        if handler:
            await handler(message)
