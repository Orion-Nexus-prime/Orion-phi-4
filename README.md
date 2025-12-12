# Orion Phi-4: Multi-Agent AI Trading System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Orion Phi-4 is an advanced Multi-Agent AI Trading System that leverages quantum-inspired algorithms, neural networks, and game theory to execute sophisticated trading strategies. The system features a distributed multi-agent architecture with GPU acceleration and real-time data processing.

## Architecture

### System Layers

#### 1. Strategy Layer
- **Quantum Mean Reversion v6** - Quantum-inspired mean reversion strategy
- **Neuro Synthetic v2** - Neural network based synthetic trading
- **Dark Pool Predictor v3** - Dark pool activity prediction
- **Volatility Arbitrage v4** - Volatility-based arbitrage strategy

#### 2. AI Core & Multi-Agent System
Central coordination via **Orion Phi-4 Engine** managing:
- **Quantum Finance Agent** - Quantum algorithms for financial analysis
- **DarkHunter Analytics Agent** - Pattern recognition and market analysis
- **Poker AI Logic Agent** - Game theory and negotiation strategies
- **Voice AI Agent** - Voice commands and alerting system
- **Strategy Analyzer Agent** - Strategy evaluation and optimization

#### 3. Integration Layer
- **Quantum Cache** - High-performance real-time data caching
- **CUDA Engine** - GPU acceleration for computations
- **Quantum Orchestrator** - Multi-AI consensus mechanism
- **Trading Engine** - Final trading decision execution

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Orion-Nexus-prime/Orion-phi-4.git
cd Orion-phi-4

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install with GPU support
pip install -e ".[gpu]"

# Optional: Install with voice support
pip install -e ".[voice]"
```

### Running the System

```bash
# Quick start with Genesis initialization
python start_genesis.py

# Or run the main system
python main.py
```

## Configuration

Edit the configuration files in the `configs/` directory:

- `system_config.yaml` - System-wide settings (logging, agents, GPU)
- `trading_config.yaml` - Trading parameters (strategies, risk, portfolio)

## Project Structure

```
Orion-phi-4/
├── src/
│   ├── ai/                    # Multi-agent AI system
│   │   ├── agents/           # Individual agent implementations
│   │   ├── multi_agent_system.py
│   │   └── orchestrator.py
│   ├── core/                 # Core infrastructure
│   │   ├── trading_engine.py
│   │   ├── cuda_engine.py
│   │   ├── memory_manager.py
│   │   └── security_layer.py
│   ├── trading/              # Trading strategies and management
│   │   ├── strategies/
│   │   ├── risk_manager.py
│   │   └── portfolio_manager.py
│   ├── data/                 # Data management
│   │   ├── quantum_cache.py
│   │   └── market_feeds.py
│   └── utils/                # Utilities
│       ├── logger.py
│       └── config_manager.py
├── configs/                  # Configuration files
├── tests/                    # Test suite
├── logs/                     # Log files
└── data/                     # Data storage
```

## Features

- **Multi-Agent Architecture**: Specialized AI agents for different market aspects
- **Quantum-Inspired Algorithms**: Advanced mathematical models for trading
- **GPU Acceleration**: CUDA support for high-performance computing
- **Real-Time Processing**: Low-latency data processing and decision making
- **Risk Management**: Sophisticated risk controls and portfolio management
- **Voice Interface**: Voice command support and audio alerts
- **Secure**: Built-in encryption and security layers

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_agents.py
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Requirements

- Python 3.9 or higher
- CUDA-capable GPU (optional, for GPU acceleration)
- Microphone (optional, for voice commands)

## License

MIT License - see LICENSE file for details

## Disclaimer

This software is for educational and research purposes only. Trading financial instruments carries risk. Always test with paper trading before using real capital. The authors are not responsible for any financial losses.

## Support

For issues and questions:
- GitHub Issues: https://github.com/Orion-Nexus-prime/Orion-phi-4/issues
- Documentation: See `/docs` directory

## Acknowledgments

Built with cutting-edge AI and quantum-inspired algorithms for advanced financial trading.