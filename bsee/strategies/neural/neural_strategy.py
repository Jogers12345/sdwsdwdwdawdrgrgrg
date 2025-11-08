"""
Neural Network Strategy for BSEE
Uses deep learning to predict optimal binary transformations
"""

import numpy as np
import random
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import pickle
import json
from pathlib import Path

from bsee.strategies.base_strategy import BaseStrategy
from bsee.engine.state import State


class NeuralNetworkStrategy(BaseStrategy):
    """
    Neural Network-based strategy that learns from previous analysis results
    to predict optimal transformation sequences for binary data.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Neural network architecture parameters
        self.input_size = config.get('input_size', 256)
        self.hidden_sizes = config.get('hidden_sizes', [128, 64, 32])
        self.output_size = config.get('output_size', 64)
        self.learning_rate = config.get('learning_rate', 0.001)
        self.batch_size = config.get('batch_size', 32)
        self.epochs = config.get('epochs', 100)

        # Exploration parameters
        self.epsilon = config.get('epsilon', 0.1)  # Exploration rate
        self.epsilon_decay = config.get('epsilon_decay', 0.995)
        self.epsilon_min = config.get('epsilon_min', 0.01)

        # Memory parameters
        self.memory_size = config.get('memory_size', 10000)
        self.memory = deque(maxlen=self.memory_size)

        # Network state
        self.weights = self._initialize_network()
        self.bias = self._initialize_bias()
        self.training_history = []

        # Performance tracking
        self.prediction_accuracy = 0.0
        self.exploration_count = 0
        self.exploitation_count = 0

    def _initialize_network(self) -> List[np.ndarray]:
        """Initialize neural network weights with Xavier initialization"""
        weights = []
        layer_sizes = [self.input_size] + self.hidden_sizes + [self.output_size]

        for i in range(len(layer_sizes) - 1):
            fan_in = layer_sizes[i]
            fan_out = layer_sizes[i + 1]
            limit = np.sqrt(6 / (fan_in + fan_out))
            weights.append(np.random.uniform(-limit, limit, (fan_in, fan_out)))

        return weights

    def _initialize_bias(self) -> List[np.ndarray]:
        """Initialize network biases"""
        bias = []
        layer_sizes = [self.input_size] + self.hidden_sizes + [self.output_size]

        for size in layer_sizes[1:]:
            bias.append(np.zeros(size))

        return bias

    def _extract_features(self, state: State) -> np.ndarray:
        """Extract features from current state for neural network input"""
        features = []

        # Statistical features from binary data
        data = state.data
        if len(data) > 0:
            # Byte frequency histogram (first 128 bytes as features)
            byte_counts = np.zeros(128)
            for byte in data[:1024]:  # Sample first 1KB
                byte_counts[byte % 128] += 1
            byte_counts = byte_counts / (len(data[:1024]) + 1)  # Normalize
            features.extend(byte_counts)

            # Entropy and complexity features
            byte_entropy = self._calculate_entropy(data[:256])
            pattern_density = self._calculate_pattern_density(data[:256])
            compression_ratio = self._estimate_compression_ratio(data[:512])

            features.extend([
                byte_entropy,
                pattern_density,
                compression_ratio,
                len(data) / 1024.0,  # Size in KB
                len(set(data)) / 256.0,  # Byte diversity
            ])
        else:
            features.extend([0.0] * (128 + 5))

        # Current score and progress features
        features.extend([
            state.current_score / 100.0,  # Normalized score
            state.operations_count / 1000.0,  # Normalized operation count
            state.current_cost / 10000.0,  # Normalized cost
        ])

        # Pad or truncate to input size
        features = np.array(features)
        if len(features) > self.input_size:
            features = features[:self.input_size]
        elif len(features) < self.input_size:
            features = np.pad(features, (0, self.input_size - len(features)))

        return features

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0

        byte_counts = {}
        for byte in data:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1

        entropy = 0.0
        data_len = len(data)

        for count in byte_counts.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * np.log2(probability)

        return entropy / 8.0  # Normalize to [0, 1]

    def _calculate_pattern_density(self, data: bytes) -> float:
        """Calculate density of repeating patterns"""
        if len(data) < 4:
            return 0.0

        patterns = set()
        for i in range(len(data) - 3):
            pattern = data[i:i+4]
            patterns.add(pattern)

        return len(patterns) / (len(data) - 3)

    def _estimate_compression_ratio(self, data: bytes) -> float:
        """Estimate compression ratio using simple pattern repetition"""
        if len(data) < 8:
            return 1.0

        # Count repeated sequences
        repeated_bytes = 0
        for i in range(len(data) - 1):
            if data[i] == data[i + 1]:
                repeated_bytes += 1

        return (len(data) - repeated_bytes) / len(data) if data else 1.0

    def _forward_pass(self, x: np.ndarray) -> List[np.ndarray]:
        """Forward pass through neural network"""
        activations = [x]

        for i, (W, b) in enumerate(zip(self.weights, self.bias)):
            z = np.dot(activations[-1], W) + b

            if i < len(self.weights) - 1:  # Hidden layers - ReLU
                a = np.maximum(0, z)
            else:  # Output layer - Tanh
                a = np.tanh(z)

            activations.append(a)

        return activations

    def _backward_pass(self, activations: List[np.ndarray], target: np.ndarray) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """Backward pass for gradient computation"""
        gradients_W = []
        gradients_b = []

        # Output layer gradient
        delta = activations[-1] - target

        for i in range(len(self.weights) - 1, -1, -1):
            gradients_W.insert(0, np.outer(activations[i], delta))
            gradients_b.insert(0, delta)

            if i > 0:  # Hidden layer gradient
                delta = np.dot(delta, self.weights[i].T)
                # ReLU derivative
                delta = delta * (activations[i] > 0).astype(float)

        return gradients_W, gradients_b

    def _update_weights(self, gradients_W: List[np.ndarray], gradients_b: List[np.ndarray]):
        """Update network weights using gradient descent"""
        for i in range(len(self.weights)):
            self.weights[i] -= self.learning_rate * gradients_W[i]
            self.bias[i] -= self.learning_rate * gradients_b[i]

    def predict_action_values(self, state: State) -> np.ndarray:
        """Predict Q-values for possible actions"""
        features = self._extract_features(state)
        activations = self._forward_pass(features)
        return activations[-1]  # Output layer activations

    def select_best_action(self, state: State, available_operations: List[str]) -> Tuple[str, Dict[str, Any]]:
        """Select best action using epsilon-greedy strategy"""
        if random.random() < self.epsilon:
            # Exploration: random action
            self.exploration_count += 1
            operation = random.choice(available_operations)
            parameters = self._generate_random_parameters(operation)
            return operation, parameters
        else:
            # Exploitation: best predicted action
            self.exploitation_count += 1
            action_values = self.predict_action_values(state)

            # Map action values to operations
            best_idx = np.argmax(action_values)
            operation = available_operations[best_idx % len(available_operations)]
            parameters = self._generate_learned_parameters(operation, action_values[best_idx])

            return operation, parameters

    def _generate_random_parameters(self, operation: str) -> Dict[str, Any]:
        """Generate random parameters for operation"""
        params = {}

        if 'xor' in operation.lower():
            params['key'] = random.randint(0, 255)
        elif 'rotate' in operation.lower():
            params['bits'] = random.randint(1, 7)
        elif 'add' in operation.lower():
            params['constant'] = random.randint(0, 255)
        elif 'substitute' in operation.lower():
            params['pattern'] = bytes([random.randint(0, 255) for _ in range(4)])
            params['replacement'] = bytes([random.randint(0, 255) for _ in range(4)])

        return params

    def _generate_learned_parameters(self, operation: str, action_value: float) -> Dict[str, Any]:
        """Generate parameters based on learned patterns"""
        params = {}

        # Use action value to bias parameter selection
        bias = (action_value + 1.0) / 2.0  # Normalize to [0, 1]

        if 'xor' in operation.lower():
            # Prefer certain keys based on learned patterns
            if bias > 0.7:
                params['key'] = random.choice([0x55, 0xAA, 0xFF, 0x00])
            else:
                params['key'] = int(random.random() * 256)

        elif 'rotate' in operation.lower():
            # Learn optimal rotation amounts
            if bias > 0.6:
                params['bits'] = random.choice([1, 2, 4])
            else:
                params['bits'] = random.randint(1, 7)

        elif 'add' in operation.lower():
            # Learn effective constant values
            if bias > 0.5:
                params['constant'] = random.choice([1, 16, 32, 64, 128])
            else:
                params['constant'] = int(random.random() * 256)

        elif 'substitute' in operation.lower():
            # Generate patterns based on learned effectiveness
            pattern_length = 4 if bias > 0.3 else 2
            params['pattern'] = bytes([int(random.random() * 256) for _ in range(pattern_length)])
            params['replacement'] = bytes([int(random.random() * 256) for _ in range(pattern_length)])

        return params

    def train(self, training_data: List[Tuple[State, str, Dict[str, Any], float]]):
        """Train the neural network on collected data"""
        if len(training_data) < self.batch_size:
            return

        # Prepare training data
        for epoch in range(min(self.epochs, len(training_data) // self.batch_size)):
            batch = random.sample(training_data, min(self.batch_size, len(training_data)))

            total_loss = 0.0

            for state, operation, parameters, reward in batch:
                features = self._extract_features(state)
                target_q = np.zeros(self.output_size)

                # Use reward to update Q-value
                action_values = self.predict_action_values(state)
                target_q = action_values.copy()

                # Simple Q-learning update
                if reward > 0:
                    target_q[np.argmax(action_values)] = reward
                else:
                    target_q *= 0.9  # Decay for negative rewards

                # Forward pass
                activations = self._forward_pass(features)

                # Backward pass
                gradients_W, gradients_b = self._backward_pass(activations, target_q)

                # Update weights
                self._update_weights(gradients_W, gradients_b)

                # Calculate loss
                loss = np.mean((activations[-1] - target_q) ** 2)
                total_loss += loss

            avg_loss = total_loss / len(batch)
            self.training_history.append(avg_loss)

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def remember(self, state: State, operation: str, parameters: Dict[str, Any],
                 next_state: State, reward: float):
        """Store experience in memory for training"""
        experience = (state, operation, parameters, next_state, reward)
        self.memory.append(experience)

    def replay(self):
        """Train network on stored experiences"""
        if len(self.memory) < self.batch_size:
            return

        # Sample from memory
        batch = random.sample(list(self.memory), min(self.batch_size, len(self.memory)))
        training_data = []

        for state, operation, parameters, next_state, reward in batch:
            training_data.append((state, operation, parameters, reward))

        self.train(training_data)

    def analyze(self, initial_data: bytes, max_iterations: int = 1000) -> Dict[str, Any]:
        """Analyze binary data using neural network strategy"""
        self.logger.info("Starting neural network analysis")

        # Initialize state
        initial_state = State(initial_data)
        current_state = initial_state

        # Tracking variables
        best_state = current_state
        best_score = current_state.current_score
        operation_history = []

        # Training data collection
        training_data = []

        for iteration in range(max_iterations):
            # Get available operations
            available_operations = list(self.operations.keys())

            # Select action
            operation, parameters = self.select_best_action(current_state, available_operations)

            # Apply operation
            next_state = self.apply_operation(current_state, operation, parameters)

            # Calculate reward
            reward = next_state.current_score - current_state.current_score

            # Store experience
            self.remember(current_state, operation, parameters, next_state, reward)

            # Collect training data
            training_data.append((current_state, operation, parameters, reward))

            # Update best state
            if next_state.current_score > best_score:
                best_state = next_state
                best_score = next_state.current_score

            # Record operation
            operation_history.append({
                'iteration': iteration,
                'operation': operation,
                'parameters': parameters,
                'score_before': current_state.current_score,
                'score_after': next_state.current_score,
                'improvement': reward
            })

            # Update current state
            current_state = next_state

            # Periodic training
            if iteration % 50 == 0 and len(training_data) >= self.batch_size:
                self.train(training_data[-self.batch_size:])
                self.replay()

            # Logging
            if iteration % 100 == 0:
                self.logger.info(f"Iteration {iteration}: Score = {best_score:.4f}, "
                               f"Epsilon = {self.epsilon:.4f}")

        # Final training round
        if len(training_data) >= self.batch_size:
            self.train(training_data[-self.batch_size:])
            self.replay()

        # Calculate statistics
        total_improvements = sum(1 for op in operation_history if op['improvement'] > 0)
        self.prediction_accuracy = total_improvements / len(operation_history) if operation_history else 0

        # Generate results
        results = {
            'strategy': 'neural_network',
            'iterations': max_iterations,
            'best_score': best_score,
            'initial_score': initial_state.current_score,
            'improvement': best_score - initial_state.current_score,
            'total_operations': len(operation_history),
            'operation_history': operation_history,
            'final_state': best_state,
            'neural_network_stats': {
                'epsilon': self.epsilon,
                'prediction_accuracy': self.prediction_accuracy,
                'exploration_count': self.exploration_count,
                'exploitation_count': self.exploitation_count,
                'memory_size': len(self.memory),
                'training_loss_history': self.training_history[-10:] if self.training_history else []
            }
        }

        self.logger.info(f"Neural network analysis complete. Best score: {best_score:.4f}")
        return results

    def save_model(self, filepath: str):
        """Save trained neural network model"""
        model_data = {
            'weights': [w.tolist() for w in self.weights],
            'bias': [b.tolist() for b in self.bias],
            'config': {
                'input_size': self.input_size,
                'hidden_sizes': self.hidden_sizes,
                'output_size': self.output_size,
                'epsilon': self.epsilon
            },
            'training_history': self.training_history,
            'performance_stats': {
                'prediction_accuracy': self.prediction_accuracy,
                'exploration_count': self.exploration_count,
                'exploitation_count': self.exploitation_count
            }
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

    def load_model(self, filepath: str):
        """Load trained neural network model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.weights = [np.array(w) for w in model_data['weights']]
        self.bias = [np.array(b) for b in model_data['bias']]

        config = model_data['config']
        self.input_size = config['input_size']
        self.hidden_sizes = config['hidden_sizes']
        self.output_size = config['output_size']
        self.epsilon = config['epsilon']

        self.training_history = model_data.get('training_history', [])

        stats = model_data.get('performance_stats', {})
        self.prediction_accuracy = stats.get('prediction_accuracy', 0.0)
        self.exploration_count = stats.get('exploration_count', 0)
        self.exploitation_count = stats.get('exploitation_count', 0)

    def export_training_data(self, filepath: str):
        """Export training data for external analysis"""
        training_data = []

        for experience in self.memory:
            state, operation, parameters, next_state, reward = experience

            training_sample = {
                'state_features': self._extract_features(state).tolist(),
                'operation': operation,
                'parameters': parameters,
                'reward': reward,
                'score_improvement': next_state.current_score - state.current_score
            }

            training_data.append(training_sample)

        with open(filepath, 'w') as f:
            json.dump(training_data, f, indent=2)

    def get_network_summary(self) -> Dict[str, Any]:
        """Get summary of neural network architecture and performance"""
        total_params = sum(w.size + b.size for w, b in zip(self.weights, self.bias))

        return {
            'architecture': {
                'input_size': self.input_size,
                'hidden_layers': self.hidden_sizes,
                'output_size': self.output_size,
                'total_parameters': int(total_params)
            },
            'training': {
                'learning_rate': self.learning_rate,
                'batch_size': self.batch_size,
                'current_epsilon': self.epsilon,
                'memory_usage': f"{len(self.memory)}/{self.memory_size}",
                'training_samples': len(self.training_history)
            },
            'performance': {
                'prediction_accuracy': self.prediction_accuracy,
                'exploration_rate': self.exploration_count / max(1, self.exploration_count + self.exploitation_count),
                'total_experiences': len(self.memory)
            }
        }