"""Troubleshooting Engine for Biomedical Devices."""
from dataclasses import dataclass
from typing import Any

from core.PHASE_1.clinical.troubleshooting import (
    TroubleshootingResult,
    TroubleshootingStep,
)


@dataclass
class TroubleshootingStep:
    """Represents a single troubleshooting step."""
    step_number: int
    action: str
    verification: str
    safety_check: str


@dataclass
class TroubleshootingResult:
    """Result of troubleshooting analysis."""
    steps: list[TroubleshootingStep]
    estimated_time: str
    required_tools: list[str]
    safety_warnings: list[str]


class TroubleshootingEngine:
    """
    Troubleshooting Engine for biomedical engineering.
    
    Generates step-by-step troubleshooting procedures based on device type
    and diagnosed problems.
    """

    def __init__(self):
        self._procedures: dict[str, dict[str, Any]] = {}
        self._initialize_procedures()

    def _initialize_procedures(self) -> None:
        """Initialize troubleshooting procedures database."""
        # Power supply troubleshooting
        self._procedures["power_failure"] = {
            "estimated_time": "30-45 minutes",
            "required_tools": [
                "Digital multimeter",
                "Oscilloscope",
                "Insulated screwdrivers",
                "ESD wrist strap",
            ],
            "safety_warnings": [
                "Disconnect device from power before opening",
                "Wait 30 seconds for capacitors to discharge",
                "Use insulated tools only",
                "Follow lockout/tagout procedures",
            ],
            "steps": [
                {
                    "action": "Verify power source",
                    "verification": "Check outlet with known working device",
                    "safety_check": "Ensure hands are dry",
                },
                {
                    "action": "Inspect power cable",
                    "verification": "Check for visible damage, test continuity",
                    "safety_check": "Cable must be unplugged",
                },
                {
                    "action": "Test power supply output voltages",
                    "verification": "Measure voltages with multimeter",
                    "safety_check": "Use caution near exposed circuits",
                },
                {
                    "action": "Check internal fuses",
                    "verification": "Test each fuse for continuity",
                    "safety_check": "Device must be unpowered",
                },
                {
                    "action": "Inspect power supply capacitors",
                    "verification": "Look for bulging, leakage, or damage",
                    "safety_check": "Discharge capacitors before inspection",
                },
                {
                    "action": "Replace power supply unit if faulty",
                    "verification": "Reconnect power and test",
                    "safety_check": "Use manufacturer-approved replacement",
                },
            ],
        }

        # Display troubleshooting
        self._procedures["display_failure"] = {
            "estimated_time": "20-30 minutes",
            "required_tools": [
                "Screwdriver set (precision)",
                "Anti-static mat",
                "Soft cloth",
                "IPA wipes",
            ],
            "safety_warnings": [
                "Disconnect power before opening",
                "Handle LCD panel with care",
                "Avoid touching screen surface",
                "Work on anti-static mat",
            ],
            "steps": [
                {
                    "action": "Check external video connections",
                    "verification": "Reseat all cable connections",
                    "safety_check": "Power off device",
                },
                {
                    "action": "Test with external monitor",
                    "verification": "Connect to known working display",
                    "safety_check": "Use appropriate adapter",
                },
                {
                    "action": "Inspect display ribbon cables",
                    "verification": "Check for damage or oxidation",
                    "safety_check": "Handle cables gently",
                },
                {
                    "action": "Check backlight functionality",
                    "verification": "Shine flashlight at angle to screen",
                    "safety_check": "Power must be off",
                },
                {
                    "action": "Verify inverter output",
                    "verification": "Measure AC voltage from inverter",
                    "safety_check": "High voltage caution",
                },
                {
                    "action": "Replace display assembly if needed",
                    "verification": "Test new display before full reassembly",
                    "safety_check": "Use OEM replacement part",
                },
            ],
        }

        # Communication failure troubleshooting
        self._procedures["communication_failure"] = {
            "estimated_time": "25-40 minutes",
            "required_tools": [
                "Network cable tester",
                "Serial/USB cables",
                "Port configuration software",
                "Wireshark (optional)",
            ],
            "safety_warnings": [
                "No electrical safety risks for communication issues",
                "Verify protocol compatibility",
                "Backup configuration before changes",
            ],
            "steps": [
                {
                    "action": "Verify physical connections",
                    "verification": "Check all cable connections",
                    "safety_check": "Ensure cables are fully seated",
                },
                {
                    "action": "Test network connectivity",
                    "verification": "Ping gateway and remote device",
                    "safety_check": None,
                },
                {
                    "action": "Check port configuration",
                    "verification": "Compare settings with known working config",
                    "safety_check": "Document original settings",
                },
                {
                    "action": "Verify firewall settings",
                    "verification": "Check inbound/outbound rules",
                    "safety_check": "Document changes",
                },
                {
                    "action": "Test with direct connection",
                    "verification": "Bypass network infrastructure",
                    "safety_check": None,
                },
                {
                    "action": "Review protocol logs",
                    "verification": "Look for error codes or timeouts",
                    "safety_check": None,
                },
            ],
        }

        # Sensor failure troubleshooting
        self._procedures["sensor_failure"] = {
            "estimated_time": "45-60 minutes",
            "required_tools": [
                "Calibration simulator",
                "Digital multimeter",
                "Oscilloscope",
                "Sensor-specific tools",
            ],
            "safety_warnings": [
                "Follow bio-compatibility guidelines",
                "Use appropriate PPE for biohazard sensors",
                "Calibration requires trained personnel",
                "Document all measurements",
            ],
            "steps": [
                {
                    "action": "Verify sensor mounting and positioning",
                    "verification": "Check physical installation",
                    "safety_check": "Device must be decontaminated",
                },
                {
                    "action": "Test sensor with simulator",
                    "verification": "Compare readings against known values",
                    "safety_check": "Use calibrated simulator",
                },
                {
                    "action": "Check sensor wiring",
                    "verification": "Test continuity and insulation",
                    "safety_check": "Power off device",
                },
                {
                    "action": "Inspect for contamination",
                    "verification": "Visual inspection and cleaning",
                    "safety_check": "Use appropriate cleaning agents",
                },
                {
                    "action": "Check for electromagnetic interference",
                    "verification": "Relocate from potential EMI sources",
                    "safety_check": None,
                },
                {
                    "action": "Replace sensor and recalibrate",
                    "verification": "Full calibration procedure",
                    "safety_check": "Document replacement",
                },
            ],
        }

        # Calibration drift troubleshooting
        self._procedures["calibration_drift"] = {
            "estimated_time": "60-90 minutes",
            "required_tools": [
                "Reference standards",
                "Calibration equipment",
                "Environment monitor",
                "Calibration software",
            ],
            "safety_warnings": [
                "Use certified reference standards",
                "Allow equipment to stabilize",
                "Record environmental conditions",
                "Follow calibration procedures",
            ],
            "steps": [
                {
                    "action": "Verify environmental conditions",
                    "verification": "Check temperature, humidity",
                    "safety_check": None,
                },
                {
                    "action": "Check reference standard calibration",
                    "verification": "Verify reference is within calibration",
                    "safety_check": "Use current calibration sticker",
                },
                {
                    "action": "Run internal diagnostics",
                    "verification": "Check for error codes",
                    "safety_check": None,
                },
                {
                    "action": "Perform two-point calibration",
                    "verification": "Verify output at low and high points",
                    "safety_check": "Allow stabilization time",
                },
                {
                    "action": "Document calibration results",
                    "verification": "Record all measurements",
                    "safety_check": "Sign calibration certificate",
                },
                {
                    "action": "Update maintenance records",
                    "verification": "Log in CMMS",
                    "safety_check": None,
                },
            ],
        }

    def generate_procedure(
        self,
        diagnosis_id: str,
        device_type: str | None = None,
        custom_steps: list[dict[str, str]] | None = None,
    ) -> TroubleshootingResult:
        """
        Generate a troubleshooting procedure based on diagnosis.
        
        Args:
            diagnosis_id: The diagnosis identifier (e.g., 'power_failure')
            device_type: Optional device type for specific procedures
            custom_steps: Optional custom steps to add
            
        Returns:
            TroubleshootingResult with step-by-step procedure
        """
        # Find matching procedure
        procedure = self._procedures.get(diagnosis_id)
        
        if procedure is None:
            # Generate generic procedure
            return self._generate_generic_procedure(diagnosis_id)
        
        # Build steps
        steps = []
        for i, step_data in enumerate(procedure["steps"], 1):
            step = TroubleshootingStep(
                step_number=i,
                action=step_data["action"],
                verification=step_data["verification"],
                safety_check=step_data.get("safety_check", "No specific safety concerns"),
            )
            steps.append(step)
        
        # Add custom steps if provided
        if custom_steps:
            start_num = len(steps) + 1
            for i, custom in enumerate(custom_steps, start_num):
                step = TroubleshootingStep(
                    step_number=i,
                    action=custom.get("action", "Custom step"),
                    verification=custom.get("verification", "Verify outcome"),
                    safety_check=custom.get("safety_check", "Follow standard precautions"),
                )
                steps.append(step)
        
        return TroubleshootingResult(
            steps=steps,
            estimated_time=procedure["estimated_time"],
            required_tools=procedure["required_tools"],
            safety_warnings=procedure["safety_warnings"],
        )

    def _generate_generic_procedure(
        self,
        diagnosis_id: str,
    ) -> TroubleshootingResult:
        """Generate a generic troubleshooting procedure."""
        generic_steps = [
            {
                "action": "Verify the problem exists",
                "verification": "Reproduce the issue",
                "safety_check": "Document symptoms",
            },
            {
                "action": "Check device documentation",
                "verification": "Review manual and service bulletins",
                "safety_check": None,
            },
            {
                "action": "Perform visual inspection",
                "verification": "Look for obvious damage",
                "safety_check": "Power off device",
            },
            {
                "action": "Run diagnostic tests",
                "verification": "Check error codes and logs",
                "safety_check": None,
            },
            {
                "action": "Isolate the cause",
                "verification": "Test components individually",
                "safety_check": "Follow isolation procedures",
            },
            {
                "action": "Implement fix",
                "verification": "Test after repair",
                "safety_check": "Verify safety systems",
            },
            {
                "action": "Document resolution",
                "verification": "Update maintenance records",
                "safety_check": None,
            },
        ]
        
        steps = [
            TroubleshootingStep(
                step_number=i,
                action=s["action"],
                verification=s["verification"],
                safety_check=s.get("safety_check") or "Follow standard precautions",
            )
            for i, s in enumerate(generic_steps, 1)
        ]
        
        return TroubleshootingResult(
            steps=steps,
            estimated_time="30-60 minutes",
            required_tools=["Basic tool kit", "Multimeter", "Documentation"],
            safety_warnings=[
                "Always disconnect power before opening equipment",
                "Follow lockout/tagout procedures",
                "Use appropriate PPE",
            ],
        )

    def get_tools_for_diagnosis(self, diagnosis_id: str) -> list[str]:
        """Get required tools for a specific diagnosis."""
        procedure = self._procedures.get(diagnosis_id)
        if procedure:
            return procedure["required_tools"]
        return ["Basic tool kit", "Multimeter", "Documentation"]

    def get_safety_warnings(self, diagnosis_id: str) -> list[str]:
        """Get safety warnings for a specific diagnosis."""
        procedure = self._procedures.get(diagnosis_id)
        if procedure:
            return procedure["safety_warnings"]
        return [
            "Always disconnect power before opening equipment",
            "Follow lockout/tagout procedures",
            "Use appropriate PPE",
        ]


# Global instance
_engine: TroubleshootingEngine | None = None


def get_troubleshooting_engine() -> TroubleshootingEngine:
    """Get or create the global troubleshooting engine instance."""
    global _engine
    if _engine is None:
        _engine = TroubleshootingEngine()
    return _engine
