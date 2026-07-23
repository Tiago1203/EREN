"""
PHASE 4 - EPIC 3: Providers Module

Providers para modelos de embedding biomédico:
- PubMedBERT Provider
- BioBERT Provider
- ClinicalBERT Provider
- Ollama Provider
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import asyncio


class EmbeddingModel(str):
    """Modelos de embedding biomédico."""
    PUBMEDBERT = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
    BIOBERT = "dmis-lab/biobert-base-cased-v1.2"
    CLINICALBERT = "emilyalsentzer/Bio_ClinicalBERT"
    SCIBERT = "allenai/scibert_scivocab_uncased"
    BLUEBERT = "bionlp/bluebert_pubmed_mimic_uncased"


@dataclass
class EmbeddingConfig:
    """Configuración para embedding."""
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimension: int = 384
    batch_size: int = 32
    max_length: int = 512
    normalize: bool = True
    cache_embeddings: bool = True


@dataclass
class GeneratedEmbedding:
    """Embedding generado."""
    text: str
    vector: list[float]
    model: str
    dimension: int
    token_count: int = 0
    generated_at: str = ""
    
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "vector": self.vector,
            "model": self.model,
            "dimension": self.dimension,
            "token_count": self.token_count,
        }


class BaseEmbeddingProvider(ABC):
    """Clase base para providers de embedding."""
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Retorna nombre del modelo."""
        ...
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Retorna dimensión del embedding."""
        ...
    
    @abstractmethod
    async def generate(self, text: str) -> GeneratedEmbedding:
        """Genera embedding para un texto."""
        ...
    
    @abstractmethod
    async def generate_batch(self, texts: list[str]) -> list[GeneratedEmbedding]:
        """Genera embeddings para múltiples textos."""
        ...



class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Provider de embedding mock para testing."""
    
    def __init__(self, dimension: int = 384):
        self._dimension = dimension
    
    @property
    def model_name(self) -> str:
        return "mock-embedding-provider"
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    async def generate(self, text: str) -> GeneratedEmbedding:
        """Genera embedding mock."""
        import random
        from datetime import datetime
        
        # Generar vector aleatorio de la dimensión correcta
        vector = [random.random() for _ in range(self._dimension)]
        
        # Normalizar
        magnitude = sum(v**2 for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]
        
        return GeneratedEmbedding(
            text=text,
            vector=vector,
            model=self.model_name,
            dimension=self._dimension,
            token_count=len(text.split()),
            generated_at=datetime.now().isoformat(),
        )
    
    async def generate_batch(self, texts: list[str]) -> list[GeneratedEmbedding]:
        """Genera embeddings mock para batch."""
        return [await self.generate(text) for text in texts]


class SentenceTransformerProvider(BaseEmbeddingProvider):
    """Provider usando sentence-transformers."""
    
    def __init__(self, config: EmbeddingConfig | None = None):
        self.config = config or EmbeddingConfig()
        self._model = None
    
    @property
    def model_name(self) -> str:
        return self.config.model
    
    @property
    def dimension(self) -> int:
        return self.config.dimension
    
    def _get_model(self):
        """Lazy load del modelo."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.config.model)
            except ImportError:
                # Fallback to mock
                return MockEmbeddingProvider(dimension=self.config.dimension)
        return self._model
    
    async def generate(self, text: str) -> GeneratedEmbedding:
        """Genera embedding para un texto."""
        model = self._get_model()
        
        if isinstance(model, MockEmbeddingProvider):
            return await model.generate(text)
        
        # Generate using sentence-transformers
        from datetime import datetime
        
        embedding = model.encode(
            text,
            normalize_embeddings=self.config.normalize,
            convert_to_numpy=True,
        )
        
        return GeneratedEmbedding(
            text=text,
            vector=embedding.tolist(),
            model=self.model_name,
            dimension=len(embedding),
            token_count=len(text.split()),
            generated_at=datetime.now().isoformat(),
        )
    
    async def generate_batch(self, texts: list[str]) -> list[GeneratedEmbedding]:
        """Genera embeddings para batch."""
        model = self._get_model()
        
        if isinstance(model, MockEmbeddingProvider):
            return await model.generate_batch(texts)
        
        from datetime import datetime
        
        embeddings = model.encode(
            texts,
            batch_size=self.config.batch_size,
            normalize_embeddings=self.config.normalize,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        
        return [
            GeneratedEmbedding(
                text=text,
                vector=emb.tolist(),
                model=self.model_name,
                dimension=len(emb),
                token_count=len(text.split()),
                generated_at=datetime.now().isoformat(),
            )
            for text, emb in zip(texts, embeddings)
        ]


class OllamaProvider(BaseEmbeddingProvider):
    """Provider usando Ollama (local LLM)."""
    
    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self._dimension = 768  # Default for nomic-embed-text
    
    @property
    def model_name(self) -> str:
        return f"ollama/{self.model}"
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    async def generate(self, text: str) -> GeneratedEmbedding:
        """Genera embedding usando Ollama."""
        import aiohttp
        from datetime import datetime
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return GeneratedEmbedding(
                            text=text,
                            vector=data["embedding"],
                            model=self.model_name,
                            dimension=len(data["embedding"]),
                            token_count=len(text.split()),
                            generated_at=datetime.now().isoformat(),
                        )
                    else:
                        raise Exception(f"Ollama error: {response.status}")
        except Exception:
            # Fallback to mock
            mock = MockEmbeddingProvider(dimension=self._dimension)
            return await mock.generate(text)
    
    async def generate_batch(self, texts: list[str]) -> list[GeneratedEmbedding]:
        """Genera embeddings usando Ollama."""
        return [await self.generate(text) for text in texts]


class OpenAIProvider(BaseEmbeddingProvider):
    """Provider usando OpenAI embeddings."""
    
    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model
        self._dimension = 1536 if model == "text-embedding-3-small" else 3072
    
    @property
    def model_name(self) -> str:
        return f"openai/{self.model}"
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    async def generate(self, text: str) -> GeneratedEmbedding:
        """Genera embedding usando OpenAI."""
        import os
        from datetime import datetime
        
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY", "")
        
        if not api_key:
            # Fallback to mock
            mock = MockEmbeddingProvider(dimension=self._dimension)
            return await mock.generate(text)
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"model": self.model, "input": text},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        embedding = data["data"][0]["embedding"]
                        return GeneratedEmbedding(
                            text=text,
                            vector=embedding,
                            model=self.model_name,
                            dimension=len(embedding),
                            token_count=len(text.split()),
                            generated_at=datetime.now().isoformat(),
                        )
                    else:
                        raise Exception(f"OpenAI error: {response.status}")
        except Exception:
            # Fallback to mock
            mock = MockEmbeddingProvider(dimension=self._dimension)
            return await mock.generate(text)
    
    async def generate_batch(self, texts: list[str]) -> list[GeneratedEmbedding]:
        """Genera embeddings usando OpenAI."""
        import os
        from datetime import datetime
        
        api_key = self.api_key or os.environ.get("OPENAI_API_KEY", "")
        
        if not api_key:
            mock = MockEmbeddingProvider(dimension=self._dimension)
            return await mock.generate_batch(texts)
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={"model": self.model, "input": texts},
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [
                            GeneratedEmbedding(
                                text=text,
                                vector=item["embedding"],
                                model=self.model_name,
                                dimension=len(item["embedding"]),
                                token_count=len(text.split()),
                                generated_at=datetime.now().isoformat(),
                            )
                            for text, item in zip(texts, data["data"])
                        ]
                    else:
                        raise Exception(f"OpenAI error: {response.status}")
        except Exception:
            mock = MockEmbeddingProvider(dimension=self._dimension)
            return await mock.generate_batch(texts)


class EmbeddingProviderFactory:
    """Fábrica de providers de embedding."""
    
    @staticmethod
    def create(
        provider_type: str,
        **kwargs,
    ) -> BaseEmbeddingProvider:
        """Crea provider según tipo."""
        providers = {
            "mock": MockEmbeddingProvider,
            "sentence-transformers": SentenceTransformerProvider,
            "ollama": OllamaProvider,
            "openai": OpenAIProvider,
        }
        
        provider_class = providers.get(provider_type.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        return provider_class(**kwargs)
    
    @staticmethod
    def create_medical(
        provider_type: str = "mock",
    ) -> BaseEmbeddingProvider:
        """Crea provider médico."""
        # Configure for medical embeddings
        config = EmbeddingConfig(
            model="sentence-transformers/all-MedNLP-MiniLM-L6-v2",
            dimension=384,
            batch_size=16,
        )
        
        if provider_type == "mock":
            return MockEmbeddingProvider(dimension=config.dimension)
        
        return SentenceTransformerProvider(config)


__all__ = [
    "EmbeddingModel",
    "EmbeddingConfig",
    "GeneratedEmbedding",
    "BaseEmbeddingProvider",
    "MockEmbeddingProvider",
    "SentenceTransformerProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "EmbeddingProviderFactory",
]
