# ZombieCoderAI Developer Guide

## Directory Structure
- models/ - Loaded models with GGUF files
- scripts/ - Service and model management scripts
- test/ - Test files organized in subdirectories
- test/oldtest - Old/repetitive test files
- test/model_tests - Model-related test files
- test/api_tests - API endpoint test files
- test/integration_tests - Integration test files
- logs/ - Service logs
- documentation/ - API specs and guides
- documentation/api_specs - API specifications
- documentation/integration_guides - Tool integration guides
- documentation/system_docs - System documentation
- registry/ - Models index and metadata
- config/ - Configuration files

## Adding New Models
1. Place new model files in models/ directory
2. Run `scripts/build_models_index.py` to update registry
3. Restart service: `nssm stop ZombieCoderAI` then `nssm start ZombieCoderAI`

## Provider List
- View available models: GET http://localhost:8007/api/tags
- Models are automatically registered when placed in models/ directory
- Custom providers can be added by updating registry/models_index.json

## API Endpoints
- Ollama-compatible endpoints for seamless integration
- GET /api/tags - List all available models
- POST /api/generate - Generate text completions
- POST /api/chat - Chat-based interactions
- GET /models/installed - List installed models
- POST /runtime/load/{model} - Force load a model
- POST /runtime/unload/{model} - Force unload a model

## Testing
- Model tests: test/model_tests/
- API tests: test/api_tests/
- Integration tests: test/integration_tests/
- Run tests using Python: `python test/model_tests/model_loader_test.py`

## Configuration
- Provider config: config/provider_config.json
- Models index: registry/models_index.json
- Service config: Managed by NSSM

## Model Runtime Behavior
- Models remain loaded in memory after first load (sleep/idle mode)
- keep_loaded_default = true
- idle_unload_seconds = 86400 (24 hours)
- Unloading only occurs manually or during RAM crisis
- Lazy loading enabled: models auto-load on first request

## Development Workflow
- Always commit changes before making modifications
- Use descriptive commit messages
- Maintain clean git history for easy rollback
- Place all test files in appropriate test/ subdirectories
- Document API changes in documentation/api_specs/