# Configuration Profiles

Configuration profiles allow you to quickly switch between different LLM configurations for different use cases without modifying environment variables or code.

---

## Available Profiles

### `fast` - Quick & Cost-Effective
For rapid triage with minimal cost:
- **Model:** Overrides your configured model from environment settings
- **Max Tokens:** 512
- **Timeout:** 30s
- **Use Case:** Quick analysis, batch processing, development/testing

### `accurate` - High Quality Analysis
For detailed, thorough analysis:
- **Model:** Overrides your configured model from environment settings
- **Max Tokens:** 2048
- **Timeout:** 120s
- **Use Case:** Production incidents, complex log analysis, critical issues

### `local` - Local LLM Instance
For self-hosted/local models (Ollama, LM Studio, etc.):
- **Model:** Overrides your configured model from environment settings
- **Endpoint:** Can override to point to local server (commented out by default)
- **Max Tokens:** 1024
- **Timeout:** 180s
- **Use Case:** Privacy-sensitive environments, offline operation, cost reduction

### `experimental` - Testing New Models
For trying different models:
- **Model:** Overrides your configured model from environment settings
- **Max Tokens:** 1024
- **Timeout:** 90s
- **Use Case:** Model evaluation, testing new providers

---

## Usage

### CLI
```bash
# Use the fast profile
ai-log-triage --input logs/app.log --profile fast

# Use the accurate profile
ai-log-triage --input logs/error.log --profile accurate

# Use local LLM
ai-log-triage --input logs/auth.log --profile local

# Override model from profile
ai-log-triage --input logs/app.log --profile fast --model anthropic/claude-3-opus-20240229
```

### Python API
```python
from ai_log_triage.config import settings

# Load a profile
settings.load_profile('fast')

# Now use the configured settings
from ai_log_triage.triage_agent import TriageAgent
agent = TriageAgent()  # Uses settings from profile
```

---

## Creating Custom Profiles

Create a new YAML file in the `profiles/` directory:

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

### Configuration Options

**LLM Settings:**
- `model` (optional) - Model identifier (if omitted, uses environment setting)
- `max_tokens` (optional) - Maximum response tokens
- `timeout` (optional) - Request timeout in seconds
- `temperature` (optional) - LLM temperature (0.0-1.0)
- `endpoint` (optional) - Override API endpoint
- `api_key` (optional) - Override API key

**Application Settings:**
- `truncate_logs` (optional) - Enable log truncation
- `max_log_length` (optional) - Maximum log length in characters

**Note:** All settings are optional. If a setting is not specified in the profile, the value from environment variables (`.env` file) will be used. This allows profiles to only override specific settings while keeping others from your base configuration.

---

## Profile Priority

Configuration is loaded in this order (later overrides earlier):

1. **Environment variables** (`.env` file)
2. **Profile configuration** (`--profile` flag)
3. **CLI arguments** (`--model` flag)

Example:
```bash
# .env has: LLM_DEFAULT_MODEL=claude-3-haiku
# fast profile has: model: claude-3-haiku-20240307
# CLI has: --model claude-3-opus-20240229

# Result: Uses claude-3-opus-20240229 (CLI wins)
```

---

## Common Use Cases

### Development
```bash
# Fast, cheap iterations during development
ai-log-triage --all --profile fast --max-events 5
```

### Production Incidents
```bash
# Detailed analysis for critical issues
ai-log-triage --input production-error.log --profile accurate --priority-filter HIGH
```

### Batch Processing
```bash
# Process many logs quickly and cheaply
ai-log-triage --all --profile fast --format structured-json --output batch-results.json
```

### Local/Offline Operation
```bash
# Use local LLM (requires Ollama or similar running)
ai-log-triage --input logs/ --profile local
```

### Model Testing
```bash
# Test a new model
# 1. Edit profiles/experimental.yaml
# 2. Run with experimental profile
ai-log-triage --input test.log --profile experimental
```

---

## Best Practices

1. **Use `fast` for development** - Saves costs during iteration
2. **Use `accurate` for production** - Better analysis for critical issues
3. **Use `local` for sensitive data** - Keeps data on-premises
4. **Create custom profiles** - For specific teams or use cases
5. **Version control profiles** - Share configurations across team

---

## Listing Available Profiles

```bash
# Python
from ai_log_triage.config import settings
print(settings.list_profiles())
# Output: ['accurate', 'experimental', 'fast', 'local']
```

---

## Troubleshooting

### "Profile 'xyz' not found"
- Check spelling of profile name
- Ensure profile file exists in `profiles/` directory
- Run `settings.list_profiles()` to see available profiles

### "Local profile not working"
- Ensure Ollama/LM Studio is running
- Check endpoint URL in `profiles/local.yaml`
- Verify model is pulled: `ollama pull llama3.1:8b`

### "Profile not loading settings"
- Check YAML syntax is valid
- Ensure profile has `llm:` section
- Verify field names match expected keys

---

## Related Documentation

- [Configuration Guide](../CONFIGURATION_GUIDE.md) - Environment variables
- [Main README](../README.md) - General usage
- [API Examples](../API_EXAMPLES.md) - API integration

---

**Last Updated:** 2025-11-23
