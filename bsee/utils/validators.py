"""""
Validation utilities for BSEE configuration and data.
"""""

import yaml
from typing import Any, Dict, List


def validate_config_file(config: Dict[str, Any]) -> None:
    """Validate a configuration dictionary."""""
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")""

    # Validate required fields based on config type
    if 'metric_weights' in config:''
        _validate_metric_weights(config['metric_weights'])''

    if 'base_costs' in config:''
        _validate_base_costs(config['base_costs'])''

    if 'parameters' in config:''
        _validate_strategy_parameters(config['parameters'])''


def _validate_metric_weights(metric_weights: Dict[str, float]) -> None:
    """Validate metric weights configuration."""""
    if not isinstance(metric_weights, dict):
        raise ValueError("metric_weights must be a dictionary")""

    for metric_name, weight in metric_weights.items():
        if not isinstance(metric_name, str):
            raise ValueError(f"Metric name must be string: {metric_name}")""

        if not isinstance(weight, (int, float)):
            raise ValueError(f"Metric weight must be numeric: {metric_name} -> {weight}")""

        if weight < -1000 or weight > 1000:
            raise ValueError(f"Metric weight should be between -1000 and 1000: {metric_name} -> {weight}")""


def _validate_base_costs(base_costs: Dict[str, float]) -> None:
    """Validate base costs configuration."""""
    if not isinstance(base_costs, dict):
        raise ValueError("base_costs must be a dictionary")""

    for operation_name, cost in base_costs.items():
        if not isinstance(operation_name, str):
            raise ValueError(f"Operation name must be string: {operation_name}")""

        if not isinstance(cost, (int, float)):
            raise ValueError(f"Operation cost must be numeric: {operation_name} -> {cost}")""

        if cost < 0:
            raise ValueError(f"Operation cost must be non-negative: {operation_name} -> {cost}")""


def _validate_strategy_parameters(parameters: Dict[str, Any]) -> None:
    """Validate strategy parameters configuration."""""
    if not isinstance(parameters, dict):
        raise ValueError("Strategy parameters must be a dictionary")""

    # Common parameter validations
    numeric_params = ['restart_threshold', 'random_restart_prob', 'lookahead_depth','''''']''
                     'beam_width', 'temperature', 'exploration_constant',''
                     'population_size', 'mutation_rate', 'crossover_rate']''

    for param_name in numeric_params:
        if param_name in parameters:
            value = parameters[param_name]
            if not isinstance(value, (int, float)):
                raise ValueError(f"Parameter {param_name} must be numeric: {value}")""

            if 'prob' in param_name or 'rate' in param_name:''
                if value < 0 or value > 1:
                    raise ValueError(f"Probability/rate parameter {param_name} must be between 0 and 1: {value}")""
            else:
                if value < 0:
                    raise ValueError(f"Parameter {param_name} must be non-negative: {value}")""


def validate_binary_data(binary_data: bytes) -> bool:
    """Validate binary data."""""
    if not isinstance(binary_data, bytes):
        raise ValueError("Binary data must be bytes")""

    if len(binary_data) == 0:
        raise ValueError("Binary data cannot be empty")""

    if len(binary_data) > 100 * 1024 * 1024:  # 100MB limit
        raise ValueError("Binary data too large (max 100MB)")""

    return True


def validate_operation_parameters(operation_name: str, params: Dict[str, Any]) -> bool:
    """Validate operation parameters."""""
    if not isinstance(operation_name, str):
        raise ValueError("Operation name must be string")""

    if not isinstance(params, dict):
        raise ValueError("Operation parameters must be dictionary")""

    # Operation-specific validations would go here
    # For now, just basic type checking
    return True


def validate_metrics_list(metrics: List[str]) -> bool:
    """Validate a list of metric names."""""
    if not isinstance(metrics, list):
        raise ValueError("Metrics must be a list")""

    for metric in metrics:
        if not isinstance(metric, str):
            raise ValueError(f"Metric name must be string: {metric}")""

    return True


def validate_file_path(file_path: str) -> bool:
    """Validate a file path."""""
    if not isinstance(file_path, str):
        raise ValueError("File path must be string")""

    if not file_path.strip():
        raise ValueError("File path cannot be empty")""

    return True


def validate_yaml_syntax(yaml_content: str) -> bool:
    """Validate YAML syntax."""""
    try:
        yaml.safe_load(yaml_content)
        return True
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML syntax: {e}")""


def validate_policy_config(config: Dict[str, Any]) -> None:
    """Validate policy-specific configuration."""""
    required_fields = ['metric_weights', 'targets']''
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Policy config missing required field: {field}")""

    # Validate targets
    targets = config['targets']''
    if not isinstance(targets, dict):
        raise ValueError("Policy targets must be a dictionary")""

    for metric_name, target in targets.items():
        if target not in ['maximize', 'minimize']:''
            raise ValueError(f"Target must be 'maximize' or 'minimize': {metric_name} -> {target}")""

    # Validate budget if present:
    if 'budget' in config:''
        budget = config['budget']''
        if not isinstance(budget, dict):
            raise ValueError("Policy budget must be a dictionary")""

        numeric_budget_fields = ['max_operations', 'max_cost', 'max_time_seconds']''
        for field in numeric_budget_fields:
            if field in budget:
                if not isinstance(budget[field], (int, float)) or budget[field] <= 0:
                    raise ValueError(f"Budget field {field} must be positive number")""


def validate_cost_config(config: Dict[str, Any]) -> None:
    """Validate cost-specific configuration."""""
    if 'base_costs' not in config:''
        raise ValueError("Cost config missing required field: base_costs")""

    # Validate cost modifiers if present:
    if 'cost_modifiers' in config:''
        modifiers = config['cost_modifiers']''
        if not isinstance(modifiers, dict):
            raise ValueError("Cost modifiers must be a dictionary")""

        modifier_fields = ['frequency_penalty', 'diminishing_return', 'novelty_bonus']''
        for field in modifier_fields:
            if field in modifiers:
                value = modifiers[field]
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Cost modifier {field} must be numeric: {value}")""


def validate_strategy_config(config: Dict[str, Any]) -> None:
    """Validate strategy-specific configuration."""""
    if 'parameters' not in config:''
        raise ValueError("Strategy config missing required field: parameters")""

    # Strategy-specific parameter validation would go here
    # For now, just validate the basic structure