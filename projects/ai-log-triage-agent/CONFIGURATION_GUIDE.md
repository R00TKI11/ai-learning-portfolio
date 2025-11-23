# Configuration Guide

This guide explains how to configure the AI Log Triage Agent.

---

## Quick Start

1. Copy the example configuration file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your required values:
   ```env
   LLM_API_KEY=your-api-key-here
   LLM_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
   LLM_DEFAULT_MODEL=your-preferred-model
   ```

3. Test your configuration:
   ```bash
   python -c "from src.ai_log_triage.config import settings; print(f'Configured: {settings.is_configured()}')"
   ```

---

## Configuration Reference

### Required Settings

These settings **must** be configured for the application to work:

| Setting | Description | Example |
|---------|-------------|---------|
| `LLM_API_KEY` | Your LLM API key | `sk-...` |
| `LLM_ENDPOINT` | API endpoint URL | `https://openrouter.ai/api/v1/chat/completions` |
| `LLM_DEFAULT_MODEL` | Default model identifier | `deepseek/deepseek-r1:free` |

### Optional Settings

These settings have sensible defaults but can be customized:

| Setting | Default | Description |
|---------|---------|-------------|
| `LLM_TIMEOUT` | `120` | Request timeout in seconds |
| `LLM_MAX_TOKENS` | `1024` | Maximum tokens in LLM responses |
| `DATA_DIR` | `./data` | Directory containing log files |

---

## Provider-Specific Examples

### OpenRouter

```env
LLM_API_KEY=sk-or-v1-...
LLM_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
LLM_DEFAULT_MODEL=deepseek/deepseek-r1:free
```

Available models (free tier):
- `deepseek/deepseek-r1:free`
- `x-ai/grok-2-1212:free`
- Many others - check [OpenRouter models](https://openrouter.ai/models)

### OpenAI

```env
LLM_API_KEY=sk-proj-...
LLM_ENDPOINT=https://api.openai.com/v1/chat/completions
LLM_DEFAULT_MODEL=gpt-4-turbo-preview
```

### Anthropic (via OpenRouter)

```env
LLM_API_KEY=sk-or-v1-...
LLM_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
LLM_DEFAULT_MODEL=anthropic/claude-3-5-sonnet
```

### Local LLM (Ollama)

```env
LLM_API_KEY=not-needed
LLM_ENDPOINT=http://localhost:11434/v1/chat/completions
LLM_DEFAULT_MODEL=llama2
LLM_TIMEOUT=300  # Local models might be slower
```

---

## Configuration Profiles

Configuration profiles provide pre-configured settings for different use cases. Profiles are stored in the `profiles/` directory as YAML files.

### Using Profiles

**CLI:**
```bash
# Use fast profile (Claude 3 Haiku, 512 tokens, 30s timeout)
ai-log-triage --input data/app.log --profile fast

# Use accurate profile (Claude 3.5 Sonnet, 2048 tokens, 120s timeout)
ai-log-triage --input data/error.log --profile accurate

# Use local LLM profile
ai-log-triage --input data/auth.log --profile local

# Use experimental profile
ai-log-triage --input data/test.log --profile experimental

# Override model from profile
ai-log-triage --input data/app.log --profile fast --model gpt-4
```

**Python API:**
```python
from ai_log_triage.config import settings

# Load a profile
settings.load_profile('accurate')

# Profile settings are now active
from ai_log_triage.triage_agent import TriageAgent
agent = TriageAgent()  # Uses settings from profile
```

### Available Profiles

| Profile | Use Case | Model | Max Tokens | Timeout |
|---------|----------|-------|------------|---------|
| `fast` | Quick analysis, batch processing, development | From environment | 512 | 30s |
| `accurate` | Production incidents, complex analysis | From environment | 2048 | 120s |
| `local` | Privacy-sensitive, offline operation | From environment | 1024 | 180s |
| `experimental` | Testing new models | From environment | 1024 | 90s |

**Note:** All profiles use your configured model from environment settings by default. You can uncomment the `model` line in any profile file to override it for that specific profile.

### Creating Custom Profiles

Create a new YAML file in `profiles/`:

```yaml
# profiles/my-custom.yaml
name: my-custom
description: My custom configuration

llm:
  model: your-model-identifier
  max_tokens: 1024
  timeout: 60
  temperature: 0.5

  # Optional: Override endpoint
  endpoint: https://custom-api.example.com/v1/chat

  # Optional: Override API key
  api_key: your-api-key-here

# Application settings
truncate_logs: true
max_log_length: 5000
```

### Configuration Priority

Configuration is loaded in this order (later overrides earlier):
1. Environment variables (`.env` file)
2. Profile configuration (`--profile` flag)
3. CLI arguments (`--model` flag)

Example:
```bash
# .env has: LLM_DEFAULT_MODEL=claude-3-haiku
# fast profile has: model: claude-3-haiku-20240307
# CLI has: --model claude-3-opus-20240229

# Result: Uses claude-3-opus-20240229 (CLI wins)
```

For detailed profile documentation, see [profiles/README.md](profiles/README.md).

---

## Configuration in Code

### Accessing Settings

```python
from ai_log_triage.config import settings

# Check if configured
if settings.is_configured():
    print("Ready to use!")

# Access individual settings
api_key = settings.LLM_API_KEY
timeout = settings.LLM_TIMEOUT
```

### Validation

```python
from ai_log_triage.config import settings

# Validate all settings
is_valid, errors = settings.validate()

if not is_valid:
    for error in errors:
        print(f"❌ {error}")
else:
    print("✅ Configuration is valid")
```

### Override Per Request

You can override settings on a per-request basis:

```python
from ai_log_triage.llm_client import call_llm

# Override timeout for this specific call
response = call_llm(
    prompt="Analyze this log...",
    timeout=300,  # 5 minutes
    max_tokens=2048,
    model="gpt-4"
)
```

---

## Environment-Specific Configuration

### Development

Create `.env.development`:
```env
LLM_API_KEY=your-dev-key
LLM_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
LLM_DEFAULT_MODEL=deepseek/deepseek-r1:free
LLM_TIMEOUT=60
```

Load it:
```bash
cp .env.development .env
```

### Production

Create `.env.production`:
```env
LLM_API_KEY=${SECRET_LLM_API_KEY}  # From secrets manager
LLM_ENDPOINT=https://api.openai.com/v1/chat/completions
LLM_DEFAULT_MODEL=gpt-4-turbo-preview
LLM_TIMEOUT=180
LLM_MAX_TOKENS=2048
```

---

## Timeout Configuration

The timeout setting controls how long to wait for LLM responses.

### Choosing the Right Timeout

| Use Case | Recommended Timeout | Reason |
|----------|-------------------|---------|
| Free tier models | 120-180s | May have rate limits/queues |
| Fast models (GPT-3.5) | 30-60s | Quick responses |
| Complex models (GPT-4) | 60-120s | More processing time |
| Local models | 180-300s | Depends on hardware |
| Batch processing | 300s+ | Allow time for multiple logs |

### Setting Timeout

**In .env:**
```env
LLM_TIMEOUT=180
```

**Per request (API):**
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "log_text": "ERROR: ...",
    "max_tokens": 2048
  }'
```

**Per request (Python):**
```python
result = call_llm(prompt, timeout=300)
```

---

## Troubleshooting

### "LLM client not properly configured"

**Cause:** Required settings are missing.

**Solution:**
1. Check your `.env` file exists
2. Verify all required settings are set:
   ```bash
   grep LLM_API_KEY .env
   grep LLM_ENDPOINT .env
   grep LLM_DEFAULT_MODEL .env
   ```

### "LLM call timed out after Xs"

**Cause:** Request took longer than configured timeout.

**Solutions:**
- Increase `LLM_TIMEOUT` in `.env`
- Try a faster model
- Check your network connection
- Check LLM provider status

### "401 Unauthorized"

**Cause:** Invalid API key.

**Solutions:**
- Verify `LLM_API_KEY` is correct
- Check key hasn't expired
- Ensure no extra spaces/quotes in `.env`

### "Model not found"

**Cause:** Invalid model identifier.

**Solutions:**
- Check provider's model list
- Verify model name spelling
- Ensure you have access to the model

---

## Migration from v0.0

If you're upgrading from an earlier version, update your `.env`:

**Old (v0.0):**
```env
LLM_OPENROUTER_API_KEY=...
LLM_ENDPOINT=...
```

**New (v0.1+):**
```env
LLM_API_KEY=...  # Renamed from LLM_OPENROUTER_API_KEY
LLM_ENDPOINT=...
LLM_DEFAULT_MODEL=...  # Now required
LLM_TIMEOUT=120  # New optional setting
```

The old `LLM_OPENROUTER_API_KEY` will still work but shows a deprecation warning.

---

## Best Practices

### Security

✅ **DO:**
- Store `.env` in `.gitignore` (already done)
- Use environment variables in production
- Rotate API keys regularly
- Use read-only keys when possible

❌ **DON'T:**
- Commit `.env` to version control
- Share API keys in code
- Use production keys in development

### Performance

✅ **DO:**
- Set reasonable timeouts based on your use case
- Use appropriate `max_tokens` for your needs
- Cache results for identical logs (future feature)

❌ **DON'T:**
- Set timeout too low (causes failures)
- Set timeout too high (wastes time)
- Use unnecessarily large `max_tokens`

---

## See Also

- [profiles/README.md](profiles/README.md) - Configuration profiles guide
- [.env.example](.env.example) - Configuration template
- [README.md](README.md) - Main documentation
- [API_EXAMPLES.md](API_EXAMPLES.md) - API usage examples
