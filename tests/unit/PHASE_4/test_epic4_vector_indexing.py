"""Unit tests for EPIC 4: Vector Indexing."""

import pytest
import asyncio


class TestEPIC4Imports:
    """Tests for EPIC 4 module imports."""

    def test_import_epic4(self):
        """Test EPIC 4 module imports."""
        from core.PHASE_4.epic4_vector_indexing import (
            InMemoryQdrantClient,
            CollectionFactory,
            KnowledgePayloadBuilder,
        )
        assert InMemoryQdrantClient is not None
        assert CollectionFactory is not None

    def test_import_qdrant(self):
        """Test qdrant module imports."""
        from core.PHASE_4.epic4_vector_indexing.qdrant import (
            QdrantConfig,
            InMemoryQdrantClient,
            DistanceMetric,
        )
        assert QdrantConfig is not None
        assert InMemoryQdrantClient is not None

    def test_import_collections(self):
        """Test collections module imports."""
        from core.PHASE_4.epic4_vector_indexing.collections import (
            CollectionType,
            CollectionConfig,
            VectorCollection,
            CollectionFactory,
        )
        assert CollectionType is not None
        assert CollectionConfig is not None

    def test_import_payloads(self):
        """Test payloads module imports."""
        from core.PHASE_4.epic4_vector_indexing.payloads import (
            VectorPayload,
            KnowledgePayloadBuilder,
            PayloadSchema,
        )
        assert VectorPayload is not None
        assert KnowledgePayloadBuilder is not None


class TestQdrantClient:
    """Tests for Qdrant client."""

    def test_create_collection(self):
        """Test collection creation."""
        from core.PHASE_4.epic4_vector_indexing import InMemoryQdrantClient
        
        client = InMemoryQdrantClient()
        config = {"size": 384, "distance": "Cosine"}
        
        result = asyncio.run(client.create_collection("test", config))
        assert result is True

    def test_collection_exists(self):
        """Test collection exists check."""
        from core.PHASE_4.epic4_vector_indexing import InMemoryQdrantClient
        
        client = InMemoryQdrantClient()
        config = {"size": 384, "distance": "Cosine"}
        
        asyncio.run(client.create_collection("test", config))
        exists = asyncio.run(client.collection_exists("test"))
        assert exists is True

    def test_delete_collection(self):
        """Test collection deletion."""
        from core.PHASE_4.epic4_vector_indexing import InMemoryQdrantClient
        
        client = InMemoryQdrantClient()
        config = {"size": 384, "distance": "Cosine"}
        
        asyncio.run(client.create_collection("test", config))
        result = asyncio.run(client.delete_collection("test"))
        assert result is True
        
        exists = asyncio.run(client.collection_exists("test"))
        assert exists is False

    def test_upsert_points(self):
        """Test upsert points."""
        from core.PHASE_4.epic4_vector_indexing import InMemoryQdrantClient
        
        client = InMemoryQdrantClient()
        config = {"size": 384, "distance": "Cosine"}
        
        asyncio.run(client.create_collection("test", config))
        
        points = [
            {"id": "1", "vector": [0.1] * 384, "payload": {"text": "test"}},
            {"id": "2", "vector": [0.2] * 384, "payload": {"text": "test2"}},
        ]
        
        result = asyncio.run(client.upsert("test", points))
        assert result is True

    def test_search(self):
        """Test vector search."""
        from core.PHASE_4.epic4_vector_indexing import InMemoryQdrantClient
        
        client = InMemoryQdrantClient()
        config = {"size": 384, "distance": "Cosine"}
        
        asyncio.run(client.create_collection("test", config))
        
        # Index a point first
        points = [{"id": "1", "vector": [0.1] * 384, "payload": {"text": "test"}}]
        asyncio.run(client.upsert("test", points))
        
        # Search
        results = asyncio.run(client.search("test", [0.1] * 384, limit=10))
        assert isinstance(results, list)


class TestCollectionFactory:
    """Tests for CollectionFactory."""

    def test_create_knowledge_collection(self):
        """Test knowledge collection creation."""
        from core.PHASE_4.epic4_vector_indexing import CollectionFactory, CollectionType
        
        collection = CollectionFactory.create_knowledge_collection(
            name="medical_knowledge",
            vector_size=384,
        )
        
        assert collection.name == "medical_knowledge"
        assert collection.type == CollectionType.KNOWLEDGE
        assert collection.config.vector_size == 384
        assert collection.config.distance == "Cosine"

    def test_create_entity_collection(self):
        """Test entity collection creation."""
        from core.PHASE_4.epic4_vector_indexing import CollectionFactory, CollectionType
        
        collection = CollectionFactory.create_entity_collection(
            name="medical_entities",
            vector_size=384,
        )
        
        assert collection.name == "medical_entities"
        assert collection.type == CollectionType.ENTITIES

    def test_collection_config(self):
        """Test collection config."""
        from core.PHASE_4.epic4_vector_indexing import CollectionConfig
        
        config = CollectionConfig(
            name="test",
            vector_size=384,
            distance="Cosine",
            m=16,
            ef_construct=200,
        )
        
        assert config.name == "test"
        assert config.vector_size == 384
        assert config.m == 16


class TestPayloadBuilders:
    """Tests for payload builders."""

    def test_vector_payload_to_dict(self):
        """Test VectorPayload conversion."""
        from core.PHASE_4.epic4_vector_indexing import VectorPayload
        
        payload = VectorPayload(
            id="test_1",
            source_id="doc_123",
            text="Patient with heart failure",
            domain="cardiology",
            icd_codes=["I50"],
        )
        
        data = payload.to_dict()
        
        assert data["id"] == "test_1"
        assert data["source_id"] == "doc_123"
        assert data["text"] == "Patient with heart failure"
        assert data["icd_codes"] == ["I50"]

    def test_vector_payload_from_dict(self):
        """Test VectorPayload creation from dict."""
        from core.PHASE_4.epic4_vector_indexing import VectorPayload
        
        data = {
            "id": "test_1",
            "source_id": "doc_123",
            "text": "Test text",
            "domain": "cardiology",
        }
        
        payload = VectorPayload.from_dict(data)
        
        assert payload.id == "test_1"
        assert payload.text == "Test text"

    def test_knowledge_payload_builder(self):
        """Test KnowledgePayloadBuilder."""
        from core.PHASE_4.epic4_vector_indexing import KnowledgePayloadBuilder
        
        builder = KnowledgePayloadBuilder()
        
        payload = builder.build({
            "source_id": "doc_123",
            "text": "Clinical study about diabetes",
            "domain": "endocrinology",
        })
        
        assert payload.source_id == "doc_123"
        assert payload.text == "Clinical study about diabetes"
        assert payload.domain == "endocrinology"
        assert payload.quality_score == 0.8

    def test_payload_validation(self):
        """Test payload validation."""
        from core.PHASE_4.epic4_vector_indexing import KnowledgePayloadBuilder
        
        builder = KnowledgePayloadBuilder()
        
        # Valid payload
        valid_payload = builder.build({
            "source_id": "doc_123",
            "text": "Valid text",
        })
        assert builder.validate(valid_payload) is True
        
        # Invalid: empty text
        invalid_payload = builder.build({
            "source_id": "doc_123",
            "text": "",
        })
        assert builder.validate(invalid_payload) is False


class TestPayloadSchema:
    """Tests for PayloadSchema."""

    def test_knowledge_schema(self):
        """Test knowledge schema."""
        from core.PHASE_4.epic4_vector_indexing import PayloadSchema
        
        schema = PayloadSchema.get_knowledge_schema()
        
        assert "id" in schema
        assert "text" in schema
        assert "domain" in schema
        assert "icd_codes" in schema

    def test_entity_schema(self):
        """Test entity schema."""
        from core.PHASE_4.epic4_vector_indexing import PayloadSchema
        
        schema = PayloadSchema.get_entity_schema()
        
        assert "id" in schema
        assert "text" in schema
        assert "entity_type" in schema


class TestCollectionTypes:
    """Tests for collection types."""

    def test_collection_types(self):
        """Test collection type enum."""
        from core.PHASE_4.epic4_vector_indexing import CollectionType
        
        assert CollectionType.KNOWLEDGE_ARTICLES.value == "knowledge_articles"
        assert CollectionType.ENTITIES.value == "entities"
        
    def test_index_types(self):
        """Test index type enum."""
        from core.PHASE_4.epic4_vector_indexing import IndexType
        
        assert IndexType.HNSW.value == "hnsw"
        assert IndexType.FLAT.value == "flat"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
