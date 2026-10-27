# Optional Cloud AI Setup

Local Ollama is the default and requires no API key. Cloud inference is optional and requires a provider credential supplied through the process environment. Do not put credentials in project files or commit them.

## 1. Mistral AI (Highest Capacity)
Mistral offers a very generous "Experiment" plan that is perfect for students and security researchers.

- **Benefit:** 1 Billion free tokens per month.
- **Setup:**
  1. Sign up at [console.mistral.ai](https://console.mistral.ai).
  2. Verify your phone number.
  3. Create an API Key.
  4. Configure a supported provider (`METERLESS_API_KEY`, `NIGHTSHIFT_API_KEY`, or `GROQ_API_KEY`) through your deployment's secret manager and explicitly set `LLM_PROVIDER=cloud`. Mistral is not currently a configured provider.

## 2. OpenRouter (Ultimate Flexibility)
OpenRouter is an aggregator that gives you access to many free models through a single API.

- **Benefit:** Access to `Mistral 7B`, `Llama 3`, and `Gemini` free models in one place.
- **Setup:**
  1. Sign up at [openrouter.ai](https://openrouter.ai).
  2. Go to Keys and create a new one.
  3. Supply the OpenRouter credential as `GROQ_API_KEY` through your deployment's secret manager and set `LLM_PROVIDER=cloud`. Do not create a project `.env` file.

## 3. Why use these instead of Groq?
Groq has very strict limits on their trial tier. Mistral and OpenRouter provide more robust free access, especially for high-volume tasks like scanning entire projects.

## 4. Privacy Note
VeriFAI LLM includes a **Security Scrubber** that automatically redacts API keys, secrets, and emails from your code before sending them to any of these cloud providers.
