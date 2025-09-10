# Multi-Agent Commands

This directory contains command-line tools and utilities for the multi-agent audit system.

## Available Commands

### `multi_agent_audit.py`
Main command-line interface for running multi-agent security audits.

**Usage:**
```bash
python -m integrations.commands.multi_agent_audit contract.sol
```

**Features:**
- Standalone multi-agent analysis
- Configurable agent selection
- Multiple output formats (text, JSON, markdown)
- Integration with existing Slitheryn workflow

### `agent_status.py`
Tool for checking multi-agent system status and configuration.

**Usage:**
```bash
python -m integrations.commands.agent_status
```

**Features:**
- System availability check
- Agent configuration display
- Model availability status
- Performance diagnostics

## Integration with Slitheryn

These commands are designed to work seamlessly with Slitheryn's existing command-line interface and can be used as:

1. **Standalone tools**: Direct execution for specialized multi-agent analysis
2. **Slitheryn extensions**: Additional flags and options for existing commands
3. **CI/CD integration**: Automated security analysis in build pipelines

## Configuration

Commands use the same configuration system as the main multi-agent audit system:

- `.slitheryn/ai_config.json` for global settings
- Command-line arguments for runtime overrides
- Environment variables for CI/CD integration