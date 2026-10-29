import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

export async function run() {
  const result = streamText({
    model: openai('gpt-4o-mini'),
    prompt: 'Say hello in one sentence.',
  });
  for await (const delta of result.textStream) {
    process.stdout.write(delta);
  }
  return await result.usage;
}
