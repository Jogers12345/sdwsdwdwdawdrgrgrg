"""
Homogeneity-Enhanced Neural Network Strategy for BSEE
Integrates the existing neural network implementation with homogeneity optimization
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
from bsee.scoring.homogeneity_scorer import HomogeneityScorer, HomogeneityMetrics


class HomogeneityNeuralStrategy(BaseStrategy):
    """
    Enhanced neural network strategy specifically designed for homogeneity optimization.
    Combines the existing neural network implementation with homogeneity-focused scoring.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Initialize homogeneity scorer for targeted optimization
        self.homogeneity_scorer = HomogeneityScorer()

        # Neural network architecture parameters (from existing implementation)
        self.input_size = config.get('input_size', 256)
        self.hidden_sizes = config.get('hidden_sizes', [128, 64, 32])
        self.output_size = config.get('output_size', 64)
        self.learning_rate = config.get('learning_rate', 0.001)
        self.batch_size = config.get('batch_size', 32)
        self.epochs = config.get('epochs', 100)

        # Exploration parameters (epsilon-greedy strategy)
        self.epsilon = config.get('epsilon', 0.1)
        self.epsilon_decay = config.get('epsilon_decay', 0.995)
        self.epsilon_min = config.get('epsilon_min', 0.01)

        # Memory for experience replay
        self.memory_size = config.get('memory_size', 10000)
        self.memory = deque(maxlen=self.memory_size)

        # Network state
        self.weights = self._initialize_network()
        self.bias = self._initialize_bias()
        self.training_history = []

        # Performance tracking for homogeneity optimization
        self.homogeneity_improvements = []
        self.best_homogeneity_score = 0.0
        self.prediction_accuracy = 0.0
        self.exploration_count = 0
        self.exploitation_count = 0

        # Homogeneity-focused configuration
        self.homogeneity_weight = config.get('homogeneity_weight', 0.7)  # Weight for homogeneity in scoring
        self.segment_size = config.get('segment_size', 64)  # Segment size for homogeneity analysis

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

    def _extract_homogeneity_features(self, state: State) -> np.ndarray:
        """
        Extract comprehensive features focused on homogeneity characteristics.
        This extends the existing feature extraction with homogeneity-specific metrics.
        """
        features = []

        # Get detailed homogeneity metrics
        homogeneity_metrics = self.homogeneity_scorer.analyze_homogeneity(state.data, self.segment_size)

        # Core homogeneity features (the most important for optimization)
        features.extend([
            homogeneity_metrics.overall_score,
            homogeneity_metrics.entropy_uniformity,
            homogeneity_metrics.pattern_consistency,
            homogeneity_metrics.structural_uniformity,
            homogeneity_metrics.avg_segment_entropy,
            homogeneity_metrics.entropy_variance,
            homogeneity_metrics.repetition_ratio,
            homogeneity_metrics.predictability_index
        ])

        # Traditional statistical features (from existing implementation)
        if len(state.data) > 0:
            # Byte frequency histogram (compressed for neural network input)
            byte_counts = np.zeros(64)  # Reduced from 128 for efficiency
            sample_size = min(1024, len(state.data))
            for byte in state.data[:sample_size]:
                byte_counts[byte % 64] += 1
            byte_counts = byte_counts / sample_size  # Normalize
            features.extend(byte_counts)

            # Additional statistical features
            byte_entropy = self._calculate_entropy(state.data[:256])
            pattern_density = self._calculate_pattern_density(state.data[:256])
            compression_ratio = self._estimate_compression_ratio(state.data[:512])

            features.extend([
                byte_entropy,
                pattern_density,
                compression_ratio,
                len(state.data) / 1024.0,  # Size in KB
                len(set(state.data)) / 256.0,  # Byte diversity
            ])
        else:
            # Pad with zeros if no data
            features.extend([0.0] * (64 + 5))

        # Current state features (homogeneity-focused)
        features.extend([
            state.current_score,  # Current homogeneity score
            state.operations_count / 100.0,  # Normalized operation count
            state.current_cost / 10000.0,  # Normalized cost
            homogeneity_metrics.segment_count / 100.0,  # Number of segments analyzed
        ])

        # Convert to numpy array and ensure correct size
        features = np.array(features, dtype=np.float32)

        # Pad or truncate to input size
        if len(features) > self.input_size:
            features = features[:self.input_size]
        elif len(features) < self.input_size:
            features = np.pad(features, (0, self.input_size - len(features)), 'constant')

        return features

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data (from existing implementation)"""
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
        """Calculate density of repeating patterns (from existing implementation)"""
        if len(data) < 4:
            return 0.0

        patterns = set()
        for i in range(len(data) - 3):
            pattern = data[i:i+4]
            patterns.add(pattern)

        return len(patterns) / (len(data) - 3)

    def _estimate_compression_ratio(self, data: bytes) -> float:
        """Estimate compression ratio (from existing implementation)"""
        if len(data) < 8:
            return 1.0

        # Count repeated sequences
        repeated_bytes = 0
        for i in range(len(data) - 1):
            if data[i] == data[i + 1]:
                repeated_bytes += 1

        return (len(data) - repeated_bytes) / len(data) if data else 1.0

    def _forward_pass(self, x: np.ndarray) -> List[np.ndarray]:
        """Forward pass through neural network (from existing implementation)"""
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
        """Backward pass for gradient computation (from existing implementation)"""
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
        """Update network weights using gradient descent (from existing implementation)"""
        for i in range(len(self.weights)):
            self.weights[i] -= self.learning_rate * gradients_W[i]
            self.bias[i] -= self.learning_rate * gradients_b[i]

    def predict_homogeneity_improvement(self, state: State) -> np.ndarray:
        """Predict homogeneity improvement values for possible operations"""
        features = self._extract_homogeneity_features(state)
        activations = self._forward_pass(features)
        return activations[-1]  # Output layer activations

    def select_best_homogeneity_action(self, state: State, available_operations: List[str]) -> Tuple[str, Dict[str, Any]]:
        """
        Select best action using epsilon-greedy strategy focused on homogeneity improvement.
        """
        if random.random() < self.epsilon:
            # Exploration: random action
            self.exploration_count += 1
            operation = random.choice(available_operations)
            parameters = self._generate_homogeneity_parameters(operation, state)
            return operation, parameters
        else:
            # Exploitation: best predicted action for homogeneity
            self.exploitation_count += 1
            action_values = self.predict_homogeneity_improvement(state)

            # Map action values to operations
            best_idx = np.argmax(action_values)
            operation = available_operations[best_idx % len(available_operations)]
            parameters = self._generate_homogeneity_parameters(operation, state, action_values[best_idx])

            return operation, parameters

    def _generate_homogeneity_parameters(self, operation: str, state: State, action_value: float = None) -> Dict[str, Any]:
        """
        Generate parameters specifically designed to improve homogeneity.
        This is more intelligent than random parameter generation.
        """
        params = {}

        # Get current homogeneity metrics to guide parameter selection
        current_metrics = self.homogeneity_scorer.analyze_homogeneity(state.data, self.segment_size)

        # Use action value to bias parameter selection towards homogeneity improvement
        if action_value is not None:
            bias = (action_value + 1.0) / 2.0  # Normalize to [0, 1]
        else:
            bias = 0.5

        if 'xor' in operation.lower():
            # Choose XOR keys that tend to increase patterns
            if current_metrics.entropy_uniformity < 0.5:  # Low uniformity, need pattern creation
                # Use keys that create repeating patterns
                params['key'] = random.choice([0x55, 0xAA, 0xFF, 0x00, 0x33, 0xCC])
            else:  # High uniformity, can be more experimental
                if bias > 0.7:
                    params['key'] = random.choice([0x55, 0xAA, 0xFF, 0x00])
                else:
                    params['key'] = int(random.random() * 256)

        elif 'rotate' in operation.lower():
            # Rotation amounts that often improve homogeneity
            if bias > 0.6:
                params['bits'] = random.choice([1, 2, 4])  # Even rotations often create patterns
            else:
                params['bits'] = random.randint(1, 7)

        elif 'add' in operation.lower():
            # Constants that can create patterns
            if bias > 0.5:
                params['constant'] = random.choice([1, 16, 32, 64, 128, 255])
            else:
                params['constant'] = int(random.random() * 256)

        elif 'substitute' in operation.lower():
            # Pattern substitution based on current homogeneity
            if current_metrics.pattern_consistency < 0.5:
                # Low consistency, create strong patterns
                pattern_length = 2 if bias > 0.3 else 4
                pattern_byte = int(random.random() * 256)
                params['pattern'] = bytes([pattern_byte] * pattern_length)
                params['replacement'] = bytes([(pattern_byte + 128) % 256] * pattern_length)
            else:
                # Higher consistency, can be more experimental
                pattern_length = 4 if bias > 0.3 else 2
                params['pattern'] = bytes([int(random.random() * 256) for _ in range(pattern_length)])
                params['replacement'] = bytes([int(random.random() * 256) for _ in range(pattern_length)])

        elif 'burrows_wheeler' in operation.lower():
            # BWT parameters - usually doesn't need extra params
            pass

        elif 'huffman' in operation.lower():
            # Huffman coding parameters
            pass

        return params

    def calculate_homogeneity_reward(self, old_state: State, new_state: State) -> float:
        """
        Calculate reward specifically focused on homogeneity improvement.
        """
        # Get homogeneity metrics for both states
        old_metrics = self.homogeneity_scorer.analyze_homogeneity(old_state.data, self.segment_size)
        new_metrics = self.homogeneity_scorer.analyze_homogeneity(new_state.data, self.segment_size)

        # Primary reward: homogeneity score improvement
        homogeneity_improvement = new_metrics.overall_score - old_metrics.overall_score

        # Secondary rewards: individual metric improvements
        entropy_improvement = new_metrics.entropy_uniformity - old_metrics.entropy_uniformity
        pattern_improvement = new_metrics.pattern_consistency - old_metrics.pattern_consistency
        structural_improvement = new_metrics.structural_uniformity - old_metrics.structural_uniformity

        # Combined reward with weighted focus
        total_reward = (
            self.homogeneity_weight * homogeneity_improvement +
            0.1 * entropy_improvement +
            0.1 * pattern_improvement +
            0.1 * structural_improvement
        )

        # Bonus for significant improvements
        if homogeneity_improvement > 0.1:
            total_reward += 0.5  # Significant improvement bonus
        elif homogeneity_improvement > 0.05:
            total_reward += 0.2  # Moderate improvement bonus

        # Penalty for making homogeneity worse
        if homogeneity_improvement < -0.05:
            total_reward -= 0.3

        return total_reward

    def remember(self, state: State, operation: str, parameters: Dict[str, Any],
                 next_state: State, reward: float):
        """Store homogeneity-focused experience in memory for training"""
        experience = (state, operation, parameters, next_state, reward)
        self.memory.append(experience)

    def train_homogeneity_network(self, training_data: List[Tuple[State, str, Dict[str, Any], float]]):
        """Train the neural network specifically for homogeneity optimization"""
        if len(training_data) < self.batch_size:
            return

        # Prepare training data focused on homogeneity
        for epoch in range(min(self.epochs, len(training_data) // self.batch_size)):
            batch = random.sample(training_data, min(self.batch_size, len(training_data)))

            total_loss = 0.0

            for state, operation, parameters, reward in batch:
                features = self._extract_homogeneity_features(state)
                target_q = np.zeros(self.output_size)

                # Use homogeneity reward to update Q-value
                action_values = self.predict_homogeneity_improvement(state)
                target_q = action_values.copy()

                # Q-learning update focused on homogeneity improvement
                if reward > 0:
                    # Positive reward: reinforce this action
                    target_q[np.argmax(action_values)] = min(reward, 1.0)  # Cap at 1.0
                else:
                    # Negative reward: discourage this action
                    target_q *= 0.9

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

        # Decay epsilon for less exploration over time
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def replay_homogeneity_experiences(self):
        """Train network on stored homogeneity-focused experiences"""
        if len(self.memory) < self.batch_size:
            return

        # Sample from memory
        batch = random.sample(list(self.memory), min(self.batch_size, len(self.memory)))
        training_data = []

        for state, operation, parameters, next_state, reward in batch:
            training_data.append((state, operation, parameters, reward))

        self.train_homogeneity_network(training_data)

    def analyze_for_homogeneity(self, initial_data: bytes, max_iterations: int = 1000) -> Dict[str, Any]:
        """
        Analyze binary data using neural network strategy specifically for homogeneity optimization.
        """
        self.logger.info("Starting homogeneity-focused neural network analysis")

        # Initialize state
        initial_state = State(initial_data)

        # Calculate initial homogeneity score
        initial_homogeneity = self.homogeneity_scorer.calculate_homogeneity_score(initial_data, self.segment_size)
        initial_state.current_score = initial_homogeneity
        self.best_homogeneity_score = initial_homogeneity

        current_state = initial_state

        # Tracking variables
        best_state = current_state
        best_score = initial_homogeneity
        operation_history = []
        homogeneity_progress = []

        # Training data collection
        training_data = []

        for iteration in range(max_iterations):
            # Get available operations
            available_operations = list(self.operations.keys())

            # Select best action for homogeneity improvement
            operation, parameters = self.select_best_homogeneity_action(current_state, available_operations)

            # Apply operation
            next_state = self.apply_operation(current_state, operation, parameters)

            # Calculate new homogeneity score
            new_homogeneity = self.homogeneity_scorer.calculate_homogeneity_score(next_state.data, self.segment_size)
            next_state.current_score = new_homogeneity

            # Calculate homogeneity-focused reward
            reward = self.calculate_homogeneity_reward(current_state, next_state)

            # Store experience
            self.remember(current_state, operation, parameters, next_state, reward)

            # Collect training data
            training_data.append((current_state, operation, parameters, reward))

            # Track homogeneity improvement
            homogeneity_progress.append({
                'iteration': iteration,
                'homogeneity_score': new_homogeneity,
                'improvement': new_homogeneity - best_score
            })

            # Update best state if homogeneity improved
            if new_homogeneity > best_score:
                best_state = next_state
                best_score = new_homogeneity
                self.best_homogeneity_score = best_score
                self.homogeneity_improvements.append(new_homogeneity - initial_homogeneity)

            # Record operation with homogeneity focus
            operation_history.append({
                'iteration': iteration,
                'operation': operation,
                'parameters': parameters,
                'homogeneity_before': current_state.current_score,
                'homogeneity_after': new_homogeneity,
                'improvement': reward,
                'entropy_uniformity': self.homogeneity_scorer.analyze_homogeneity(next_state.data, self.segment_size).entropy_uniformity,
                'pattern_consistency': self.homogeneity_scorer.analyze_homogeneity(next_state.data, self.segment_size).pattern_consistency
            })

            # Update current state
            current_state = next_state

            # Periodic training on homogeneity experiences
            if iteration % 50 == 0 and len(training_data) >= self.batch_size:
                self.train_homogeneity_network(training_data[-self.batch_size:])
                self.replay_homogeneity_experiences()

            # Enhanced logging for homogeneity progress
            if iteration % 100 == 0:
                current_metrics = self.homogeneity_scorer.analyze_homogeneity(current_state.data, self.segment_size)
                self.logger.info(f"Iteration {iteration}: Homogeneity = {best_score:.4f}, "
                               f"Entropy Uniformity = {current_metrics.entropy_uniformity:.4f}, "
                               f"Pattern Consistency = {current_metrics.pattern_consistency:.4f}, "
                               f"Epsilon = {self.epsilon:.4f}")

        # Final training round on homogeneity data
        if len(training_data) >= self.batch_size:
            self.train_homogeneity_network(training_data[-self.batch_size:])
            self.replay_homogeneity_experiences()

        # Calculate final statistics
        total_improvements = sum(1 for op in operation_history if op['improvement'] > 0)
        self.prediction_accuracy = total_improvements / len(operation_history) if operation_history else 0

        # Get final comprehensive homogeneity metrics
        final_metrics = self.homogeneity_scorer.analyze_homogeneity(best_state.data, self.segment_size)

        # Generate comprehensive results
        results = {
            'strategy': 'homogeneity_neural_network',
            'iterations': max_iterations,
            'best_homogeneity_score': best_score,
            'initial_homogeneity_score': initial_homogeneity,
            'homogeneity_improvement': best_score - initial_homogeneity,
            'improvement_percentage': ((best_score - initial_homogeneity) / initial_homogeneity * 100) if initial_homogeneity > 0 else 0,
            'total_operations': len(operation_history),
            'operation_history': operation_history,
            'homogeneity_progress': homogeneity_progress,
            'final_state': best_state,
            'final_homogeneity_metrics': {
                'overall_score': final_metrics.overall_score,
                'entropy_uniformity': final_metrics.entropy_uniformity,
                'pattern_consistency': final_metrics.pattern_consistency,
                'structural_uniformity': final_metrics.structural_uniformity,
                'avg_segment_entropy': final_metrics.avg_segment_entropy,
                'entropy_variance': final_metrics.entropy_variance,
                'repetition_ratio': final_metrics.repetition_ratio,
                'predictability_index': final_metrics.predictability_index
            },
            'neural_network_stats': {
                'epsilon': self.epsilon,
                'prediction_accuracy': self.prediction_accuracy,
                'exploration_count': self.exploration_count,
                'exploitation_count': self.exploitation_count,
                'memory_size': len(self.memory),
                'training_loss_history': self.training_history[-10:] if self.training_history else [],
                'homogeneity_improvements': self.homogeneity_improvements[-20:] if self.homogeneity_improvements else []
            },
            'performance_summary': {
                'successful_operations': total_improvements,
                'success_rate': self.prediction_accuracy,
                'best_iteration': operation_history.index(max(operation_history, key=lambda x: x['improvement'])) if operation_history else 0,
                'average_improvement': np.mean([op['improvement'] for op in operation_history]) if operation_history else 0
            }
        }

        self.logger.info(f"Homogeneity neural network analysis complete. Best homogeneity score: {best_score:.4f} "
                        f"(improvement: {best_score - initial_homogeneity:.4f})")
        return results

    def save_homogeneity_model(self, filepath: str):
        """Save trained homogeneity-focused neural network model"""
        model_data = {
            'weights': [w.tolist() for w in self.weights],
            'bias': [b.tolist() for b in self.bias],
            'config': {
                'input_size': self.input_size,
                'hidden_sizes': self.hidden_sizes,
                'output_size': self.output_size,
                'epsilon': self.epsilon,
                'homogeneity_weight': self.homogeneity_weight,
                'segment_size': self.segment_size
            },
            'training_history': self.training_history,
            'homogeneity_improvements': self.homogeneity_improvements,
            'performance_stats': {
                'best_homogeneity_score': self.best_homogeneity_score,
                'prediction_accuracy': self.prediction_accuracy,
                'exploration_count': self.exploration_count,
                'exploitation_count': self.exploitation_count
            }
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

    def load_homogeneity_model(self, filepath: str):
        """Load trained homogeneity-focused neural network model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.weights = [np.array(w) for w in model_data['weights']]
        self.bias = [np.array(b) for b in model_data['bias']]

        config = model_data['config']
        self.input_size = config['input_size']
        self.hidden_sizes = config['hidden_sizes']
        self.output_size = config['output_size']
        self.epsilon = config['epsilon']
        self.homogeneity_weight = config.get('homogeneity_weight', 0.7)
        self.segment_size = config.get('segment_size', 64)

        self.training_history = model_data.get('training_history', [])
        self.homogeneity_improvements = model_data.get('homogeneity_improvements', [])

        stats = model_data.get('performance_stats', {})
        self.best_homogeneity_score = stats.get('best_homogeneity_score', 0.0)
        self.prediction_accuracy = stats.get('prediction_accuracy', 0.0)
        self.exploration_count = stats.get('exploration_count', 0)
        self.exploitation_count = stats.get('exploitation_count', 0)

    def get_homogeneity_network_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of homogeneity-focused neural network"""
        total_params = sum(w.size + b.size for w, b in zip(self.weights, self.bias))

        return {
            'strategy_type': 'Homogeneity Neural Network',
            'optimization_target': 'Binary Homogeneity Improvement',
            'architecture': {
                'input_size': self.input_size,
                'hidden_layers': self.hidden_sizes,
                'output_size': self.output_size,
                'total_parameters': int(total_params)
            },
            'homogeneity_config': {
                'homogeneity_weight': self.homogeneity_weight,
                'segment_size': self.segment_size,
                'best_achieved_score': self.best_homogeneity_score
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
                'total_experiences': len(self.memory),
                'homogeneity_improvements': len(self.homogeneity_improvements)
            }
        }