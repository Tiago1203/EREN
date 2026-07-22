"""AI Exceptions - Jerarquía de excepciones del AI Core."""

from __future__ import annotations


class AIError(Exception):
    """Base exception para todos los errores del AI Core."""

    def __init__(self, message: str, code: str = "AI_ERROR", **kwargs) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = kwargs


class AIConfigurationError(AIError):
    """Error de configuración del AI Core."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, code="CONFIG_ERROR", **kwargs)


class AIProviderError(AIError):
    """Error relacionado con el proveedor de IA."""

    def __init__(self, message: str, provider: str = "", **kwargs) -> None:
        super().__init__(message, code="PROVIDER_ERROR", **kwargs)
        self.provider = provider


class AIProviderNotFoundError(AIProviderError):
    """Proveedor de IA no encontrado."""

    def __init__(self, provider: str) -> None:
        super().__init__(f"Provider not found: {provider}", provider=provider)
        self.code = "PROVIDER_NOT_FOUND"


class AIModelError(AIError):
    """Error relacionado con el modelo de IA."""

    def __init__(self, message: str, model: str = "", **kwargs) -> None:
        super().__init__(message, code="MODEL_ERROR", **kwargs)
        self.model = model


class AIModelNotFoundError(AIModelError):
    """Modelo de IA no encontrado."""

    def __init__(self, model: str) -> None:
        super().__init__(f"Model not found: {model}", model=model)
        self.code = "MODEL_NOT_FOUND"


class AIContextError(AIError):
    """Error relacionado con el contexto de IA."""

    def __init__(self, message: str, **kwargs) -> None:
        super().__init__(message, code="CONTEXT_ERROR", **kwargs)


class AIValidationError(AIError):
    """Error de validación."""

    def __init__(self, message: str, field: str = "", **kwargs) -> None:
        super().__init__(message, code="VALIDATION_ERROR", **kwargs)
        self.field = field


class AIInjectionError(AIError):
    """Error de inyección de dependencias."""

    def __init__(self, message: str, dependency: str = "", **kwargs) -> None:
        super().__init__(message, code="INJECTION_ERROR", **kwargs)
        self.dependency = dependency


class AIInitializationError(AIError):
    """Error de inicialización del AI Core."""

    def __init__(self, message: str, component: str = "", **kwargs) -> None:
        super().__init__(message, code="INIT_ERROR", **kwargs)
        self.component = component


class AIProcessingError(AIError):
    """Error durante el procesamiento de una request."""

    def __init__(self, message: str, request_id: str = "", **kwargs) -> None:
        super().__init__(message, code="PROCESSING_ERROR", **kwargs)
        self.request_id = request_id


class AITimeoutError(AIError):
    """Timeout en operación de IA."""

    def __init__(self, message: str, operation: str = "", timeout_ms: int = 0, **kwargs) -> None:
        super().__init__(message, code="TIMEOUT_ERROR", **kwargs)
        self.operation = operation
        self.timeout_ms = timeout_ms


class AIRateLimitError(AIProviderError):
    """Rate limit excedido."""

    def __init__(self, provider: str, retry_after: int = 0) -> None:
        super().__init__(
            f"Rate limit exceeded for provider: {provider}",
            provider=provider,
        )
        self.code = "RATE_LIMIT_ERROR"
        self.retry_after = retry_after


class AIAuthenticationError(AIProviderError):
    """Error de autenticación con el proveedor."""

    def __init__(self, provider: str, message: str = "Authentication failed") -> None:
        super().__init__(message, provider=provider)
        self.code = "AUTH_ERROR"


class AIQuotaExceededError(AIProviderError):
    """Cuota excedida con el proveedor."""

    def __init__(self, provider: str, quota_type: str = "") -> None:
        super().__init__(
            f"Quota exceeded for {quota_type} on provider: {provider}",
            provider=provider,
        )
        self.code = "QUOTA_EXCEEDED"
        self.quota_type = quota_type
