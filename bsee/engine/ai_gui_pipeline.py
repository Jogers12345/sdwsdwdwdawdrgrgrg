"""
AI-Enhanced GUI Pipeline with Learning and Real-time AI Recommendations
Integrates homogeneity optimization AI with the existing GUI system
"""

import logging
import yaml
import time
import psutil
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Any
from datetime import datetime

# Import existing pipeline components
from bsee.engine.state import State
from bsee.engine.history import HistoryManager, OperationEntry
from bsee.operations.operations_registry import OperationsRegistry
from bsee.metrics.metrics_registry import MetricsRegistry
from bsee.strategies.base_strategy import BaseStrategy
from bsee.strategies.greedy_strategy import GreedyStrategy
from bsee.cost.cost_model import CostModel
from bsee.scoring.scorer import Scorer
from bsee.results.exporter import ResultsExporter
from bsee.utils.validators import validate_config_file

# Import AI components
from bsee_ai.learners.homogeneity_learner import HomogeneityLearner
from bsee_ai.predictors.operation_predictor import OperationPredictor
from bsee_ai.utils.simple_scorer import SimpleHomogeneityScorer


@dataclass
class AIPipelineResults:
    """Enhanced results from AI-enhanced pipeline execution."""
    success: bool
    initial_state: State
    final_state: State
    total_operations: int
    total_cost: float
    total_time: float
    output_directory: str
    final_score: float
    metrics_improvement: Dict[str, float]
    ai_learning_summary: Dict[str, Any]
    ai_recommendations_used: int
    homogeneity_improvement: float


class AIGUIPipeline:
    """AI-enhanced GUI-aware pipeline with learning and real-time recommendations."""

    def __init__(self, args, progress_queue):
        """Initialize AI-enhanced pipeline with CLI arguments and progress queue."""
        self.args = args
        self.progress_queue = progress_queue
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        self.last_update_time = time.time()

        # Load configuration
        self.policy_config = self._load_yaml_config(args.policy)
        self.costs_config = self._load_yaml_config(args.costs)
        self.strategy_config = self._load_strategy_config(args.strategy)

        # Initialize traditional components
        self.operations_registry = OperationsRegistry()
        self.metrics_registry = MetricsRegistry()
        self.history_manager = HistoryManager()
        self.cost_model = CostModel(self.costs_config)
        self.scorer = Scorer(self.policy_config)
        self.exporter = ResultsExporter()

        # Initialize AI components
        self.homogeneity_scorer = SimpleHomogeneityScorer()
        self.ai_learner = HomogeneityLearner()
        self.ai_predictor = OperationPredictor(self.ai_learner)

        # Initialize strategy
        self.strategy = self._create_strategy(args.strategy)

        # Parse user constraints
        self.allowed_operations = self._parse_allowed_operations(args.allowed_ops)
        self.target_metrics = self._parse_target_metrics(args.target_metrics)
        self.requested_metrics = self._parse_metrics(args.metrics)

        # Apply constraints to registries
        self._apply_constraints()

        # Track execution state
        self.current_state: Optional[State] = None
        self.iteration_count = 0
        self.total_cost_spent = 0.0
        self.best_state: Optional[State] = None
        self.no_improvement_count = 0

        # AI tracking
        self.ai_recommendations_used = 0
        self.ai_improvements = 0.0
        self.initial_homogeneity = 0.0
        self.best_homogeneity = 0.0

        # Performance tracking
        self.process = psutil.Process()

        # Send initial AI status
        self._send_ai_status("AI system initialized and ready")

    def run(self) -> AIPipelineResults:
        """Execute the complete AI-enhanced analysis pipeline."""
        try:
            self._send_progress('status', 'Starting AI-enhanced BSEE analysis pipeline...')
            self._send_progress('terminal', 'Starting AI-enhanced BSEE analysis pipeline...', 'info')

            # Phase 1: Initialization with AI analysis
            self._send_progress('status', 'Phase 1: Initialization with AI analysis')
            self._send_progress('terminal', 'Phase 1: Initialization with AI analysis', 'info')
            self._initialize_analysis_with_ai()

            # Phase 2: AI-guided strategy execution
            self._send_progress('status', 'Phase 2: AI-guided strategy execution')
            self._send_progress('terminal', 'Phase 2: AI-guided strategy execution', 'info')
            self._execute_ai_guided_strategy_loop()

            # Phase 3: Results export with AI insights
            self._send_progress('status', 'Phase 3: Results export with AI insights')
            self._send_progress('terminal', 'Phase 3: Results export with AI insights', 'info')
            results = self._export_ai_enhanced_results()

            self._send_progress('status', 'AI-enhanced pipeline execution completed successfully')
            self._send_progress('terminal', 'AI-enhanced pipeline execution completed successfully', 'success')
            return results

        except Exception as e:
            self._send_progress('terminal', f'AI-enhanced pipeline execution failed: {e}', 'error')
            self.logger.error(f"AI-enhanced pipeline execution failed: {e}")
            raise

    def _send_progress(self, msg_type: str, data, level: str = 'info'):
        """Send progress update to GUI."""
        if msg_type == 'terminal':
            message = {'type': msg_type, 'text': data, 'level': level}
        elif msg_type == 'visualization':
            message = {'type': msg_type, **data}
        elif msg_type == 'metrics':
            message = {'type': msg_type, 'metrics': data}
        elif msg_type == 'ai_recommendations':
            message = {'type': msg_type, 'recommendations': data}
        elif msg_type == 'ai_status':
            message = {'type': msg_type, 'status': data}
        elif msg_type in ['status', 'operations', 'score', 'memory', 'progress']:
            message = {'type': msg_type, 'value': data}
        else:
            message = {'type': msg_type, 'data': data}

        try:
            self.progress_queue.put_nowait(message)
        except:
            pass  # Queue might be full

    def _send_ai_status(self, status_message: str):
        """Send AI system status update."""
        self._send_progress('ai_status', status_message)
        self.logger.info(f"AI Status: {status_message}")

    def _send_ai_recommendations(self, recommendations: List[Dict[str, Any]]):
        """Send AI recommendations to GUI."""
        self._send_progress('ai_recommendations', recommendations)

    def _initialize_analysis_with_ai(self) -> None:
        """Initialize the analysis with AI-enhanced data analysis."""
        # Load binary file
        input_path = Path(self.args.input_file)
        with open(input_path, 'rb') as f:
            binary_data = f.read()

        self._send_progress('terminal', f'Loaded binary file: {input_path} ({len(binary_data)} bytes)', 'info')

        # Create initial state
        self.current_state = State(binary_data=binary_data)
        self.best_state = self.current_state

        # AI Analysis of initial data
        self._send_ai_status("AI analyzing initial data characteristics...")
        ai_analysis = self.homogeneity_scorer.analyze_data(binary_data)
        self.initial_homogeneity = ai_analysis['overall_score']
        self.best_homogeneity = self.initial_homogeneity

        # Send AI analysis to GUI
        self._send_progress('ai_analysis', {
            'data_characteristics': ai_analysis['characteristics'],
            'initial_homogeneity': self.initial_homogeneity,
            'unique_bytes': ai_analysis['unique_bytes'],
            'entropy_score': ai_analysis['entropy_score'],
            'pattern_score': ai_analysis['pattern_score'],
            'repetition_score': ai_analysis['repetition_score'],
            'uniformity_score': ai_analysis['uniformity_score']
        })

        # Send initial data to visualization
        self._send_progress('visualization', {
            'binary_data': binary_data,
            'offset': 0
        })

        # Calculate initial metrics
        self._calculate_state_metrics(self.current_state)
        self.current_state.score = self.scorer.calculate_score(
            self.current_state, None, self.target_metrics
        )
        self.best_state.score = self.current_state.score

        # Send initial metrics to GUI
        self._send_progress('metrics', self.current_state.metrics)
        self._send_progress('score', self.current_state.score)

        self._send_progress('terminal', f'Initial score: {self.current_state.score:.2f}', 'info')
        self._send_progress('terminal', f'Initial homogeneity: {self.initial_homogeneity:.4f}', 'info')
        self._log_metrics_summary(self.current_state.metrics, "Initial")

        # Get initial AI recommendations
        initial_recommendations = self.ai_predictor.predict_next_operation(
            binary_data, self.initial_homogeneity, max_sequence_length=3
        )
        self._send_ai_recommendations([
            {
                'operation': pred.operation,
                'parameters': pred.parameters,
                'confidence': pred.confidence,
                'expected_improvement': pred.expected_improvement,
                'reasoning': pred.reasoning
            }
            for pred in initial_recommendations
        ])

        self._send_ai_status(f"AI ready with {len(initial_recommendations)} initial recommendations")

    def _execute_ai_guided_strategy_loop(self) -> None:
        """Execute the AI-guided strategy loop."""
        self._send_progress('terminal', f'Starting AI-guided strategy execution with {self.args.strategy} strategy', 'info')

        # Check convergence criteria
        while not self._should_terminate():
            self.iteration_count += 1

            # Send progress update
            progress = (self.iteration_count / self.args.max_operations) * 100
            self._send_progress('progress', progress)
            self._send_progress('operations', {'current': self.iteration_count, 'max': self.args.max_operations})

            # Get AI recommendations every 5 iterations
            ai_recommendations = []
            if self.iteration_count % 5 == 0:
                self._send_ai_status("AI generating new recommendations...")
                ai_recommendations = self.ai_predictor.predict_next_operation(
                    self.current_state.binary_data,
                    self.homogeneity_scorer.calculate_score(self.current_state.binary_data),
                    max_sequence_length=2
                )
                self._send_ai_recommendations([
                    {
                        'operation': pred.operation,
                        'parameters': pred.parameters,
                        'confidence': pred.confidence,
                        'expected_improvement': pred.expected_improvement,
                        'reasoning': pred.reasoning
                    }
                    for pred in ai_recommendations
                ])

            # Decide between AI recommendation and strategy proposal
            if ai_recommendations and ai_recommendations[0].confidence > 0.4:
                # Use AI recommendation
                ai_pred = ai_recommendations[0]
                operation_name = ai_pred.operation
                params = ai_pred.parameters
                self.ai_recommendations_used += 1
                self._send_progress('terminal',
                    f'Iteration {self.iteration_count}: Using AI recommendation {operation_name} '
                    f'(confidence: {ai_pred.confidence:.2f}, expected improvement: {ai_pred.expected_improvement:.4f})',
                    'info')
            else:
                # Use traditional strategy proposal
                operation_name, params = self.strategy.propose(self.current_state)
                self._send_progress('terminal', f'Iteration {self.iteration_count}: Using strategy proposal {operation_name}', 'debug')

            if not operation_name:
                self._send_progress('terminal', 'No operation proposed, terminating', 'warning')
                break

            # Calculate dynamic cost
            cost = self.cost_model.calculate_cost(
                operation_name, self.history_manager.entries
            )

            # Check budget constraints
            if not self._check_budget_constraints(cost):
                self._send_progress('terminal', 'Budget constraints reached, terminating', 'info')
                break

            # Send operation info
            self._send_progress('visualization', {
                'operation': {
                    'name': operation_name,
                    'params': params,
                    'cost': cost,
                    'ai_recommended': operation_name == (ai_recommendations[0].operation if ai_recommendations else None)
                }
            })

            # Execute operation
            try:
                new_state = self._execute_operation_with_ai(operation_name, params, cost)
                if new_state is None:
                    continue

                # Detect changes for visualization
                changes = self._detect_changes(self.current_state.binary_data, new_state.binary_data)
                if changes:
                    self._send_progress('visualization', {
                        'binary_data': new_state.binary_data,
                        'changes': changes,
                        'operation': {
                            'name': operation_name,
                            'params': params,
                            'cost': cost,
                            'bytes_affected': len(changes)
                        }
                    })

                # Strategy decides accept/reject
                if self.strategy.accept(new_state):
                    self._accept_new_state_with_ai(new_state, operation_name, params)
                    self._send_progress('terminal',
                        f'Accepted {operation_name}: score={new_state.score:.3f}, homogeneity={self.homogeneity_scorer.calculate_score(new_state.binary_data):.4f}',
                        'debug')
                else:
                    self._send_progress('terminal', f'Rejected {operation_name}', 'debug')

            except Exception as e:
                self._send_progress('terminal', f'Error executing operation {operation_name}: {e}', 'error')
                self.logger.error(f"Error executing operation {operation_name}: {e}")
                continue

            # Send periodic updates
            self._send_periodic_update()

            # Log progress periodically
            if self.iteration_count % 10 == 0:
                current_homogeneity = self.homogeneity_scorer.calculate_score(self.current_state.binary_data)
                self._send_progress('terminal',
                    f"Iteration {self.iteration_count}: Score={self.current_state.score:.2f}, "
                    f"Homogeneity={current_homogeneity:.4f}, Cost={self.total_cost_spent:.1f}, "
                    f"Best={self.best_state.score:.2f}, AI recommendations used={self.ai_recommendations_used}", 'info')

    def _execute_operation_with_ai(self, operation_name: str, params: Dict[str, Any], cost: float) -> Optional[State]:
        """Execute an operation with AI tracking."""
        # Get current homogeneity before operation
        old_homogeneity = self.homogeneity_scorer.calculate_score(self.current_state.binary_data)

        # Get operation function
        operation_fn = self.operations_registry.get_operation(operation_name)

        # Apply operation to current binary data
        new_binary, inverse_fn, metadata = operation_fn(self.current_state.binary_data, **params)

        # Create new state
        new_state = State(
            binary_data=new_binary,
            parent_state_id=self.current_state.state_id,
            operation_applied={
                'operation': operation_name,
                'params': params,
                'cost': cost,
                'timestamp': datetime.now().isoformat()
            },
            operation_history=self.current_state.operation_history + [{
                'operation': operation_name,
                'params': params,
                'cost': cost
            }],
            inverse_operations=self.current_state.inverse_operations + [inverse_fn],
            generation=self.current_state.generation + 1
        )

        # Calculate new homogeneity
        new_homogeneity = self.homogeneity_scorer.calculate_score(new_binary)

        # AI learns from this operation
        self.ai_learner.learn_from_result(
            self.current_state.binary_data,
            operation_name,
            params,
            old_homogeneity,
            new_homogeneity
        )

        # Track AI improvement
        improvement = new_homogeneity - old_homogeneity
        if improvement > 0:
            self.ai_improvements += improvement

        # Calculate metrics and score
        self._calculate_state_metrics(new_state)
        new_state.score = self.scorer.calculate_score(
            new_state, self.current_state, self.target_metrics
        )

        return new_state

    def _accept_new_state_with_ai(self, new_state: State, operation_name: str, params: Dict[str, Any]) -> None:
        """Accept a new state with AI tracking."""
        # Create history entry
        entry = OperationEntry(
            step_number=len(self.history_manager.entries) + 1,
            operation_name=new_state.operation_applied['operation'],
            parameters=new_state.operation_applied['params'],
            inverse_function=new_state.inverse_operations[-1],
            cost=new_state.operation_applied['cost'],
            timestamp=new_state.timestamp,
            parent_state_id=self.current_state.state_id,
            resulting_state_id=new_state.state_id,
            effectiveness_score=new_state.score - self.current_state.score
        )

        # Add to history
        self.history_manager.add_entry(entry)

        # Update current state
        self.current_state = new_state
        self.total_cost_spent += new_state.operation_applied['cost']

        # Calculate new homogeneity
        current_homogeneity = self.homogeneity_scorer.calculate_score(self.current_state.binary_data)

        # Send metrics update including homogeneity
        self._send_progress('metrics', new_state.metrics)
        self._send_progress('score', new_state.score)
        self._send_progress('homogeneity', current_homogeneity)

        # Update best state if improved
        if new_state.score > self.best_state.score:
            self.best_state = new_state
            self.best_homogeneity = current_homogeneity
            self.no_improvement_count = 0
            self._send_progress('terminal',
                f"New best state: score={new_state.score:.2f}, homogeneity={current_homogeneity:.4f} "
                f"(score improvement: {new_state.score - self.best_state.score + new_state.score:.2f})", 'success')
        else:
            self.no_improvement_count += 1

    def _detect_changes(self, old_data: bytes, new_data: bytes) -> List[int]:
        """Detect which bytes changed between old and new data."""
        changes = []
        min_len = min(len(old_data), len(new_data))

        for i in range(min_len):
            if old_data[i] != new_data[i]:
                changes.append(i)

        return changes

    def _calculate_state_metrics(self, state: State) -> None:
        """Calculate all requested metrics for a state."""
        metric_results = self.metrics_registry.calculate_metrics(
            state.binary_data, self.requested_metrics
        )
        state.metrics = metric_results

    def _export_ai_enhanced_results(self) -> AIPipelineResults:
        """Export AI-enhanced analysis results to files."""
        # Create output directory with timestamp
        output_dir = self.exporter.create_output_directory(self.args.output_dir)

        # Export all traditional result files
        self.exporter.export_summary(
            output_dir, self.best_state, self.history_manager,
            self.total_cost_spent, self.iteration_count
        )
        self.exporter.export_final_binary(output_dir, self.best_state.binary_data)
        self.exporter.export_inverse_operations(
            output_dir, self.best_state.state_id,
            self.args.input_file, self.history_manager
        )
        self.exporter.export_timeline(output_dir, self.history_manager)
        self.exporter.export_metrics_comparison(
            output_dir, self.current_state, self.best_state
        )
        self.exporter.export_operation_usage(output_dir, self.history_manager)

        # Export AI-specific results
        self._export_ai_results(output_dir)

        # Calculate metrics improvement
        metrics_improvement = {}
        if self.current_state and self.best_state:
            for metric_name in self.requested_metrics:
                initial_val = self.current_state.metrics.get(metric_name, 0)
                final_val = self.best_state.metrics.get(metric_name, 0)
                if initial_val != 0:
                    improvement = (final_val - initial_val) / abs(initial_val) * 100
                else:
                    improvement = 0 if final_val == 0 else 100
                metrics_improvement[metric_name] = improvement

        # Get AI learning summary
        ai_learning_summary = self.ai_learner.get_learning_summary()

        # Calculate homogeneity improvement
        homogeneity_improvement = self.best_homogeneity - self.initial_homogeneity

        # Set final progress
        self._send_progress('progress', 100)

        # Send final AI status
        self._send_ai_status(f"AI analysis complete. Used {self.ai_recommendations_used} AI recommendations. "
                            f"Homogeneity improvement: {homogeneity_improvement:.4f}")

        return AIPipelineResults(
            success=True,
            initial_state=self.current_state,
            final_state=self.best_state,
            total_operations=self.iteration_count,
            total_cost=self.total_cost_spent,
            total_time=time.time() - self.start_time,
            output_directory=output_dir,
            final_score=self.best_state.score if self.best_state else 0,
            metrics_improvement=metrics_improvement,
            ai_learning_summary=ai_learning_summary,
            ai_recommendations_used=self.ai_recommendations_used,
            homogeneity_improvement=homogeneity_improvement
        )

    def _export_ai_results(self, output_dir: str):
        """Export AI-specific results."""
        # Export AI learning summary
        ai_summary = self.ai_learner.get_learning_summary()
        ai_summary_file = Path(output_dir) / "ai_learning_summary.json"
        with open(ai_summary_file, 'w') as f:
            import json
            json.dump(ai_summary, f, indent=2)

        # Export AI operation predictions
        predictions_summary = {
            'total_recommendations_used': self.ai_recommendations_used,
            'total_ai_improvements': self.ai_improvements,
            'recommendation_success_rate': self.ai_recommendations_used / max(1, self.iteration_count),
            'homogeneity_improvement': self.best_homogeneity - self.initial_homogeneity,
            'ai_learning_progress': ai_summary['learning_progress']
        }
        predictions_file = Path(output_dir) / "ai_predictions_summary.json"
        with open(predictions_file, 'w') as f:
            json.dump(predictions_summary, f, indent=2)

        self._send_progress('terminal', f'AI results exported to {output_dir}', 'info')

    def _send_periodic_update(self):
        """Send periodic performance updates including AI status."""
        current_time = time.time()
        if current_time - self.last_update_time >= 0.5:  # Update every 500ms
            # Send performance metrics
            memory_mb = self.process.memory_info().rss / 1024 / 1024
            self._send_progress('memory', f'{memory_mb:.1f}')

            # Calculate operations per second
            elapsed_time = current_time - self.start_time
            if elapsed_time > 0:
                ops_per_sec = self.iteration_count / elapsed_time
                self._send_progress('performance', {
                    'ops_per_sec': ops_per_sec,
                    'memory_mb': memory_mb,
                    'elapsed_seconds': elapsed_time,
                    'ai_recommendations_used': self.ai_recommendations_used,
                    'ai_improvements': self.ai_improvements
                })

            self.last_update_time = current_time

    def _should_terminate(self) -> bool:
        """Check if termination criteria are met."""
        # Check maximum operations
        if self.iteration_count >= self.args.max_operations:
            self._send_progress('terminal', 'Maximum operations reached', 'info')
            return True

        # Check maximum cost
        if self.total_cost_spent >= self.args.max_cost:
            self._send_progress('terminal', 'Maximum cost reached', 'info')
            return True

        # Check for convergence (no improvement for N iterations)
        if self.no_improvement_count >= 50:  # Configurable
            self._send_progress('terminal', 'No improvement for 50 iterations, terminating', 'info')
            return True

        # Check strategy convergence
        if self.strategy.is_converged():
            self._send_progress('terminal', 'Strategy reports convergence', 'info')
            return True

        return False

    def _check_budget_constraints(self, cost: float) -> bool:
        """Check if applying an operation would exceed budget constraints."""
        return (self.total_cost_spent + cost <= self.args.max_cost and
                self.iteration_count < self.args.max_operations)

    def _load_yaml_config(self, config_path: str) -> Dict:
        """Load YAML configuration file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path, 'r') as f:
            config = yaml.safe_load(f)

        validate_config_file(config)
        return config

    def _load_strategy_config(self, strategy_name: str) -> Dict:
        """Load strategy-specific configuration."""
        config_path = f"config/strategies/strategy_{strategy_name}.yaml"
        return self._load_yaml_config(config_path)

    def _create_strategy(self, strategy_name: str) -> BaseStrategy:
        """Create strategy instance based on name."""
        strategy_map = {
            'greedy': GreedyStrategy,
            # Note: In a full implementation, we'd include other strategies
        }

        if strategy_name not in strategy_map:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        strategy_class = strategy_map[strategy_name]
        return strategy_class(self.strategy_config)

    def _parse_allowed_operations(self, allowed_ops: Optional[str]) -> Optional[Set[str]]:
        """Parse allowed operations from CLI argument."""
        if allowed_ops is None:
            return None

        return set(op.strip() for op in allowed_ops.split(','))

    def _parse_target_metrics(self, target_metrics: str) -> Dict[str, str]:
        """Parse target metrics with optimization directions."""
        targets = {}
        for metric_spec in target_metrics.split(','):
            metric_spec = metric_spec.strip()
            if '=' in metric_spec:
                metric_name, direction = metric_spec.split('=', 1)
                targets[metric_name.strip()] = direction.strip()
        return targets

    def _parse_metrics(self, metrics: str) -> List[str]:
        """Parse metrics list from CLI argument."""
        if metrics.lower() == 'all':
            return self.metrics_registry.list_all_metrics()

        return [metric.strip() for metric in metrics.split(',')]

    def _apply_constraints(self) -> None:
        """Apply user constraints to registries."""
        # Filter operations if allowed operations specified
        if self.allowed_operations is not None:
            self.operations_registry.filter_operations(self.allowed_operations)

        # Apply operation limit if specified
        if self.args.operation_limit is not None:
            self.operations_registry.limit_operations(self.args.operation_limit)

    def _log_metrics_summary(self, metrics: Dict[str, float], label: str) -> None:
        """Log a summary of key metrics."""
        key_metrics = ['file_ideality_score', 'entropy_global', 'lz77_ratio']
        summary_parts = [f"{label} metrics:"]

        for metric in key_metrics:
            if metric in metrics:
                summary_parts.append(f"{metric}={metrics[metric]:.4f}")

        self._send_progress('terminal', " | ".join(summary_parts), 'info')