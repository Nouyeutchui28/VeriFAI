# Setup Guide for Free Cloud AI (VeriFAI-Lite)

To use VeriFAI LLM with high-capacity cloud intelligence for free, we recommend the following providers.

## 1. Mistral AI (Highest Capacity)
Mistral offers a very generous "Experiment" plan that is perfect for students and security researchers.

- **Benefit:** 1 Billion free tokens per month.
- **Setup:**
  1. Sign up at [console.mistral.ai](https://console.mistral.ai).
  2. Verify your phone number.
  3. Create an API Key.
  4. Add it to your `.env` file:
     ```env
     MISTRAL_API_KEY=your_key_here
     ```

## 2. OpenRouter (Ultimate Flexibility)
OpenRouter is an aggregator that gives you access to many free models through a single API.

- **Benefit:** Access to `Mistral 7B`, `Llama 3`, and `Gemini` free models in one place.
- **Setup:**
  1. Sign up at [openrouter.ai](https://openrouter.ai).
  2. Go to Keys and create a new one.
  3. Add it to your `.env` file:
     ```env
     OPENROUTER_API_KEY=your_key_here
     ```

## 3. Why use these instead of Groq?
Groq has very strict limits on their trial tier. Mistral and OpenRouter provide more robust free access, especially for high-volume tasks like scanning entire projects.

## 4. Privacy Note
VeriFAI LLM includes a **Security Scrubber** that automatically redacts API keys, secrets, and emails from your code before sending them to any of these cloud providers.
