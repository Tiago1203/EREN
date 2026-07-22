"""Conversation Controller - Main interface for conversation management."""
from dataclasses import dataclass
from typing import AsyncIterator, Any
from uuid import UUID

from core.PHASE_2.cognitive.conversation.domain.entities import (
    Conversation,
    Message,
    ConversationId,
    MessageId,
    ConversationStatus,
    MessageRole,
)
from core.PHASE_2.cognitive.conversation.infrastructure.redis_store import RedisConversationStore


@dataclass
class ConversationControllerConfig:
    """Configuration for conversation controller."""
    max_history: int = 50
    session_timeout: int = 1800  # 30 minutes


class ConversationController:
    """
    Main interface for conversation management.
    
    Handles:
    - Conversation lifecycle (create, end, archive)
    - Message sending and receiving
    - History retrieval
    - Session management
    """
    
    def __init__(
        self,
        store: RedisConversationStore,
        cognitive_runtime: Any,  # CognitiveRuntime
        config: ConversationControllerConfig | None = None,
    ):
        self.store = store
        self.cognitive_runtime = cognitive_runtime
        self.config = config or ConversationControllerConfig()
    
    async def create_conversation(
        self,
        user_id: UUID,
        tenant_id: UUID,
        session_id: UUID,
        primary_domain: str = "biomedical",
    ) -> Conversation:
        """
        Create a new conversation.
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            session_id: Session ID
            primary_domain: Primary domain (biomedical, clinical, hospital)
        
        Returns:
            Created conversation
        """
        conversation = Conversation.create(
            tenant_id=tenant_id,
            user_id=user_id,
            session_id=session_id,
            primary_domain=primary_domain,
        )
        
        # Save to store
        await self.store.save_conversation(conversation)
        
        # Create session
        await self.store.create_session(conversation.id, user_id)
        
        return conversation
    
    async def send_message(
        self,
        conversation_id: ConversationId,
        content: str,
        user_id: UUID,
    ) -> tuple[Message, str]:
        """
        Send a message and get AI response.
        
        Args:
            conversation_id: Conversation ID
            content: Message content
            user_id: User ID
        
        Returns:
            Tuple of (user_message, ai_response)
        """
        # Get conversation
        conversation = await self.store.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        # Create user message
        user_message = Message.create(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=content,
        )
        
        # Save user message
        await self.store.save_message(conversation_id, user_message)
        
        # Update conversation
        conversation.add_message()
        await self.store.save_conversation(conversation)
        
        # Get AI response
        from core.PHASE_2.cognitive.runtime import ProcessingContext
        
        context = ProcessingContext(
            conversation_id=conversation_id.value,
            user_id=user_id,
            tenant_id=conversation.tenant_id,
            message=content,
            domain=conversation.primary_domain,
        )
        
        result = await self.cognitive_runtime.process_message(context)
        
        if result.blocked:
            ai_response = f"[Bloqueado] {result.block_reason}"
        elif result.error:
            ai_response = f"[Error] {result.error}"
        else:
            ai_response = result.response or ""
        
        # Create AI message
        ai_message = Message.create(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=ai_response,
        )
        ai_message.confidence = result.confidence or 0.0
        
        # Save AI message
        await self.store.save_message(conversation_id, ai_message)
        
        # Update conversation confidence
        conversation.update_confidence(result.confidence or 0.0)
        await self.store.save_conversation(conversation)
        
        return user_message, ai_message
    
    async def send_message_stream(
        self,
        conversation_id: ConversationId,
        content: str,
        user_id: UUID,
    ) -> AsyncIterator[str]:
        """
        Send a message with streaming response.
        
        Args:
            conversation_id: Conversation ID
            content: Message content
            user_id: User ID
        
        Yields:
            Response chunks
        """
        # Get conversation
        conversation = await self.store.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        # Create user message
        user_message = Message.create(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=content,
        )
        
        # Save user message
        await self.store.save_message(conversation_id, user_message)
        
        # Process with streaming
        from core.PHASE_2.cognitive.runtime import ProcessingContext
        
        context = ProcessingContext(
            conversation_id=conversation_id.value,
            user_id=user_id,
            tenant_id=conversation.tenant_id,
            message=content,
            domain=conversation.primary_domain,
        )
        
        async for chunk in self.cognitive_runtime.process_message_stream(context):
            yield chunk
    
    async def get_conversation(
        self,
        conversation_id: ConversationId,
    ) -> Conversation | None:
        """Get a conversation by ID."""
        return await self.store.get_conversation(conversation_id)
    
    async def get_history(
        self,
        conversation_id: ConversationId,
        limit: int = 50,
    ) -> list[Message]:
        """Get message history."""
        return await self.store.get_message_history(conversation_id, limit)
    
    async def end_conversation(
        self,
        conversation_id: ConversationId,
    ) -> Conversation:
        """End a conversation."""
        conversation = await self.store.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        conversation.end()
        await self.store.save_conversation(conversation)
        
        return conversation
    
    async def archive_conversation(
        self,
        conversation_id: ConversationId,
    ) -> None:
        """Archive a conversation (move to cold storage)."""
        conversation = await self.store.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")
        
        conversation.status = ConversationStatus.ARCHIVED
        await self.store.save_conversation(conversation)
    
    async def get_active_conversations(
        self,
        user_id: UUID,
    ) -> list[Conversation]:
        """Get all active conversations for a user."""
        conversation_ids = await self.store.get_active_conversations(user_id)
        
        conversations = []
        for conv_id in conversation_ids:
            conv = await self.store.get_conversation(conv_id)
            if conv:
                conversations.append(conv)
        
        return conversations
    
    async def refresh_session(
        self,
        conversation_id: ConversationId,
    ) -> None:
        """Refresh session TTL."""
        await self.store.refresh_session(conversation_id)
    
    async def add_feedback(
        self,
        message_id: MessageId,
        conversation_id: ConversationId,
        feedback: str,
    ) -> None:
        """Add user feedback to a message."""
        history = await self.store.get_message_history(conversation_id)
        
        for msg in history:
            if msg.id == message_id:
                msg.user_feedback = feedback
                await self.store.save_message(conversation_id, msg)
                break


# Factory function
def create_conversation_controller(
    redis_url: str,
    cognitive_runtime: Any,
) -> ConversationController:
    """Create a conversation controller."""
    from core.PHASE_2.cognitive.conversation.infrastructure.redis_store import create_redis_conversation_store
    
    store = create_redis_conversation_store(redis_url)
    
    return ConversationController(
        store=store,
        cognitive_runtime=cognitive_runtime,
    )
