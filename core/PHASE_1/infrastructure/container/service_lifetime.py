"""Service Lifetime for the Cognitive Dependency Injection Container.

Defines all service lifetime options.

Architecture only -- no implementations, no business logic.
"""


class ServiceLifetime:
    """Service lifetime options.

    Defines how long a service instance is kept in the container.
    """

    # Single instance for the entire application lifetime
    SINGLETON = "singleton"

    # One instance per scope
    SCOPED = "scoped"

    # New instance every time it's resolved
    TRANSIENT = "transient"

    # Factory method called every time
    FACTORY = "factory"

    # Singleton but created lazily on first use
    LAZY_SINGLETON = "lazy_singleton"

    # Weak reference singleton (garbage collected when no refs)
    WEAK_SINGLETON = "weak_singleton"

    @classmethod
    def is_valid(cls, lifetime: str) -> bool:
        """Check if a lifetime value is valid.

        Args:
            lifetime: Lifetime string to check.

        Returns:
            True if valid, False otherwise.
        """
        valid_lifetimes = {
            cls.SINGLETON,
            cls.SCOPED,
            cls.TRANSIENT,
            cls.FACTORY,
            cls.LAZY_SINGLETON,
            cls.WEAK_SINGLETON,
        }
        return lifetime in valid_lifetimes

    @classmethod
    def requires_instance_storage(cls, lifetime: str) -> bool:
        """Check if lifetime requires instance storage.

        Args:
            lifetime: Lifetime to check.

        Returns:
            True if needs storage.
        """
        return lifetime in {
            cls.SINGLETON,
            cls.LAZY_SINGLETON,
            cls.WEAK_SINGLETON,
            cls.SCOPED,
        }
