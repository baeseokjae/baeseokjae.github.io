'use client';
import { useChat } from '@ai-sdk/react';

export function Chat() {
  const { messages, sendMessage, status } = useChat();
  return (
    <div>
      {messages.map((m) => (
        <p key={m.id}>{m.id}</p>
      ))}
      <span>{status}</span>
      <button onClick={() => sendMessage({ text: 'Hello' })}>Send</button>
    </div>
  );
}
