// The surface used by the published 2026-04 article, unchanged.
import { useChat } from 'ai/react';
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

export function LegacyChat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    maxSteps: 3,
  });
  return (
    <form onSubmit={handleSubmit}>
      <input value={input} onChange={handleInputChange} />
      <span>{messages.length}</span>
      <span>{isLoading ? 'loading' : 'idle'}</span>
    </form>
  );
}

export async function handler() {
  const result = streamText({
    model: openai('gpt-4o-mini'),
    system: 'You are terse.',
    prompt: 'hi',
    maxSteps: 3,
  });
  return (result as any).toDataStreamResponse();
}
