"""HL7 v2 Message Handler for Hospital Systems Integration."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable


class HL7MessageType(str, Enum):
    ADT = "ADT"  # Admit/Discharge/Transfer
    ORM = "ORM"  # Order Message
    ORU = "ORU"  # Observation Result
    MDM = "MDM"  # Medical Document Management
    DFT = "DFT"  # Detail Financial Transaction
    QRY = "QRY"  # Query


@dataclass
class HL7Segment:
    """Represents an HL7 message segment."""
    name: str
    fields: list[str]


@dataclass
class HL7Message:
    """Parsed HL7 message."""
    message_type: str
    trigger_event: str
    segments: dict[str, list[HL7Segment]]
    raw_message: str

    @property
    def message_control_id(self) -> str:
        """Get message control ID from MSH segment."""
        segments = self.segments.get("MSH", [])
        if segments:
            return segments[0].fields[10] if len(segments[0].fields) > 10 else ""
        return ""

    @property
    def sending_application(self) -> str:
        """Get sending application from MSH segment."""
        segments = self.segments.get("MSH", [])
        if segments:
            return segments[0].fields[2] if len(segments[0].fields) > 2 else ""
        return ""


class HL7Parser:
    """
    HL7 v2.x message parser.
    
    Parses HL7 messages into structured data for processing.
    """

    SEGMENT_DELIMITER = "\r"
    FIELD_DELIMITER = "|"
    COMPONENT_DELIMITER = "^"
    REPETITION_DELIMITER = "~"
    SUBCOMPONENT_DELIMITER = "&"

    def parse(self, raw_message: str) -> HL7Message:
        """
        Parse an HL7 v2 message.
        
        Args:
            raw_message: Raw HL7 message string
            
        Returns:
            Parsed HL7Message object
        """
        # Normalize line endings
        message = raw_message.replace("\n", "\r").replace("\r\r", "\r")
        
        # Split into segments
        segment_strings = message.split(self.SEGMENT_DELIMITER)
        segment_strings = [s for s in segment_strings if s.strip()]
        
        segments: dict[str, list[HL7Segment]] = {}
        
        for seg_str in segment_strings:
            fields = self._split_fields(seg_str)
            if not fields:
                continue
            
            segment_name = fields[0]
            hl7_segment = HL7Segment(
                name=segment_name,
                fields=fields[1:],  # Exclude segment name
            )
            
            if segment_name not in segments:
                segments[segment_name] = []
            segments[segment_name].append(hl7_segment)
        
        # Extract message type
        message_type = ""
        trigger_event = ""
        
        msh_segments = segments.get("MSH", [])
        if msh_segments:
            # MSH.9 contains message type^trigger event
            type_fields = msh_segments[0].fields
            if len(type_fields) > 1:
                type_component = type_fields[1]
                components = type_component.split(self.COMPONENT_DELIMITER)
                message_type = components[0] if len(components) > 0 else ""
                trigger_event = components[1] if len(components) > 1 else ""
        
        return HL7Message(
            message_type=message_type,
            trigger_event=trigger_event,
            segments=segments,
            raw_message=raw_message,
        )

    def _split_fields(self, segment: str) -> list[str]:
        """Split a segment into fields."""
        if not segment:
            return []
        
        # MSH segment has special handling (first character is field delimiter)
        if segment.startswith("MSH"):
            # MSH.1 is the field delimiter itself
            first_field = segment[3]
            fields = [segment[:3]]  # "MSH"
            remainder = segment[4:]  # Skip MSH and the delimiter
            
            # Use MSH.1 as the field delimiter for this message
            if first_field == self.FIELD_DELIMITER:
                remaining_fields = remainder.split(self.FIELD_DELIMITER)
                fields.extend(remaining_fields)
            else:
                # Non-standard delimiter, treat as normal segment
                fields = segment.split(self.FIELD_DELIMITER)
            
            return fields
        
        return segment.split(self.FIELD_DELIMITER)

    def format_datetime(self, hl7_date: str) -> datetime | None:
        """
        Parse HL7 datetime format to Python datetime.
        
        Supports formats: YYYYMMDD, YYYYMMDDHHmm, YYYYMMDDHHmmss
        """
        if not hl7_date:
            return None
        
        formats = [
            "%Y%m%d%H%M%S",
            "%Y%m%d%H%M",
            "%Y%m%d",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(hl7_date[:len(fmt.replace("%", ""))], fmt)
            except ValueError:
                continue
        
        return None


class HL7Listener:
    """
    HL7 v2 message listener for receiving messages from hospital systems.
    
    Can be used with MLLP protocol or direct socket connections.
    """

    def __init__(self, port: int = 2575):
        """
        Initialize HL7 listener.
        
        Args:
            port: Port to listen on for incoming messages
        """
        self.port = port
        self.parser = HL7Parser()
        self._handlers: dict[str, Callable[[HL7Message], None]] = {}
        self._running = False

    def register_handler(
        self,
        message_type: str,
        handler: Callable[[HL7Message], None],
    ) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: Message type (e.g., "ADT", "ORU")
            handler: Callback function to handle the message
        """
        self._handlers[message_type] = handler

    async def process_message(self, raw_message: str) -> HL7Message | None:
        """
        Process an incoming HL7 message.
        
        Args:
            raw_message: Raw HL7 message string
            
        Returns:
            Parsed HL7Message if successful
        """
        try:
            message = self.parser.parse(raw_message)
            
            # Find appropriate handler
            handler = self._handlers.get(message.message_type)
            if handler:
                handler(message)
            elif "*" in self._handlers:
                # Wildcard handler
                self._handlers["*"](message)
            
            return message
            
        except Exception as e:
            # Log parsing error
            return None

    def extract_patient_id(self, message: HL7Message) -> str | None:
        """
        Extract patient ID from PID segment.
        
        Args:
            message: Parsed HL7 message
            
        Returns:
            Patient ID or None if not found
        """
        pid_segments = message.segments.get("PID", [])
        if not pid_segments:
            return None
        
        pid = pid_segments[0]
        # PID.3 contains patient ID list
        if len(pid.fields) > 3:
            return pid.fields[3].split(self.COMPONENT_DELIMITER)[0]
        
        return None

    def extract_location(self, message: HL7Message) -> str | None:
        """
        Extract location from PV1 segment.
        
        Args:
            message: Parsed HL7 message
            
        Returns:
            Location code or None if not found
        """
        pv1_segments = message.segments.get("PV1", [])
        if not pv1_segments:
            return None
        
        pv1 = pv1_segments[0]
        # PV1.3 contains patient location
        if len(pv1.fields) > 3:
            return pv1.fields[3].split(self.COMPONENT_DELIMITER)[0]
        
        return None

    def extract_order_info(self, message: HL7Message) -> list[dict[str, str]]:
        """
        Extract order information from OBR segment.
        
        Args:
            message: Parsed HL7 message
            
        Returns:
            List of order dictionaries
        """
        orders = []
        
        obr_segments = message.segments.get("OBR", [])
        for obr in obr_segments:
            if len(obr.fields) > 4:
                order = {
                    "order_id": obr.fields[2] if len(obr.fields) > 2 else "",
                    "universal_service_id": obr.fields[4],
                    "datetime": obr.fields[7] if len(obr.fields) > 7 else "",
                }
                orders.append(order)
        
        return orders


# Factory function
def create_hl7_listener(port: int = 2575) -> HL7Listener:
    """
    Create an HL7 listener instance.
    
    Args:
        port: Port to listen on
        
    Returns:
        Configured HL7Listener instance
    """
    return HL7Listener(port=port)
