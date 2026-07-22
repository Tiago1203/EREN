"""Demo: First Cognitive Cycle of EREN.

This script demonstrates the first end-to-end cognitive cycle
executing through all components using only contracts.

Usage:
    python core/runtime/demo_cognitive_cycle.py
"""


# Add the project to the path
import sys

sys.path.insert(0, '/workspace/project/EREN')

from core.PHASE_2.runtime import (
    RuntimeBuilder,
)


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_event(event) -> None:
    """Print an event."""
    print(f"  📍 [{event.event_type.value}] {event.payload}")


def main():
    """Execute the first cognitive cycle."""
    print_header("EREN COGNITIVE RUNTIME — FIRST COGNITIVE CYCLE")
    print("\n🚀 Starting the Cognitive Operating System...")

    # Create the runtime with builder
    print("\n📦 Creating Cognitive Runtime...")
    runtime = (
        RuntimeBuilder()
        .with_name("EREN Cognitive Runtime")
        .with_version("1.0.0")
        .with_simulation_mode(True)
        .with_simulation_delay(50)  # Faster for demo
        .with_auto_boot(False)  # Manual control
        .with_auto_validate(False)
        .build()
    )
    print(f"   ✅ Runtime created: {runtime.runtime_id}")
    print(f"   📊 State: {runtime.state.value}")

    # Initialize
    print_header("STEP 1: INITIALIZATION")
    print("   🔧 Initializing Composition Root...")
    print("   🔧 Building DI Container...")
    print("   🔧 Configuring Event Bus...")
    print("   🔧 Setting up Capability Registry...")
    print("   🔧 Creating Managers...")
    print("   🔧 Initializing Engines...")
    runtime.initialize()
    print(f"   ✅ State: {runtime.state.value}")
    print(f"   📊 Events published: {len(runtime.events)}")

    # Boot
    print_header("STEP 2: BOOT")
    print("   📋 Executing Boot Manager...")
    print("   📋 Loading modules...")
    print("   📋 Validating contracts...")
    runtime.boot()
    print(f"   ✅ State: {runtime.state.value}")

    # Validate
    print_header("STEP 3: VALIDATION")
    print("   🔍 Validating all components...")
    report = runtime.validate()
    print(f"   ✅ Validation: {'PASSED' if report.is_valid else 'FAILED'}")
    print(f"   📋 Checks: {len(report.results)}, Passed: {sum(1 for r in report.results if r.passed)}")

    # Start
    print_header("STEP 4: START")
    runtime.start()
    print("   ✅ Runtime is RUNNING")
    print(f"   📊 Events published: {len(runtime.events)}")

    # Create session
    print_header("STEP 5: CREATE SESSION")
    print("   👤 User: Dr. Smith")
    print("   🏥 Hospital: General Hospital")
    session = runtime.create_session(
        user_id="dr-smith",
        hospital_id="general-hospital"
    )
    print(f"   ✅ Session created: {session.session_id}")
    print(f"   🔗 Correlation ID: {session.correlation_id}")

    # Execute cognitive cycle
    print_header("STEP 6: COGNITIVE CYCLE")
    print("   🎯 Intent: 'Device XYZ showing error code E123'")

    intent = {
        "query": "Device XYZ showing error code E123",
        "user_id": "dr-smith",
        "urgency": "high",
        "device_type": "patient_monitor",
    }

    print("\n   📍 Executing through all engines...\n")

    # Execute the cycle
    runtime.execute_cognitive_cycle(session, intent=intent)

    print("\n   ✅ COGNITIVE CYCLE COMPLETED!")

    # Show results
    print_header("CYCLE RESULTS")
    print(f"   📊 Stages completed: {len(session.stages_completed)}")
    print(f"   🔧 Engines executed: {', '.join(session.engines_executed)}")
    print(f"   📝 Plan created: {session.plan.get('plan_id', 'N/A')}")
    print(f"   📚 Knowledge retrieved: {len(session.knowledge_results)} items")
    print(f"   🧠 Memories retrieved: {len(session.memory_results)} items")
    print(f"   💡 Hypotheses generated: {len(session.hypotheses)}")
    print(f"   ✅ Decisions made: {len(session.decisions)}")
    print(f"   ⚡ Actions generated: {len(session.actions)}")

    # Best hypothesis
    if session.hypotheses:
        best = session.hypotheses[0]
        print(f"\n   🏆 Best hypothesis: {best.get('description', 'N/A')}")
        print(f"   📈 Probability: {best.get('probability', 0):.2f}")

    # Decision
    if session.decisions:
        decision = session.decisions[0]
        print(f"\n   🎯 Decision: {decision.get('type', 'N/A')}")
        print(f"   📝 Based on: {decision.get('based_on_hypothesis', 'N/A')}")
        print(f"   📊 Confidence: {decision.get('confidence', 0):.2f}")

    # Action
    if session.actions:
        action = session.actions[0]
        print(f"\n   ⚡ Action: {action.get('type', 'N/A')}")
        print(f"   📋 Result: {action.get('result', 'N/A')}")

    # Complete session
    print_header("STEP 7: COMPLETE SESSION")
    runtime.complete_session(session)
    print("   ✅ Session completed")

    # Show all events
    print_header("EVENT FLOW")
    for i, event in enumerate(runtime.events, 1):
        print(f"   {i:2d}. [{event.event_type.value}]")

    # Metrics
    print_header("METRICS")
    summary = runtime.metrics.get_summary()
    print(f"   Status: {summary['status']}")
    print(f"   Duration: {summary.get('duration_ms', 0)}ms")
    print(f"   Sessions: {summary['sessions']['created']} created, {summary['sessions']['completed']} completed")
    print(f"   Cycles: {summary['cycles']['completed']} completed, {summary['cycles']['failed']} failed")
    print(f"   Events: {summary['events']['published']} published")
    print(f"   Errors: {summary['errors']['total']} total, {summary['errors']['critical']} critical")

    # Health
    print_header("HEALTH STATUS")
    health = runtime.health_check()
    print(f"   Overall: {health.overall_status.value}")
    print(f"   Components: {health.summary['healthy']} healthy, {health.summary['degraded']} degraded, {health.summary['unhealthy']} unhealthy")

    # Shutdown
    print_header("SHUTDOWN")
    runtime.shutdown()
    print(f"   ✅ Runtime stopped: {runtime.state.value}")

    # Final summary
    print_header("FIRST COGNITIVE CYCLE COMPLETE!")
    print("""
   🎉 This demonstrates the complete flow through all EREN components:
   
   📥 Input → Composition Root → DI Container → Event Bus
   ↓
   Session Manager → Lifecycle Manager → Orchestrator
   ↓
   Planner → Knowledge → Memory → Reasoning → Decision → Tool
   ↓
   Cognitive Context Update → Session Complete → Runtime Done
   
   ✨ All components worked together using ONLY contracts!
   ✨ No AI was used — pure architecture coordination!
    """)


if __name__ == "__main__":
    main()
