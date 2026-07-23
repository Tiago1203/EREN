"""
Tests para la implementación completa de PHASE 5

Incluye tests para:
- Real Phase Gateways
- MultiAgentOrchestrator
- Agent Repository
- Integración completa
"""

import pytest
from datetime import UTC, datetime


# =============================================================================
# TESTS REAL PHASE GATEWAYS
# =============================================================================

from core.PHASE_5.foundation.gateways.real import (
    Phase1Gateway,
    Phase2Gateway,
    Phase3Gateway,
    Phase4Gateway,
    MultiPhaseGateway,
)


class TestRealPhaseGateways:
    """Tests para Real Phase Gateways."""
    
    @pytest.mark.asyncio
    async def test_phase1_gateway_initialize(self):
        """Test inicialización de PHASE 1 Gateway."""
        gateway = Phase1Gateway()
        await gateway.initialize()
        assert gateway._initialized is True
    
    @pytest.mark.asyncio
    async def test_phase1_gateway_device_context(self):
        """Test obtención de contexto de dispositivo."""
        gateway = Phase1Gateway()
        await gateway.initialize()
        
        device = await gateway.get_device_context("device_123")
        
        assert device["device_id"] == "device_123"
        assert "type" in device
        assert "status" in device
    
    @pytest.mark.asyncio
    async def test_phase1_gateway_incident_context(self):
        """Test obtención de contexto de incidente."""
        gateway = Phase1Gateway()
        await gateway.initialize()
        
        incident = await gateway.get_incident_context("incident_123")
        
        assert incident["incident_id"] == "incident_123"
        assert "severity" in incident
    
    @pytest.mark.asyncio
    async def test_phase2_gateway_initialize(self):
        """Test inicialización de PHASE 2 Gateway."""
        gateway = Phase2Gateway()
        await gateway.initialize()
        assert gateway._initialized is True
    
    @pytest.mark.asyncio
    async def test_phase2_gateway_embeddings(self):
        """Test obtención de embeddings."""
        gateway = Phase2Gateway()
        await gateway.initialize()
        
        embeddings = await gateway.get_embeddings(["test text", "another text"])
        
        assert len(embeddings) == 2
        assert len(embeddings[0]) == 768
    
    @pytest.mark.asyncio
    async def test_phase2_gateway_retrieve_context(self):
        """Test recuperación de contexto."""
        gateway = Phase2Gateway()
        await gateway.initialize()
        
        context = await gateway.retrieve_context("test query")
        
        assert context["query"] == "test query"
        assert "context" in context
    
    @pytest.mark.asyncio
    async def test_phase3_gateway_initialize(self):
        """Test inicialización de PHASE 3 Gateway."""
        gateway = Phase3Gateway()
        await gateway.initialize()
        assert gateway._initialized is True
    
    @pytest.mark.asyncio
    async def test_phase3_gateway_validate_reasoning(self):
        """Test validación con razonamiento."""
        gateway = Phase3Gateway()
        await gateway.initialize()
        
        result = await gateway.validate_with_reasoning(
            claim="Test claim",
            evidence=[{"source": "test"}],
        )
        
        assert result["valid"] is True
        assert "confidence" in result
        assert "reasoning" in result
    
    @pytest.mark.asyncio
    async def test_phase3_gateway_check_safety(self):
        """Test verificación de seguridad."""
        gateway = Phase3Gateway()
        await gateway.initialize()
        
        safety = await gateway.check_safety("test content")
        
        assert safety["safe"] is True
        assert "warnings" in safety
    
    @pytest.mark.asyncio
    async def test_phase4_gateway_initialize(self):
        """Test inicialización de PHASE 4 Gateway."""
        gateway = Phase4Gateway()
        await gateway.initialize()
        assert gateway._initialized is True
    
    @pytest.mark.asyncio
    async def test_phase4_gateway_search_knowledge(self):
        """Test búsqueda de conocimiento."""
        gateway = Phase4Gateway()
        await gateway.initialize()
        
        results = await gateway.search_knowledge(
            query="test query",
            domain="clinical",
            top_k=5,
        )
        
        assert results["query"] == "test query"
        assert results["domain"] == "clinical"
        assert results["top_k"] == 5
    
    @pytest.mark.asyncio
    async def test_phase4_gateway_retrieve_with_rag(self):
        """Test retrieval con RAG."""
        gateway = Phase4Gateway()
        await gateway.initialize()
        
        result = await gateway.retrieve_with_rag("test query")
        
        assert "query" in result
        assert "rag_applied" in result
        assert result["rag_applied"] is True
    
    @pytest.mark.asyncio
    async def test_multi_phase_gateway_initialize_all(self):
        """Test inicialización de Multi-Phase Gateway."""
        gateway = MultiPhaseGateway()
        await gateway.initialize_all()
        
        assert gateway._initialized is True
    
    @pytest.mark.asyncio
    async def test_multi_phase_gateway_full_context(self):
        """Test obtención de contexto completo."""
        gateway = MultiPhaseGateway()
        
        context = await gateway.get_full_context(
            query="test query",
            context_type="clinical",
        )
        
        assert context["query"] == "test query"
        assert "business" in context
        assert "cognitive" in context
        assert "clinical" in context
        assert "knowledge" in context
        assert "phases_integrated" in context
        assert len(context["phases_integrated"]) == 4
    
    @pytest.mark.asyncio
    async def test_multi_phase_gateway_process_all_phases(self):
        """Test procesamiento con todas las fases."""
        gateway = MultiPhaseGateway()
        
        result = await gateway.process_with_all_phases({
            "query": "test",
            "type": "diagnostic",
        })
        
        assert "embeddings" in result
        assert "cognitive_context" in result
        assert "clinical_validation" in result
        assert "safety_check" in result
        assert "knowledge" in result
        assert "rag_context" in result


# =============================================================================
# TESTS AGENT REPOSITORY
# =============================================================================

from core.PHASE_5.foundation.registry.agent_repository import (
    IAgentRepository,
    InMemoryAgentRepository,
)
from core.PHASE_5.foundation import Agent
from core.PHASE_5.foundation.types import AgentType


class TestAgentRepository:
    """Tests para Agent Repository."""
    
    @pytest.mark.asyncio
    async def test_in_memory_repository_save(self):
        """Test guardar agente."""
        repo = InMemoryAgentRepository()
        agent = Agent(agent_id="agent_1", agent_type=AgentType.ORCHESTRATOR)
        
        await repo.save(agent)
        
        saved = await repo.get_by_id("agent_1")
        assert saved is not None
        assert saved.agent_id == "agent_1"
    
    @pytest.mark.asyncio
    async def test_in_memory_repository_get(self):
        """Test obtener agente."""
        repo = InMemoryAgentRepository()
        agent = Agent(agent_id="agent_1", agent_type=AgentType.ORCHESTRATOR)
        
        await repo.save(agent)
        
        retrieved = await repo.get_by_id("agent_1")
        assert retrieved is not None
        assert retrieved.agent_id == "agent_1"
    
    @pytest.mark.asyncio
    async def test_in_memory_repository_get_not_found(self):
        """Test obtener agente no existente."""
        repo = InMemoryAgentRepository()
        
        retrieved = await repo.get_by_id("nonexistent")
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_in_memory_repository_delete(self):
        """Test eliminar agente."""
        repo = InMemoryAgentRepository()
        agent = Agent(agent_id="agent_1", agent_type=AgentType.ORCHESTRATOR)
        
        await repo.save(agent)
        deleted = await repo.delete("agent_1")
        
        assert deleted is True
        assert await repo.get_by_id("agent_1") is None
    
    @pytest.mark.asyncio
    async def test_in_memory_repository_list_all(self):
        """Test listar agentes."""
        repo = InMemoryAgentRepository()
        
        await repo.save(Agent(agent_id="agent_1", agent_type=AgentType.ORCHESTRATOR))
        await repo.save(Agent(agent_id="agent_2", agent_type=AgentType.ORCHESTRATOR))
        
        agents = await repo.list_all()
        assert len(agents) == 2
    
    @pytest.mark.asyncio
    async def test_in_memory_repository_update(self):
        """Test actualizar agente."""
        repo = InMemoryAgentRepository()
        agent = Agent(agent_id="agent_1", agent_type=AgentType.ORCHESTRATOR)
        
        await repo.save(agent)
        
        agent.name = "Updated Name"
        await repo.update(agent)
        
        updated = await repo.get_by_id("agent_1")
        assert updated.name == "Updated Name"
    
    @pytest.mark.asyncio
    async def test_in_memory_repository_count(self):
        """Test contar agentes."""
        repo = InMemoryAgentRepository()
        
        await repo.save(Agent(agent_id="agent_1", agent_type=AgentType.ORCHESTRATOR))
        await repo.save(Agent(agent_id="agent_2", agent_type=AgentType.ORCHESTRATOR))
        
        count = await repo.count()
        assert count == 2
    
    @pytest.mark.asyncio
    async def test_in_memory_repository_clear(self):
        """Test limpiar repositorio."""
        repo = InMemoryAgentRepository()
        
        await repo.save(Agent(agent_id="agent_1", agent_type=AgentType.ORCHESTRATOR))
        await repo.clear()
        
        count = await repo.count()
        assert count == 0


# =============================================================================
# TESTS MULTI-AGENT ORCHESTRATOR
# =============================================================================

from core.PHASE_5.epic1_orchestrator import MultiAgentOrchestrator


class TestMultiAgentOrchestrator:
    """Tests para Multi-Agent Orchestrator."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_creation(self):
        """Test creación del orquestador."""
        orchestrator = MultiAgentOrchestrator(name="TestOrchestrator")
        
        assert orchestrator.name == "TestOrchestrator"
        assert orchestrator.orchestrator_id is not None
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialize(self):
        """Test inicialización del orquestador."""
        orchestrator = MultiAgentOrchestrator()
        
        await orchestrator.initialize()
        
        assert orchestrator._initialized is True
    
    @pytest.mark.asyncio
    async def test_epic_status(self):
        """Test estado de EPICs."""
        orchestrator = MultiAgentOrchestrator()
        
        status = orchestrator.get_epic_status()
        
        assert "epic_1" in status
        assert "epic_2" in status
        assert "epic_11" in status
        assert len(status) == 11
    
    @pytest.mark.asyncio
    async def test_enable_disable_epic(self):
        """Test habilitar/deshabilitar EPIC."""
        orchestrator = MultiAgentOrchestrator()
        
        # Deshabilitar
        result = orchestrator.disable_epic("epic_2")
        assert result is True
        
        status = orchestrator.get_epic_status()
        assert status["epic_2"]["enabled"] is False
        
        # Habilitar
        result = orchestrator.enable_epic("epic_2")
        assert result is True
        
        status = orchestrator.get_epic_status()
        assert status["epic_2"]["enabled"] is True
    
    @pytest.mark.asyncio
    async def test_determine_epic_flow_biomedical(self):
        """Test flujo para tarea biomédica."""
        orchestrator = MultiAgentOrchestrator()
        
        flow = orchestrator._determine_epic_flow("biomedical_analysis")
        
        assert "epic_2" in flow
        assert "epic_11" in flow
    
    @pytest.mark.asyncio
    async def test_determine_epic_flow_diagnostic(self):
        """Test flujo para tarea diagnóstica."""
        orchestrator = MultiAgentOrchestrator()
        
        flow = orchestrator._determine_epic_flow("diagnostic_task")
        
        assert "epic_2" in flow
        assert "epic_3" in flow
        assert "epic_11" in flow
    
    @pytest.mark.asyncio
    async def test_determine_epic_flow_full(self):
        """Test flujo completo."""
        orchestrator = MultiAgentOrchestrator()
        
        flow = orchestrator._determine_epic_flow("complex_task")
        
        assert len(flow) == 10
        assert "epic_2" in flow
        assert "epic_3" in flow
        assert "epic_4" in flow
        assert "epic_5" in flow
        assert "epic_6" in flow
        assert "epic_7" in flow
        assert "epic_8" in flow
        assert "epic_9" in flow
        assert "epic_10" in flow
        assert "epic_11" in flow
    
    @pytest.mark.asyncio
    async def test_execute_task(self):
        """Test ejecución de tarea."""
        orchestrator = MultiAgentOrchestrator()
        
        result = await orchestrator.execute_task(
            task_type="diagnostic",
            input_data={"device_id": "device_123"},
        )
        
        assert "session_id" in result
        assert result["task_type"] == "diagnostic"
        assert "epics_executed" in result
        assert "results" in result
        assert "final_output" in result
    
    @pytest.mark.asyncio
    async def test_execute_task_with_full_flow(self):
        """Test ejecución con flujo completo."""
        orchestrator = MultiAgentOrchestrator()
        
        result = await orchestrator.execute_task(
            task_type="complex_analysis",
            input_data={"query": "test"},
        )
        
        assert result["success"] is True
        assert result["execution_count"] == 10
    
    @pytest.mark.asyncio
    async def test_bus_stats(self):
        """Test estadísticas del bus."""
        orchestrator = MultiAgentOrchestrator()
        
        stats = orchestrator.get_bus_stats()
        
        assert "messages_sent" in stats
        assert "messages_delivered" in stats
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test estadísticas del orquestador."""
        orchestrator = MultiAgentOrchestrator()
        
        stats = orchestrator.get_stats()
        
        assert "orchestrator_id" in stats
        assert "epics_count" in stats
        assert "enabled_epics" in stats
        assert "bus_stats" in stats


# =============================================================================
# TESTS INTEGRACIÓN COMPLETA
# =============================================================================

class TestIntegration:
    """Tests de integración completa."""
    
    @pytest.mark.asyncio
    async def test_full_system_integration(self):
        """Test integración del sistema completo."""
        # 1. Crear Gateway
        gateway = MultiPhaseGateway()
        await gateway.initialize_all()
        
        # 2. Crear Orchestrator
        orchestrator = MultiAgentOrchestrator()
        await orchestrator.initialize()
        
        # 3. Ejecutar tarea
        result = await orchestrator.execute_task(
            task_type="diagnostic",
            input_data={"device_id": "device_123"},
        )
        
        # 4. Verificar resultados
        assert result["success"] is True
        assert len(result["epics_executed"]) >= 2
        
        # 5. Verificar contexto completo
        context = await gateway.get_full_context("test query")
        assert len(context["phases_integrated"]) == 4


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
