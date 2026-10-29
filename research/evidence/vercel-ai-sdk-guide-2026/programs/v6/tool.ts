import { generateText, stepCountIs, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

export async function run() {
  return generateText({
    model: openai('gpt-4o-mini'),
    prompt: 'What is the temperature in Seoul?',
    tools: {
      weather: tool({
        description: 'Return the current temperature for a city',
        inputSchema: z.object({ city: z.string() }),
        execute: async ({ city }) => ({ city, tempC: 21 }),
      }),
    },
    stopWhen: stepCountIs(3),
  });
}
