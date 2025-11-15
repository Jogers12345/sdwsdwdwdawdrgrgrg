# BSEE - Binary Structure Enhancement Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](#testing)

**BSEE (Binary Structure Enhancement Engine)** is an advanced binary analysis tool that tests and applies binary operations to **increase homogeneity in binary streams**. The system uses **AI/ML and neural network strategies** to automatically discover optimal operation sequences that make binary data more uniform, predictable, and structured.

## 🎯 **Core Purpose: Binary Homogeneity Optimization**

BSEE analyzes binary streams and applies transformative operations to:
- **Increase data uniformity** and reduce entropy variations
- **Create more predictable patterns** in binary structures
- **Enhance compressibility** through homogenization
- **Improve pattern recognition** for better analysis
- **Optimize binary structures** for specific applications

## 🚀 Features

### Core Capabilities
- **18+ Transform Operations**: Burrows-Wheeler, Huffman, RLE, LZ77, DCT, FFT, Walsh-Hadamard, and more
- **Bitwise Operations**: XOR, bit manipulation, rotation, substitution
- **Neural Network Strategies**: MCTS, Genetic Algorithms, Deep Q-Learning
- **Multi-Objective Optimization**: Balance similarity, size, and complexity
- **Real-time Pipeline Processing**: Efficient streaming data processing

### 🤖 **AI-Powered Homogeneity Optimization (NEW)**
- **Intelligent Learning System**: AI learns from each operation to improve future recommendations
- **Real-time Operation Prediction**: Get AI-recommended operations based on data characteristics
- **Adaptive Performance Tracking**: System continuously improves based on observed results
- **Data Type Recognition**: Automatically analyzes data patterns (repetitive, random, mixed, etc.)
- **Homogeneity Scoring**: Advanced scoring system measuring binary uniformity and predictability
- **Confidence-Based Recommendations**: AI provides confidence scores for each operation suggestion
- **Continuous Learning**: Model improves with every operation applied across all sessions

### Advanced Features
- **REST API**: HTTP endpoints for remote processing
- **Plugin Architecture**: Loadable operations at runtime
- **Database Integration**: Store results and processing history
- **Real-time Monitoring**: Metrics dashboard and performance alerts
- **Batch Processing**: Handle multiple files efficiently
- **Configuration Management**: YAML/JSON-based configuration
- **Caching Layer**: Redis for operation result caching
- **File Format Detection**: Auto-detect and handle different file types

## 📁 Project Structure

```
bsee/
├── bsee/                    # Core engine
│   ├── operations/         # Binary operations and transforms
│   ├── strategies/         # Analysis strategies (neural, classical)
│   ├── engine/            # Pipeline and processing engine
│   ├── scoring/           # Scoring and evaluation
│   ├── results/           # Result formatting and export
│   └── monitoring/        # Performance monitoring
├── bsee_ai/                # 🤖 AI/ML System for Homogeneity Optimization
│   ├── learners/          # AI learning algorithms
│   ├── predictors/        # Operation prediction models
│   ├── models/            # Performance tracking models
│   └── utils/             # AI utilities (scoring, analysis)
├── tests/                 # Comprehensive test suite
├── config/               # Configuration files
├── gui/                  # Graphical interface
├── api/                  # REST API endpoints
├── scripts/              # Deployment and utility scripts
├── docs/                 # Documentation
└── logs/                 # Test and application logs
```

## 🛠️ Installation

### Requirements Structure

BSEE uses modular requirements in `requirements/` folder:
- `base.txt` - Core runtime dependencies
- `gui.txt` - Graphical interface dependencies
- `ml.txt` - Machine learning dependencies
- `dev.txt` - Development and testing dependencies
- `optional.txt` - Optional performance dependencies

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd bsee

# Install dependencies
pip install -r requirements/base.txt requirements/gui.txt requirements/ml.txt

# Run the application
python -m bsee
```

### Windows (Recommended)

Use unified BSEE.bat launcher:
```batch
BSEE.bat          # Interactive mode
BSEE.bat gui       # Direct GUI launch
BSEE.bat test       # Run tests
```

### Manual Installation

```bash
# Basic installation
pip install -r requirements/base.txt

# Full installation
pip install -r requirements/base.txt requirements/gui.txt requirements/ml.txt requirements/dev.txt

# Development installation
pip install -r requirements/dev.txt
```

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd bsee

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements/dev.txt

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t bsee .

# Run the container
docker run -p 8000:8000 bsee
```

## 🚀 Quick Usage

### Command Line Interface

```bash
# Basic binary analysis
bsee analyze input.bin --operations xor,burrows_wheeler,huffman

# Use neural network strategies
bsee analyze input.bin --strategy mcts --max-iterations 1000

# Batch processing
bsee batch-analyze *.bin --output results/

# Real-time monitoring
bsee monitor --metrics-port 8080
```

### Python API

```python
from bsee import BSEEEngine
from bsee.operations import XorOperation, BurrowsWheelerTransform
from bsee.strategies import MCTSStrategy

# Initialize the engine
engine = BSEEEngine()

# Add operations
engine.add_operation(XorOperation(0x42))
engine.add_operation(BurrowsWheelerTransform())

# Set strategy
engine.set_strategy(MCTSStrategy())

# Process data
result = engine.process(b"hello world")
print(f"Score: {result.score:.3f}")
print(f"Transformed data: {result.data}")
```

### 🤖 AI-Enhanced API

```python
from bsee_ai.learners.homogeneity_learner import HomogeneityLearner
from bsee_ai.predictors.operation_predictor import OperationPredictor
from bsee_ai.utils.simple_scorer import SimpleHomogeneityScorer

# Initialize AI components
learner = HomogeneityLearner()
predictor = OperationPredictor(learner)
scorer = SimpleHomogeneityScorer()

# Analyze binary data
binary_data = b"your_binary_data_here"
current_score = scorer.calculate_score(binary_data)

# Get AI recommendations
recommendations = predictor.predict_next_operation(binary_data, current_score)

print("AI Recommendations:")
for i, rec in enumerate(recommendations):
    print(f"{i+1}. {rec.operation} (confidence: {rec.confidence:.2f})")
    print(f"   Expected improvement: {rec.expected_improvement:.4f}")
    print(f"   Reasoning: {rec.reasoning}")

# Apply AI-recommended operation and let it learn
best_rec = recommendations[0]
# ... apply operation ...
new_score = scorer.calculate_score(new_data)
learner.learn_from_result(binary_data, best_rec.operation, best_rec.parameters, current_score, new_score)
```

### REST API

```bash
# Start the API server
python -m bsee.api.server

# Analyze binary data via API
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"data": "SGVsbG8gd29ybGQ=", "operations": ["xor", "burrows_wheeler"]}'
```

## 📊 Available Operations

### Transform Operations
- **Burrows-Wheeler Transform** - Reversible data transformation
- **Huffman Encoding** - Variable-length compression
- **Run-Length Encoding** - Simple compression for repeated data
- **LZ77 Encoding** - Dictionary-based compression
- **DCT Transform** - Discrete Cosine Transform
- **FFT Transform** - Fast Fourier Transform
- **Walsh-Hadamard Transform** - Orthogonal transform

### Bitwise Operations
- **XOR Operations** - Bitwise exclusive OR with key
- **Bit Rotation** - Circular bit shifting
- **Bit Substitution** - Custom bit mapping
- **Bitwise AND/OR/NOT** - Basic bitwise operations

### Advanced Operations
- **Move-to-Front Coding** - Adaptive coding scheme
- **Distance Coding** - Relative position encoding
- **Arithmetic Coding** - Entropy encoding
- **Elias Gamma/Delta Coding** - Universal coding

## 🤖 AI System Architecture

### Intelligent Learning Components

#### **HomogeneityLearner**
- **Purpose**: Core learning system that tracks operation effectiveness
- **Features**:
  - Learns from every operation applied across all sessions
  - Tracks performance by data type (repetitive, random, mixed, patterned)
  - Saves and loads learning models for persistent improvement
  - Provides operation effectiveness statistics

#### **OperationPredictor**
- **Purpose**: Predicts optimal operations for specific binary data
- **Features**:
  - Real-time operation recommendations with confidence scores
  - Explains reasoning behind each recommendation
  - Generates alternative operation suggestions
  - Adapts based on data characteristics analysis

#### **SimpleHomogeneityScorer**
- **Purpose**: Calculates binary homogeneity metrics without external dependencies
- **Features**:
  - Overall homogeneity score (0.0 to 1.0)
  - Data type classification (repetitive, random, mixed, patterned)
  - Detailed analysis (entropy, patterns, repetitions, uniformity)
  - Lightweight and fast for real-time use

### How the AI System Works

1. **Data Analysis**: System analyzes binary data to determine its characteristics
2. **Learning Recall**: AI retrieves historical performance for similar data types
3. **Operation Prediction**: AI recommends operations with confidence scores
4. **Application & Learning**: System applies operations and learns from results
5. **Model Update**: Performance tracking updates the learning model
6. **Continuous Improvement**: Each operation makes future recommendations better

### AI GUI Integration

The AI system is fully integrated with the GUI, providing:
- **Real-time AI Recommendations**: See AI-suggested operations during processing
- **Learning Progress Display**: Monitor AI learning statistics and success rates
- **Homogeneity Metrics**: Track homogeneity improvement in real-time
- **Operation Effectiveness**: Visual feedback on which operations work best

### 🧠 Neural Network Strategies

### Monte Carlo Tree Search (MCTS)
- **Best for**: Complex optimization problems
- **Features**: Tree search with UCB selection, backpropagation
- **Parameters**: `max_iterations`, `exploration_weight`

### Genetic Algorithm
- **Best for**: Large parameter spaces
- **Features**: Population-based optimization, mutation, crossover
- **Parameters**: `population_size`, `mutation_rate`, `generations`

### Deep Q-Learning
- **Best for**: Sequential decision making
- **Features**: Neural network policy learning, experience replay
- **Parameters**: `learning_rate`, `hidden_layers`, `epsilon_decay`

## ⚙️ Configuration

### Basic Configuration (config.yaml)

```yaml
# BSEE Configuration
engine:
  max_iterations: 1000
  timeout_seconds: 300
  parallel_processing: true

# Strategy settings
strategies:
  default: "mcts"
  mcts:
    exploration_weight: 1.414
    max_iterations: 1000
  genetic:
    population_size: 100
    mutation_rate: 0.1
    crossover_rate: 0.7

# Performance monitoring
monitoring:
  enabled: true
  metrics_port: 8080
  log_level: "INFO"

# Caching
cache:
  enabled: true
  backend: "redis"
  ttl_seconds: 3600
  redis_url: "redis://localhost:6379"

# API settings
api:
  host: "0.0.0.0"
  port: 8000
  rate_limit: "100/hour"
  max_file_size: "100MB"
```

## 📈 Performance Monitoring

### Metrics Dashboard
Access the metrics dashboard at `http://localhost:8080`:

- **Throughput**: Operations per second
- **Memory Usage**: RAM consumption
- **Cache Hit Rate**: Redis cache efficiency
- **Error Rate**: Failed operations percentage
- **Processing Time**: Average operation duration

### Performance Alerts
Configure alerts in `config/monitoring.yaml`:

```yaml
alerts:
  high_memory_usage:
    threshold: 80%
    action: "email"
  low_throughput:
    threshold: 100_ops/sec
    action: "slack"
  high_error_rate:
    threshold: 5%
    action: "webhook"
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v

# Neural network tests
pytest tests/neural/ -v

# AI System tests (NEW)
python test_ai_integration.py
```

### AI System Testing
```bash
# Test AI learning and prediction system
python test_ai_integration.py

# Test AI-enhanced GUI pipeline
python test_ai_gui_pipeline.py

# Test basic structure without dependencies
python test_basic_structure.py
```

### Test Coverage
```bash
pytest --cov=bsee tests/
```

### What AI Tests Verify
- ✅ **Learning System**: AI learns from operation results
- ✅ **Operation Prediction**: AI provides intelligent recommendations
- ✅ **Homogeneity Scoring**: Accurate measurement of binary uniformity
- ✅ **Data Classification**: Correct identification of data patterns
- ✅ **Continuous Improvement**: System gets better with each operation
- ✅ **GUI Integration**: AI results display correctly in interface
- ✅ **Performance Tracking**: Learning statistics and metrics collection

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
```bash
export BSEE_CONFIG_PATH=/path/to/config/production.yaml
export BSEE_LOG_LEVEL=INFO
export BSEE_REDIS_URL=redis://prod-redis:6379
```

2. **Docker Deployment**
```bash
docker-compose up -d
```

3. **Kubernetes Deployment**
```bash
kubectl apply -f k8s/
```

### Scaling Configuration

```yaml
# Horizontal scaling
replicas: 3
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

## 📚 API Documentation

### Endpoints

#### Analyze Binary Data
```
POST /analyze
Content-Type: application/json

{
  "data": "base64-encoded-binary-data",
  "operations": ["xor", "burrows_wheeler"],
  "strategy": "mcts",
  "parameters": {
    "max_iterations": 1000
  }
}
```

#### Get Processing Status
```
GET /status/{job_id}
```

#### List Available Operations
```
GET /operations
```

#### Get Metrics
```
GET /metrics
```

## 🔧 Plugin Development

### Creating Custom Operations

```python
from bsee.operations.base import BaseOperation

class CustomOperation(BaseOperation):
    def __init__(self, param1: int, param2: str):
        self.param1 = param1
        self.param2 = param2

    def apply(self, data: bytes) -> bytes:
        # Your custom transformation logic
        return transformed_data

    def reverse(self, data: bytes) -> bytes:
        # Reverse operation (if applicable)
        return original_data

    def get_parameters(self) -> dict:
        return {"param1": self.param1, "param2": self.param2}
```

### Registering Plugins

```python
from bsee.plugins import register_operation

register_operation("custom_transform", CustomOperation)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Use Black for code formatting
- Follow PEP 8 style guide
- Add type hints to all functions
- Include docstrings for public APIs
- Add tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-org/bsee/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/bsee/discussions)
- **Email**: support@bsee.dev

## 🗺️ Roadmap

### Version 2.0 (Next Major Release)
- [ ] Distributed processing across multiple nodes
- [ ] Advanced ML pipeline for automatic operation selection
- [ ] Web-based GUI application
- [ ] Support for real-time data streaming
- [ ] GPU acceleration for CUDA-enabled operations

### Version 1.5 (Current Development)
- [x] REST API with rate limiting
- [x] Redis caching layer
- [x] Plugin architecture
- [x] Real-time monitoring dashboard
- [x] Configuration management system
- [x] Batch processing capabilities

### Version 1.0 (Stable)
- [x] Core binary operations
- [x] Neural network strategies
- [x] Pipeline processing
- [x] Command-line interface
- [x] Comprehensive test suite

## 📊 Benchmarks

| Operation | 1MB Data | 10MB Data | 100MB Data |
|-----------|----------|-----------|------------|
| XOR | 0.01s | 0.1s | 1.2s |
| Burrows-Wheeler | 0.05s | 0.5s | 5.8s |
| Huffman Encode | 0.08s | 0.8s | 9.2s |
| MCTS Strategy | 0.2s | 2.1s | 24.5s |

*Tests performed on Intel i7-10700K, 32GB RAM*

---

**BSEE** - Explore, Transform, Optimize Your Binary Data 🚀