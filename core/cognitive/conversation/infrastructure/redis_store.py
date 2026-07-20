"""Redis-based Conversation Store."""
import json
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from core.cognitive.conversation.domain.entities import (
    Conversation,
    Message,
    ConversationId,
    MessageId,
    ConversationStatus,
    MessageRole,
)


class RedisConversationStore:
    """Conversation store using Redis."""
    
    # TTL settings
    SESSION_TTL = 1800  # 30 minutes
    MESSAGE_TTL = 86400  # 24 hours
    
    def __init__(self, redis_client: Any):
        """
        Initialize the conversation store.
        
        Args:
            redis_client: Redis async client (redis.asyncio.Redis)
        """
        self.redis = redis_client
    
    # Conversation methods
    async def save_conversation(self, conversation: Conversation) -> None:
        """Save a conversation."""
        key = f"conversation:{conversation.id.value}"
        data = {
            "id": str(conversation.id.value),
            "tenant_id": str(conversation.tenant_id),
            "user_id": str(conversation.user_id),
            "session_id": str(conversation.session_id),
            "status": conversation.status.value,
            "primary_domain": conversation.primary_domain,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "ended_at": conversation.ended_at.isoformat() if conversation.ended_at else None,
            "message_count": conversation.message_count,
            "average_confidence": conversation.average_confidence,
        }
        await self.redis.setex(key, self.SESSION_TTL, json.dumps(data))
    
    async def get_conversation(self, conversation_id: ConversationId) -> Conversation | None:
        """Get a conversation by ID."""
        key = f"conversation:{conversation_id.value}"
        data = await self.redis.get(key)
        
        if not data:
            return None
        
        conv_data = json.loads(data)
        
        return Conversation(
            id=ConversationId(UUID(conv_data["id"])),
            tenant_id=UUID(conv_data["tenant_id"]),
            user_id=UUID(conv_data["user_id"]),
            session_id=UUID(conv_data["session_id"]),
            status=ConversationStatus(conv_data["status"]),
            primary_domain=conv_data["primary_domain"],
            created_at=datetime.fromisoformat(conv_data["created_at"]),
            updated_at=datetime.fromisoformat(conv_data["updated_at"]),
            ended_at=datetime.fromisoformat(conv_data["ended_at"]) if conv_data["ended_at"] else None,
            message_count=conv_data["message_count"],
            average_confidence=conv_data["average_confidence"],
        )
    
    async def delete_conversation(self, conversation_id: ConversationId) -> None:
        """Delete a conversation."""
        key = f"conversation:{conversation_id.value}"
        await self.redis.delete(key)
        
        # Also delete message history
        history_key = f"conversation:{conversation_id.value}:history"
        await self.redis.delete(history_key)
    
    # Message methods
    async def save_message(self, conversation_id: ConversationId, message: Message) -> None:
        """Save a message to conversation history."""
        key = f"conversation:{conversation_id.value}:history"
        
        data = {
            "id": str(message.id.value),
            "conversation_id": str(message.conversation_id.value),
            "role": message.role.value,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
            "latency_ms": message.latency_ms,
            "confidence": message.confidence,
            "tokens_used": message.tokens_used,
            "reasoning_steps": message.reasoning_steps,
            "user_feedback": message.user_feedback,
        }
        
        # Add to list
        await self.redis.rpush(key, json.dumps(data))
        
        # Trim to max 50 messages
        await self.redis.ltrim(key, -50, -1)
        
        # Set TTL
        await self.redis.expire(key, self.MESSAGE_TTL)
        
        # Refresh conversation TTL
        conv_key = f"conversation:{conversation_id.value}"
        await self.redis.expire(conv_key, self.SESSION_TTL)
    
    async def get_message_history(
        self,
        conversation_id: ConversationId,
        limit: int = 50,
    ) -> list[Message]:
        """Get message history for a conversation."""
        key = f"conversation:{conversation_id.value}:history"
        
        # Get last N messages
        messages_data = await self.redis.lrange(key, -limit, -1)
        
        messages = []
        for msg_data in messages_data:
            data = json.loads(msg_data)
            messages.append(Message(
                id=MessageId(UUID(data["id"])),
                conversation_id=ConversationId(UUID(data["conversation_id"])),
                role=MessageRole(data["role"]),
                content=data["content"],
                created_at=datetime.fromisoformat(data["created_at"]),
                latency_ms=data["latency_ms"],
                confidence=data["confidence"],
                tokens_used=data["tokens_used"],
                reasoning_steps=data["reasoning_steps"],
                user_feedback=data["user_feedback"],
            ))
        
        return messages
    
    # Session methods
    async def create_session(
        self,
        conversation_id: ConversationId,
        user_id: UUID,
        metadata: dict | None = None,
    ) -> None:
        """Create a new session."""
        key = f"session:{conversation_id.value}"
        data = {
            "user_id": str(user_id),
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        await self.redis.setex(key, self.SESSION_TTL, json.dumps(data))
    
    async def refresh_session(self, conversation_id: ConversationId) -> None:
        """Refresh session TTL."""
        key = f"conversation:{conversation_id.value}"
        await self.redis.expire(key, self.SESSION_TTL)
        
        session_key = f"session:{conversation_id.value}"
        await self.redis.expire(session_key, self.SESSION_TTL)
    
    # Utility methods
    async def get_active_conversations(self, user_id: UUID) -> list[ConversationId]:
        """Get active conversations for a user."""
        pattern = "conversation:*"
        keys = await self.redis.keys(pattern)
        
        conversations = []
        for key in keys:
            data = await self.redis.get(key)
            if data:
                conv_data = json.loads(data)
                if (
                    UUID(conv_data["user_id"]) == user_id
                    and conv_data["status"] == ConversationStatus.ACTIVE.value
                ):
                    conversations.append(ConversationId(UUID(conv_data["id"])))
        
        return conversations


# Factory function
def create_redis_conversation_store(redis_url: str) -> RedisConversationStore:
    """Create a Redis conversation store."""
    import redis.asyncio as redis
    return RedisConversationStore(redis.from_url(redis_url))
