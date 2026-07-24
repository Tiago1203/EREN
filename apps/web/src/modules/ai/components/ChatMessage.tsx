'use client';

import type { ChatMessage as ChatMessageType } from '../types/ai.types';

interface ChatMessageProps {
  message: ChatMessageType;
  showTimestamp?: boolean;
  showAgent?: boolean;
}

export function ChatMessage({ message, showTimestamp = true, showAgent = true }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg p-4 ${
          isUser
            ? 'bg-[var(--primary)] text-white'
            : 'bg-[var(--card)] border border-[var(--border)]'
        }`}
      >
        {/* Agent info */}
        {showAgent && isAssistant && message.agentName && (
          <div className="flex items-center gap-2 mb-2 pb-2 border-b border-[var(--border)]">
            <div className="w-6 h-6 rounded-full bg-[var(--primary)] flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <span className="text-sm font-medium">{message.agentName}</span>
            {message.confidence !== undefined && (
              <ConfidenceBadge confidence={message.confidence} />
            )}
          </div>
        )}

        {/* Message content */}
        <div className="prose prose-sm max-w-none">
          {message.content.split('\n').map((line, i) => (
            <p key={i} className={i > 0 ? 'mt-2' : ''}>{line}</p>
          ))}
        </div>

        {/* Error */}
        {message.error && (
          <div className="mt-2 p-2 bg-red-100 text-red-700 rounded text-sm">
            Error: {message.error}
          </div>
        )}

        {/* Recommendations */}
        {message.recommendations && message.recommendations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-[var(--border)]">
            <p className="text-sm font-medium mb-2">Recomendaciones:</p>
            <div className="space-y-2">
              {message.recommendations.map((rec) => (
                <div key={rec.id} className="p-2 bg-[var(--background)] rounded">
                  <p className="font-medium text-sm">{rec.title}</p>
                  <p className="text-xs text-muted">{rec.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-4 border-t border-[var(--border)]">
            <p className="text-sm font-medium mb-2">Fuentes:</p>
            <ul className="space-y-1">
              {message.sources.map((source) => (
                <li key={source.id} className="text-xs text-muted">
                  • {source.title}
                  {source.relevance && ` (${(source.relevance * 100).toFixed(0)}%)`}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Uncertainty */}
        {message.uncertainty && (
          <UncertaintyBadge uncertainty={message.uncertainty} />
        )}

        {/* Timestamp */}
        {showTimestamp && (
          <div className={`text-xs mt-2 ${isUser ? 'text-blue-100' : 'text-muted'}`}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        )}
      </div>
    </div>
  );
}

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const color = confidence >= 0.8 ? 'bg-green-500' : confidence >= 0.5 ? 'bg-yellow-500' : 'bg-red-500';
  return (
    <span className={`${color} text-white text-xs px-2 py-0.5 rounded-full`}>
      {(confidence * 100).toFixed(0)}%
    </span>
  );
}

function UncertaintyBadge({ uncertainty }: { uncertainty: ChatMessageType['uncertainty'] }) {
  if (!uncertainty) return null;

  const colors = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
    unknown: 'bg-gray-100 text-gray-800',
  };

  return (
    <div className={`mt-3 p-2 rounded text-xs ${colors[uncertainty.level]}`}>
      <div className="flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>Incertidumbre: {uncertainty.message}</span>
      </div>
      {uncertainty.factors.length > 0 && (
        <ul className="mt-1 pl-4 list-disc">
          {uncertainty.factors.map((factor, i) => (
            <li key={i}>{factor}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default ChatMessage;
