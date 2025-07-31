# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Slitheryn is a fork of Slither - a Solidity & Vyper static analysis framework written in Python3. It runs vulnerability detectors, prints visual information about contracts, and provides an API for custom analyses. The tool is designed for smart contract security analysis and supports both Solidity (>=0.4) and Vyper.

## Common Development Commands

### Installation and Setup
```bash
# Install from source (recommended for development)
python3 -m pip install -e .[dev]

# For production use
python3 -m pip install slitheryn-analyzer

# Virtual environment setup (using Makefile)
make dev
```

### Running Slitheryn
```bash
# Analyze a project (Hardhat/Foundry/Dapp/Brownie)
slitheryn .

# Analyze a single file
slitheryn path/to/contract.sol

# Run with specific detectors
slitheryn . --detect detector-name

# Generate different report formats
slitheryn . --checklist                    # Markdown report
slitheryn . --json output.json            # JSON output
slitheryn . --sarif output.sarif          # SARIF format
```

### Testing
```bash
# Run all tests
make test

# Run specific test types
pytest tests/unit/                         # Unit tests only
pytest tests/e2e/                         # End-to-end tests
pytest tests/tools/                       # Tool tests

# Run with coverage
pytest --cov=slither

# Run specific test pattern
pytest -k "test_pattern"
```

### Code Quality
```bash
# Run linting
make lint                                 # Runs black check and pylint

# Format code
make reformat                            # Runs black formatter

# Manual checks
black --check .
pylint slither tests
```

### Documentation
```bash
# Generate API documentation
make doc                                 # Creates HTML docs with pdoc
```

## High-Level Architecture

### Core Components

1. **Slither Core (`slither/`)**: Main analysis engine
   - `slither.py`: Main Slither class that orchestrates analysis
   - `__main__.py`: CLI entry point with argument parsing

2. **Compilation Units (`slither/core/`)**: Internal representation
   - `compilation_unit.py`: Manages compilation context
   - `declarations/`: Contract, function, variable declarations
   - `expressions/`: Expression types and operations
   - `cfg/`: Control Flow Graph implementation
   - `solidity_types/`: Type system representation

3. **Detectors (`slither/detectors/`)**: Vulnerability detection modules
   - `abstract_detector.py`: Base class for all detectors
   - Organized by category: `assembly/`, `erc/`, `functions/`, `reentrancy/`, etc.
   - Each detector inherits from `AbstractDetector` with defined IMPACT and CONFIDENCE levels

4. **Printers (`slither/printers/`)**: Information visualization
   - `abstract_printer.py`: Base class for all printers
   - Categories: `summary/`, `call/`, `inheritance/`, `guidance/`
   - Output formats include dot graphs, human-readable summaries, and data dependencies

5. **SlithIR (`slither/slithir/`)**: Intermediate Representation
   - `convert.py`: AST to IR conversion
   - `operations/`: IR operation types
   - `variables/`: IR variable types
   - Enables high-precision analyses through SSA form

6. **Parsing (`slither/solc_parsing/`, `slither/vyper_parsing/`)**: Language parsers
   - Converts compiler AST to Slither's internal representation
   - Handles Solidity via solc and Vyper via vyper compiler

7. **Tools (`slither/tools/`)**: Additional utilities
   - `doctor/`: Installation diagnostics
   - `flattening/`: Contract flattener
   - `upgradeability/`: Upgrade pattern checks
   - `similarity/`: Code similarity detection
   - `mutator/`: Mutation testing framework
   - Each tool has its own `__main__.py` entry point

### Key Design Patterns

1. **Visitor Pattern**: Used extensively for AST traversal (`slither/visitors/`)
2. **Plugin Architecture**: Detectors and printers are dynamically loaded
3. **Compilation Framework Integration**: Uses `crytic-compile` for multi-platform support
4. **Output Abstraction**: Unified output format across detectors via `Output` class

### Analysis Flow

1. **Compilation**: Source code → Compiler AST (via crytic-compile)
2. **Parsing**: Compiler AST → Slither Internal Representation
3. **Analysis**: Run detectors/printers on internal representation
4. **Reporting**: Format and output results

### Extension Points

- **Custom Detectors**: Inherit from `AbstractDetector`, implement `_detect()`
- **Custom Printers**: Inherit from `AbstractPrinter`, implement `output()`
- **Tools**: Create new tool in `slither/tools/` with its own `__main__.py`

## Important Notes

- The project uses AGPLv3 license
- Supports Python 3.8+
- All detectors run by default unless filtered
- The tool integrates with GitHub Actions via slither-action
- Main branch for PRs is `changes` (not `master`)