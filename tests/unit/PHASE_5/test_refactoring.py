"""
Tests para las mejoras de refactorización de PHASE 5

Incluye tests para:
- Shared Domain Objects (eliminación de duplicación)
- AgentBus (comunicación entre agentes)
- OrchestratorAgent (conexión de EPICs)
- Integrated Gateways
"""

import pytest
from datetime import UTC, datetime

# =============================================================================
# TESTS SHARED DOMAIN OBJECTS
# =============================================================================

from core.PHASE_5.foundation.domain.shared import (
    SharedSessionStatus,
    SharedMetricType,
    SharedOptimizationType,
    SharedMetricValue,
    SharedAgentMetric,
    SharedRecommendation,
    SharedLearningSession,
    SharedOptimizationReport,
)


class TestSharedDomainObjects:
    """Tests para Domain Objects compartidos."""
    
    def test_shared_session_status(self):
        """Test SharedSessionStatus enum."""
        assert SharedSessionStatus.PENDING.value == "pending"
        assert SharedSessionStatus.RUNNING.value == "running"
        assert SharedSessionStatus.COMPLETED.value == "completed"
    
    def test_shared_metric_type(self):
        """Test SharedMetricType enum."""
        assert SharedMetricType.PERFORMANCE.value == "performance"
        assert SharedMetricType.ACCURACY.value == "accuracy"
        assert SharedMetricType.RESPONSE_TIME.value == "response_time"
    
    def test_shared_agent_metric_creation(self):
        """Test creación de SharedAgentMetric."""
        metric = SharedAgentMetric(
            agent_id="agent_1",
            metric_type=SharedMetricType.PERFORMANCE,
            current_value=0.85,
            previous_value=0.75,
        )
        
        assert metric.agent_id == "agent_1"
        assert metric.metric_type == SharedMetricType.PERFORMANCE
        assert metric.trend == "stable"  # Cambio < 5%
    
    def test_shared_agent_metric_improving(self):
        """Test cálculo de tendencia improving."""
        metric = SharedAgentMetric(
            agent_id="agent_1",
            metric_type=SharedMetricType.PERFORMANCE,
            current_value=0.90,
            previous_value=0.70,
        )
        
        assert metric.calculate_trend() == "improving"
    
    def test_shared_agent_metric_declining(self):
        """Test cálculo de tendencia declining."""
        metric = SharedAgentMetric(
            agent_id="agent_1",
            metric_type=SharedMetricType.PERFORMANCE,
            current_value=0.60,
            previous_value=0.80,
        )
        
        assert metric.calculate_trend() == "declining"
    
    def test_shared_recommendation(self):
        """Test SharedRecommendation."""
        rec = SharedRecommendation(
            title="Improve accuracy",
            description="Reduce error rate",
            priority=8,
            expected_impact=0.75,
        )
        
        assert rec.title == "Improve accuracy"
        assert rec.implemented is False
        
        rec.implement()
        assert rec.implemented is True
        assert rec.implemented_at is not None
    
    def test_shared_learning_session(self):
        """Test SharedLearningSession."""
        session = SharedLearningSession(
            agent_id="agent_1",
            description="Training session",
        )
        
        assert session.status == SharedSessionStatus.PENDING
        assert len(session.metrics) == 0
        
        session.start()
        assert session.status == SharedSessionStatus.RUNNING
        assert session.started_at is not None
        
        metric = SharedAgentMetric(
            agent_id="agent_1",
            metric_type=SharedMetricType.PERFORMANCE,
            current_value=0.85,
        )
        session.add_metric(metric)
        assert len(session.metrics) == 1
        
        session.add_improvement("Better accuracy")
        assert "Better accuracy" in session.improvements
        
        session.complete()
        assert session.status == SharedSessionStatus.COMPLETED
        assert session.completed_at is not None
    
    def test_shared_optimization_report(self):
        """Test SharedOptimizationReport."""
        report = SharedOptimizationReport(
            session_id="session_1",
            analysis_summary="Good performance",
        )
        
        # Primera recomendación no implementada
        rec1 = SharedRecommendation(
            title="Test recommendation 1",
            priority=8,
        )
        report.add_recommendation(rec1)
        
        assert report.metrics_analyzed == 1
        assert report.metrics_improved == 0  # No implementada
        
        # Segunda recomendación implementada
        rec2 = SharedRecommendation(
            title="Test recommendation 2",
            priority=9,
        )
        rec2.implement()
        report.add_recommendation(rec2)
        
        assert report.metrics_analyzed == 2
        assert report.metrics_improved == 1


# =============================================================================
# TESTS AGENT BUS
# =============================================================================

from core.PHASE_5.foundation.messaging.agent_bus import (
    AgentBus,
    AgentBusConfig,
    BusMessage,
    BusSubscription,
)


class TestAgentBus:
    """Tests para AgentBus."""
    
    @pytest.mark.asyncio
    async def test_bus_send(self):
        """Test envío de mensaje."""
        bus = AgentBus()
        
        message = await bus.send(
            sender="agent_1",
            receiver="agent_2",
            action="task_complete",
            payload={"task_id": "task_1"},
        )
        
        assert message.sender == "agent_1"
        assert message.receiver == "agent_2"
        assert message.action == "task_complete"
    
    @pytest.mark.asyncio
    async def test_bus_receive(self):
        """Test recepción de mensaje."""
        bus = AgentBus()
        
        await bus.send(
            sender="agent_1",
            receiver="agent_2",
            action="task",
        )
        
        message = await bus.receive("agent_2")
        
        assert message is not None
        assert message.sender == "agent_1"
    
    @pytest.mark.asyncio
    async def test_bus_broadcast(self):
        """Test broadcast."""
        bus = AgentBus()
        
        # Crear inboxes para agentes
        bus._inbox["agent_2"] = []
        bus._inbox["agent_3"] = []
        
        messages = await bus.broadcast(
            sender="agent_1",
            action="system_update",
        )
        
        assert len(messages) == 2  # agent_2 y agent_3
    
    @pytest.mark.asyncio
    async def test_bus_subscribe(self):
        """Test suscripción a topic."""
        bus = AgentBus()
        
        received = []
        async def handler(msg):
            received.append(msg)
        
        subscription = await bus.subscribe(
            agent_id="agent_1",
            topic="clinical_updates",
            handler=handler,
        )
        
        assert subscription.agent_id == "agent_1"
        assert subscription.topic == "clinical_updates"
    
    @pytest.mark.asyncio
    async def test_bus_publish(self):
        """Test publicación a topic."""
        bus = AgentBus()
        
        received = []
        async def handler(msg):
            received.append(msg)
        
        await bus.subscribe(
            agent_id="agent_1",
            topic="test_topic",
            handler=handler,
        )
        
        await bus.publish(
            publisher="agent_0",
            topic="test_topic",
            action="test_action",
        )
        
        assert len(received) == 1
    
    def test_bus_stats(self):
        """Test estadísticas del bus."""
        bus = AgentBus()
        
        stats = bus.get_stats()
        
        assert "messages_sent" in stats
        assert "messages_delivered" in stats
        assert "broadcasts_sent" in stats


# =============================================================================
# TESTS ORCHESTRATOR AGENT
# =============================================================================

from core.PHASE_5.epic1_orchestrator import OrchestratorAgent
from core.PHASE_5.foundation.types import AgentPriority
from core.PHASE_5.foundation.domain import AgentTask


class TestOrchestratorAgent:
    """Tests para OrchestratorAgent."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_creation(self):
        """Test creación de orquestador."""
        agent = OrchestratorAgent()
        
        assert agent.agent_id is not None
        assert agent.agent_type.value == "orchestrator"
        assert len(agent._epic_registry.connections) == 11  # EPIC 1-11
    
    @pytest.mark.asyncio
    async def test_epic_registration(self):
        """Test registro de EPICs."""
        agent = OrchestratorAgent()
        
        status = agent.get_epic_status()
        
        assert "epic_1" in status
        assert "epic_2" in status
        assert status["epic_1"]["name"] == "Agent Orchestrator"
    
    @pytest.mark.asyncio
    async def test_enable_disable_epic(self):
        """Test habilitar/deshabilitar EPIC."""
        agent = OrchestratorAgent()
        
        assert agent.disable_epic("epic_2") is True
        status = agent.get_epic_status()
        assert status["epic_2"]["enabled"] is False
        
        assert agent.enable_epic("epic_2") is True
        status = agent.get_epic_status()  # Obtener nuevo status
        assert status["epic_2"]["enabled"] is True
    
    @pytest.mark.asyncio
    async def test_determine_epic_flow(self):
        """Test determinación de flujo de EPICs."""
        agent = OrchestratorAgent()
        
        # Tarea de diagnóstico
        task = AgentTask(
            task_id="task_1",
            agent_id="orchestrator",
            task_type="diagnostic_analysis",
        )
        
        flow = agent._determine_epic_flow(task)
        
        assert "epic_1" in flow
        assert "epic_3" in flow  # Diagnostic
    
    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test ejecución de tarea."""
        agent = OrchestratorAgent()
        
        task = AgentTask(
            task_id="task_1",
            agent_id="orchestrator",
            task_type="simple_task",
        )
        
        result = await agent.execute(task)
        
        assert result.task_id == task.task_id
        assert result.agent_id == agent.agent_id


# =============================================================================
# TESTS INTEGRATED GATEWAYS
# =============================================================================

from core.PHASE_5.foundation.gateways.integrated import (
    IntegratedPhase1Gateway,
    IntegratedPhase2Gateway,
    IntegratedPhase3Gateway,
    IntegratedPhase4Gateway,
    IntegratedMultiPhaseGateway,
)


class TestIntegratedGateways:
    """Tests para Integrated Gateways."""
    
    @pytest.mark.asyncio
    async def test_phase1_gateway(self):
        """Test PHASE 1 Gateway."""
        gateway = IntegratedPhase1Gateway()
        await gateway.initialize()
        
        device = await gateway.get_device_context("device_1")
        
        assert device["device_id"] == "device_1"
        assert "type" in device
    
    @pytest.mark.asyncio
    async def test_phase2_gateway(self):
        """Test PHASE 2 Gateway."""
        gateway = IntegratedPhase2Gateway()
        await gateway.initialize()
        
        embeddings = await gateway.get_embeddings(["test"])
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 768  # Dimensión estándar
    
    @pytest.mark.asyncio
    async def test_phase3_gateway(self):
        """Test PHASE 3 Gateway."""
        gateway = IntegratedPhase3Gateway()
        await gateway.initialize()
        
        validation = await gateway.validate_with_reasoning(
            claim="Test claim",
            evidence=[],
        )
        
        assert validation["valid"] is True
        assert "confidence" in validation
    
    @pytest.mark.asyncio
    async def test_phase4_gateway(self):
        """Test PHASE 4 Gateway."""
        gateway = IntegratedPhase4Gateway()
        await gateway.initialize()
        
        results = await gateway.search_knowledge("test query")
        
        assert "query" in results
        assert results["query"] == "test query"
    
    @pytest.mark.asyncio
    async def test_multi_phase_gateway(self):
        """Test Multi-Phase Gateway."""
        gateway = IntegratedMultiPhaseGateway()
        
        context = await gateway.get_full_context("test query")
        
        assert "query" in context
        assert "business" in context
        assert "cognitive" in context
        assert "clinical" in context
        assert "knowledge" in context


# =============================================================================
# TESTS FOUNDATION IMPORTS
# =============================================================================

class TestFoundationImports:
    """Tests para verificar que Foundation tiene todos los exports."""
    
    def test_shared_objects_in_foundation(self):
        """Test que Shared Objects están en Foundation."""
        from core.PHASE_5.foundation import (
            SharedSessionStatus,
            SharedMetricType,
            SharedAgentMetric,
            SharedRecommendation,
            SharedLearningSession,
            SharedOptimizationReport,
        )
        
        assert SharedSessionStatus is not None
        assert SharedMetricType is not None
        assert SharedAgentMetric is not None
    
    def test_agent_bus_in_foundation(self):
        """Test que AgentBus está en Foundation."""
        from core.PHASE_5.foundation import AgentBus, AgentBusConfig
        
        assert AgentBus is not None
        assert AgentBusConfig is not None
    
    def test_integrated_gateways_in_foundation(self):
        """Test que Integrated Gateways están disponibles."""
        from core.PHASE_5.foundation.gateways import (
            IntegratedPhase1Gateway,
            IntegratedPhase2Gateway,
            IntegratedPhase3Gateway,
            IntegratedPhase4Gateway,
            IntegratedMultiPhaseGateway,
        )
        
        assert IntegratedPhase1Gateway is not None
        assert IntegratedMultiPhaseGateway is not None


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
