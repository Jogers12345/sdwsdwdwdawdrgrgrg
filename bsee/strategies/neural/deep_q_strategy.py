"""
Deep Q-Network Strategy for BSEE
Advanced deep learning strategy using experience replay and target networks
"""

import numpy as np
import random
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import pickle
import json
from pathlib import Path
import copy

from bsee.strategies.base_strategy import BaseStrategy
from bsee.engine.state import State


class DeepQNetworkStrategy(BaseStrategy):
    """
    Deep Q-Network strategy with experience replay and target network updates
    for stable learning in binary structure exploration.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        # Network architecture
        self.state_size = config.get('state_size', 200)
        self.action_size = config.get('action_size', 64)
        self.hidden_layers = config.get('hidden_layers', [256, 128, 64])

        # Learning parameters
        self.learning_rate = config.get('learning_rate', 0.0001)
        self.gamma = config.get('gamma', 0.95)  # Discount factor
        self.epsilon = config.get('epsilon', 1.0)
        self.epsilon_min = config.get('epsilon_min', 0.01)
        self.epsilon_decay = config.get('epsilon_decay', 0.995)

        # Experience replay
        self.memory_size = config.get('memory_size', 50000)
        self.memory = deque(maxlen=self.memory_size)
        self.batch_size = config.get('batch_size', 64)

        # Target network
        self.target_update_freq = config.get('target_update_freq', 1000)
        self.target_update_counter = 0
        self.target_weights = None
        self.target_bias = None

        # Training parameters
        self.training_episodes = config.get('training_episodes', 1000)
        self.training_start = config.get('training_start', 1000)  # Start training after this many steps

        # Networks
        self.q_network_weights = self._initialize_network()
        self.q_network_bias = self._initialize_bias()
        self._initialize_target_network()

        # Statistics
        self.training_step = 0
        self.episode_rewards = []
        self.losses = []
        self.q_values_history = []

        # Operation encoding
        self.operation_encoding = self._create_operation_encoding()

    def _initialize_network(self) -> List[np.ndarray]:
        """Initialize Q-network weights with He initialization"""
        weights = []
        layer_sizes = [self.state_size] + self.hidden_layers + [self.action_size]

        for i in range(len(layer_sizes) - 1):
            fan_in = layer_sizes[i]
            std = np.sqrt(2.0 / fan_in)  # He initialization
            weights.append(np.random.normal(0, std, (fan_in, layer_sizes[i + 1])))

        return weights

    def _initialize_bias(self) -> List[np.ndarray]:
        """Initialize network biases"""
        bias = []
        layer_sizes = [self.state_size] + self.hidden_layers + [self.action_size]

        for size in layer_sizes[1:]:
            bias.append(np.zeros(size))

        return bias

    def _initialize_target_network(self):
        """Initialize target network as copy of main network"""
        self.target_weights = [w.copy() for w in self.q_network_weights]
        self.target_bias = [b.copy() for b in self.q_network_bias]

    def _create_operation_encoding(self) -> Dict[str, np.ndarray]:
        """Create encoding for different operations"""
        operations = ['xor', 'add', 'sub', 'rotate', 'reverse', 'substitute', 'compress', 'decompress']
        encoding = {}

        for i, op in enumerate(operations):
            # One-hot encoding with some learned features
            vector = np.zeros(len(operations))
            vector[i] = 1.0
            encoding[op] = vector

        return encoding

    def _extract_state_features(self, state: State) -> np.ndarray:
        """Extract comprehensive state features"""
        features = []

        # Basic data statistics
        data = state.data
        if len(data) > 0:
            # Byte frequency distribution (normalized)
            byte_freq = np.zeros(64)
            sample_size = min(1024, len(data))
            for byte in data[:sample_size]:
                byte_freq[byte % 64] += 1
            byte_freq = byte_freq / sample_size
            features.extend(byte_freq)

            # Pattern features
            features.extend([
                self._calculate_entropy(data[:256]),
                self._calculate_autocorrelation(data[:256]),
                self._calculate_run_length_encoding_efficiency(data[:512]),
                self._calculate_byte_transition_patterns(data[:256]),
            ])

            # Structural features
            features.extend([
                len(data) / 10000.0,  # Normalized size
                len(set(data)) / 256.0,  # Byte diversity
                self._calculate_repeated_patterns(data[:1024]),
                self._calculate_compression_estimate(data[:512]),
            ])
        else:
            features.extend([0.0] * (64 + 4 + 4))

        # Current state features
        features.extend([
            state.current_score / 100.0,
            state.operations_count / 1000.0,
            state.current_cost / 10000.0,
            self._get_recent_improvement_rate(state),
        ])

        # Operation history features
        features.extend(self._get_operation_history_features(state))

        # Ensure correct size
        features = np.array(features)
        if len(features) > self.state_size:
            features = features[:self.state_size]
        elif len(features) < self.state_size:
            features = np.pad(features, (0, self.state_size - len(features)))

        return features

    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate normalized Shannon entropy"""
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

    def _calculate_autocorrelation(self, data: bytes) -> float:
        """Calculate autocorrelation at lag 1"""
        if len(data) < 2:
            return 0.0

        data_array = np.array([b for b in data])
        correlation = np.corrcoef(data_array[:-1], data_array[1:])[0, 1]

        return (correlation + 1.0) / 2.0 if not np.isnan(correlation) else 0.0

    def _calculate_run_length_encoding_efficiency(self, data: bytes) -> float:
        """Calculate RLE compression efficiency"""
        if len(data) < 2:
            return 0.0

        rle_size = 1
        current_run = 1

        for i in range(1, len(data)):
            if data[i] == data[i-1] and current_run < 255:
                current_run += 1
            else:
                rle_size += 2  # byte + run_length
                current_run = 1

        efficiency = 1.0 - (rle_size / len(data))
        return max(0.0, efficiency)

    def _calculate_byte_transition_patterns(self, data: bytes) -> float:
        """Calculate byte transition pattern regularity"""
        if len(data) < 2:
            return 0.0

        transitions = {}
        for i in range(len(data) - 1):
            transition = (data[i], data[i+1])
            transitions[transition] = transitions.get(transition, 0) + 1

        # Calculate regularity as inverse of transition diversity
        total_transitions = len(data) - 1
        regularity = sum(count**2 for count in transitions.values()) / (total_transitions**2)

        return regularity

    def _calculate_repeated_patterns(self, data: bytes) -> float:
        """Calculate density of repeated patterns"""
        if len(data) < 4:
            return 0.0

        patterns = set()
        for i in range(len(data) - 3):
            pattern = data[i:i+4]
            patterns.add(pattern)

        return 1.0 - (len(patterns) / (len(data) - 3))

    def _calculate_compression_estimate(self, data: bytes) -> float:
        """Estimate compressibility"""
        if len(data) < 8:
            return 0.0

        # Simple compression estimate based on byte repetitions
        unique_bytes = len(set(data))
        compressibility = 1.0 - (unique_bytes / len(data))

        return compressibility

    def _get_recent_improvement_rate(self, state: State) -> float:
        """Calculate recent improvement rate from operation history"""
        if not hasattr(state, 'recent_scores') or len(state.recent_scores) < 2:
            return 0.0

        recent_scores = state.recent_scores[-10:]  # Last 10 operations
        if len(recent_scores) < 2:
            return 0.0

        improvements = [recent_scores[i+1] - recent_scores[i] for i in range(len(recent_scores)-1)]
        positive_improvements = sum(1 for imp in improvements if imp > 0)

        return positive_improvements / len(improvements) if improvements else 0.0

    def _get_operation_history_features(self, state: State) -> List[float]:
        """Extract features from operation history"""
        features = []

        # Operation type frequencies
        op_counts = {'xor': 0, 'add': 0, 'sub': 0, 'rotate': 0, 'substitute': 0}
        total_ops = len(state.operation_history) if hasattr(state, 'operation_history') else 0

        if total_ops > 0:
            for op in state.operation_history[-20:]:  # Last 20 operations
                op_type = op.split('_')[0] if '_' in op else op
                if op_type in op_counts:
                    op_counts[op_type] += 1

            for op_type in op_counts:
                features.append(op_counts[op_type] / min(20, total_ops))
        else:
            features.extend([0.0] * len(op_counts))

        return features

    def _forward_pass(self, state_features: np.ndarray, weights: List[np.ndarray],
                      bias: List[np.ndarray]) -> List[np.ndarray]:
        """Forward pass through network"""
        activations = [state_features]

        for i, (W, b) in enumerate(zip(weights, bias)):
            z = np.dot(activations[-1], W) + b

            if i < len(weights) - 1:  # Hidden layers - Leaky ReLU
                a = np.where(z > 0, z, 0.01 * z)
            else:  # Output layer - Linear
                a = z

            activations.append(a)

        return activations

    def predict_q_values(self, state: State, use_target_network: bool = False) -> np.ndarray:
        """Predict Q-values for all actions"""
        state_features = self._extract_state_features(state)

        if use_target_network:
            weights = self.target_weights
            bias = self.target_bias
        else:
            weights = self.q_network_weights
            bias = self.q_network_bias

        activations = self._forward_pass(state_features, weights, bias)
        return activations[-1]

    def select_action(self, state: State, available_operations: List[str]) -> Tuple[str, Dict[str, Any]]:
        """Select action using epsilon-greedy policy"""
        if random.random() < self.epsilon:
            # Exploration
            operation = random.choice(available_operations)
            parameters = self._generate_random_parameters(operation)
            return operation, parameters
        else:
            # Exploitation
            q_values = self.predict_q_values(state)

            # Select best action from available operations
            valid_actions = q_values[:len(available_operations)]
            best_action_idx = np.argmax(valid_actions)
            operation = available_operations[best_action_idx]

            parameters = self._generate_learned_parameters(operation, q_values[best_action_idx])
            return operation, parameters

    def _generate_random_parameters(self, operation: str) -> Dict[str, Any]:
        """Generate random parameters for operation"""
        params = {}

        if 'xor' in operation.lower():
            params['key'] = random.randint(0, 255)
        elif 'add' in operation.lower() or 'sub' in operation.lower():
            params['value'] = random.randint(0, 255)
        elif 'rotate' in operation.lower():
            params['bits'] = random.randint(1, 7)
        elif 'substitute' in operation.lower():
            params['pattern'] = bytes([random.randint(0, 255) for _ in range(4)])
            params['replacement'] = bytes([random.randint(0, 255) for _ in range(4)])

        return params

    def _generate_learned_parameters(self, operation: str, q_value: float) -> Dict[str, Any]:
        """Generate parameters based on learned Q-value"""
        params = {}
        confidence = (q_value + 10.0) / 20.0  # Normalize Q-value to confidence

        if 'xor' in operation.lower():
            # Use learned effective XOR keys
            if confidence > 0.7:
                params['key'] = random.choice([0x55, 0xAA, 0xFF, 0x00, 0x5A, 0xA5])
            else:
                params['key'] = int(confidence * 255)

        elif 'add' in operation.lower() or 'sub' in operation.lower():
            # Use learned effective values
            if confidence > 0.6:
                params['value'] = random.choice([1, 2, 4, 8, 16, 32, 64, 128])
            else:
                params['value'] = int(confidence * 255)

        elif 'rotate' in operation.lower():
            # Learn optimal rotation amounts
            if confidence > 0.5:
                params['bits'] = random.choice([1, 2, 3, 4])
            else:
                params['bits'] = random.randint(1, 7)

        elif 'substitute' in operation.lower():
            # Generate substitution based on confidence
            pattern_length = 4 if confidence > 0.4 else 2
            params['pattern'] = bytes([int(confidence * 255) for _ in range(pattern_length)])
            params['replacement'] = bytes([int((1 - confidence) * 255) for _ in range(pattern_length)])

        return params

    def remember(self, state: State, action: str, parameters: Dict[str, Any],
                 reward: float, next_state: State, done: bool):
        """Store experience in replay memory"""
        experience = (state, action, parameters, reward, next_state, done)
        self.memory.append(experience)

    def replay(self):
        """Train network on replay memory"""
        if len(self.memory) < self.batch_size:
            return

        # Sample random batch from memory
        batch = random.sample(self.memory, self.batch_size)

        # Prepare training data
        states = []
        target_q_values = []

        for state, action, parameters, reward, next_state, done in batch:
            state_features = self._extract_state_features(state)
            current_q_values = self.predict_q_values(state)

            if done:
                target = reward
            else:
                next_q_values = self.predict_q_values(next_state, use_target_network=True)
                target = reward + self.gamma * np.max(next_q_values)

            # Update Q-value for taken action
            action_idx = list(self.operations.keys()).index(action) if action in self.operations else 0
            current_q_values[action_idx] = target

            states.append(state_features)
            target_q_values.append(current_q_values)

        # Convert to numpy arrays
        states = np.array(states)
        target_q_values = np.array(target_q_values)

        # Train network
        self._train_network_batch(states, target_q_values)

        # Update target network
        self.target_update_counter += 1
        if self.target_update_counter >= self.target_update_freq:
            self._update_target_network()
            self.target_update_counter = 0

    def _train_network_batch(self, states: np.ndarray, targets: np.ndarray):
        """Train network on a batch of data"""
        total_loss = 0.0

        for i in range(len(states)):
            # Forward pass
            activations = self._forward_pass(states[i], self.q_network_weights, self.q_network_bias)

            # Calculate loss (MSE)
            loss = np.mean((activations[-1] - targets[i]) ** 2)
            total_loss += loss

            # Backward pass
            error = activations[-1] - targets[i]

            # Update weights and biases
            for j in range(len(self.q_network_weights) - 1, -1, -1):
                if j > 0:
                    # Hidden layer gradients
                    delta = np.dot(error, self.q_network_weights[j].T)
                    # Leaky ReLU derivative
                    delta = delta * np.where(activations[j] > 0, 1, 0.01)
                    error = delta

                # Update weights
                weight_gradient = np.outer(activations[j], error)
                self.q_network_weights[j] -= self.learning_rate * weight_gradient
                self.q_network_bias[j] -= self.learning_rate * error

        avg_loss = total_loss / len(states)
        self.losses.append(avg_loss)

    def _update_target_network(self):
        """Update target network weights"""
        for i in range(len(self.q_network_weights)):
            # Soft update: target = tau * main + (1 - tau) * target
            tau = 0.1  # Soft update rate
            self.target_weights[i] = (tau * self.q_network_weights[i] +
                                     (1 - tau) * self.target_weights[i])
            self.target_bias[i] = (tau * self.q_network_bias[i] +
                                  (1 - tau) * self.target_bias[i])

    def analyze(self, initial_data: bytes, max_iterations: int = 1000) -> Dict[str, Any]:
        """Analyze binary data using Deep Q-Network strategy"""
        self.logger.info("Starting Deep Q-Network analysis")

        # Initialize state
        initial_state = State(initial_data)
        current_state = initial_state

        # Tracking variables
        best_state = current_state
        best_score = current_state.current_score
        episode_rewards = []
        operation_history = []

        for episode in range(max_iterations):
            # Get available operations
            available_operations = list(self.operations.keys())

            # Select and execute action
            operation, parameters = self.select_action(current_state, available_operations)
            next_state = self.apply_operation(current_state, operation, parameters)

            # Calculate reward
            reward = next_state.current_score - current_state.current_score
            episode_rewards.append(reward)

            # Check if episode is done (no improvement or max operations)
            done = (self.operations_count >= max_iterations or
                   len(operation_history) > 0 and abs(reward) < 0.001)

            # Store experience
            self.remember(current_state, operation, parameters, reward, next_state, done)

            # Update best state
            if next_state.current_score > best_score:
                best_state = next_state
                best_score = next_state.current_score

            # Record operation
            operation_history.append({
                'episode': episode,
                'operation': operation,
                'parameters': parameters,
                'score_before': current_state.current_score,
                'score_after': next_state.current_score,
                'reward': reward,
                'epsilon': self.epsilon
            })

            # Update current state
            current_state = next_state
            self.training_step += 1

            # Train network
            if len(self.memory) > self.training_start:
                self.replay()

            # Decay epsilon
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

            # Logging
            if episode % 100 == 0:
                avg_reward = np.mean(episode_rewards[-100:]) if episode_rewards else 0
                self.logger.info(f"Episode {episode}: Best Score = {best_score:.4f}, "
                               f"Avg Reward = {avg_reward:.4f}, Epsilon = {self.epsilon:.4f}")

            # Early stopping if no improvement
            if len(operation_history) > 100:
                recent_rewards = [op['reward'] for op in operation_history[-100:]]
                if all(abs(r) < 0.001 for r in recent_rewards):
                    self.logger.info("Early stopping: no significant improvement")
                    break

        # Calculate episode statistics
        total_reward = sum(episode_rewards)
        self.episode_rewards.append(total_reward)

        # Generate results
        results = {
            'strategy': 'deep_q_network',
            'episodes': episode + 1,
            'best_score': best_score,
            'initial_score': initial_state.current_score,
            'improvement': best_score - initial_state.current_score,
            'total_reward': total_reward,
            'total_operations': len(operation_history),
            'operation_history': operation_history,
            'final_state': best_state,
            'training_stats': {
                'epsilon': self.epsilon,
                'memory_size': len(self.memory),
                'training_steps': self.training_step,
                'recent_losses': self.losses[-10:] if self.losses else [],
                'episode_rewards': episode_rewards[-100:] if episode_rewards else []
            },
            'network_performance': {
                'prediction_accuracy': self._calculate_prediction_accuracy(operation_history),
                'exploration_rate': sum(1 for op in operation_history[-100:] if op['epsilon'] > random.random()) / min(100, len(operation_history)),
                'average_reward': total_reward / len(episode_rewards) if episode_rewards else 0
            }
        }

        self.logger.info(f"Deep Q-Network analysis complete. Best score: {best_score:.4f}")
        return results

    def _calculate_prediction_accuracy(self, operation_history: List[Dict[str, Any]]) -> float:
        """Calculate prediction accuracy based on operation success"""
        if not operation_history:
            return 0.0

        successful_operations = sum(1 for op in operation_history if op['reward'] > 0)
        return successful_operations / len(operation_history)

    def save_model(self, filepath: str):
        """Save trained model"""
        model_data = {
            'q_network_weights': [w.tolist() for w in self.q_network_weights],
            'q_network_bias': [b.tolist() for b in self.q_network_bias],
            'target_weights': [w.tolist() for w in self.target_weights],
            'target_bias': [b.tolist() for b in self.target_bias],
            'config': {
                'state_size': self.state_size,
                'action_size': self.action_size,
                'hidden_layers': self.hidden_layers,
                'epsilon': self.epsilon
            },
            'training_stats': {
                'episode_rewards': self.episode_rewards,
                'losses': self.losses,
                'training_step': self.training_step
            }
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

    def load_model(self, filepath: str):
        """Load trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        self.q_network_weights = [np.array(w) for w in model_data['q_network_weights']]
        self.q_network_bias = [np.array(b) for b in model_data['q_network_bias']]
        self.target_weights = [np.array(w) for w in model_data['target_weights']]
        self.target_bias = [np.array(b) for b in model_data['target_bias']]

        config = model_data['config']
        self.state_size = config['state_size']
        self.action_size = config['action_size']
        self.hidden_layers = config['hidden_layers']
        self.epsilon = config['epsilon']

        training_stats = model_data.get('training_stats', {})
        self.episode_rewards = training_stats.get('episode_rewards', [])
        self.losses = training_stats.get('losses', [])
        self.training_step = training_stats.get('training_step', 0)

    def get_model_summary(self) -> Dict[str, Any]:
        """Get comprehensive model summary"""
        total_params = sum(w.size + b.size for w, b in
                          zip(self.q_network_weights, self.q_network_bias))

        return {
            'architecture': {
                'state_size': self.state_size,
                'action_size': self.action_size,
                'hidden_layers': self.hidden_layers,
                'total_parameters': int(total_params),
                'network_type': 'Deep Q-Network'
            },
            'training': {
                'learning_rate': self.learning_rate,
                'gamma': self.gamma,
                'epsilon': self.epsilon,
                'batch_size': self.batch_size,
                'memory_size': len(self.memory),
                'training_steps': self.training_step
            },
            'performance': {
                'episodes_completed': len(self.episode_rewards),
                'average_reward': np.mean(self.episode_rewards) if self.episode_rewards else 0,
                'recent_loss': self.losses[-1] if self.losses else 0,
                'memory_utilization': len(self.memory) / self.memory_size
            }
        }