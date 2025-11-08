"""
Configuration validator for BSEE engine.
Validates configuration files and provides detailed error messages.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from pydantic import ValidationError

from .schemas import BSEEConfig, ConfigError


class ConfigValidator:
    """Validates BSEE configuration files."""

    def __init__(self):
        self._config_schema = BSEEConfig

    def validate_config(self, config_data: Union[Dict[str, Any], str, Path]) -> BSEEConfig:
        """
        Validate configuration data and return a BSEEConfig instance.

        Args:
            config_data: Configuration as dict, file path, or Path object

        Returns:
            Validated BSEEConfig instance

        Raises:
            ConfigError: If validation fails
        """
        try:
            # Load config if it's a file path
            if isinstance(config_data, (str, Path)):
                config_dict = self._load_config_file(config_data)
            else:
                config_dict = config_data

            # Validate and create config instance
            config = self._config_schema(**config_dict)

            # Perform additional validation
            self._validate_additional_constraints(config)

            return config

        except ValidationError as e:
            raise ConfigError(f"Configuration validation failed: {e}") from e
        except Exception as e:
            raise ConfigError(f"Failed to validate configuration: {e}") from e

    def _load_config_file(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load configuration from file."""
        config_path = Path(config_path)

        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        if not config_path.is_file():
            raise ConfigError(f"Configuration path is not a file: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    raise ConfigError(f"Unsupported config file format: {config_path.suffix}")

        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file {config_path}: {e}") from e
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file {config_path}: {e}") from e
        except Exception as e:
            raise ConfigError(f"Failed to read config file {config_path}: {e}") from e

    def _validate_additional_constraints(self, config: BSEEConfig) -> None:
        """Perform additional validation beyond Pydantic schema."""
        # Validate port conflicts
        ports_used = []
        if config.api.enabled:
            ports_used.append(config.api.port)
        if config.monitoring.enabled:
            ports_used.append(config.monitoring.metrics_port)
            if config.monitoring.prometheus_enabled:
                ports_used.append(config.monitoring.prometheus_port)
            if config.monitoring.dashboard_enabled:
                ports_used.append(config.monitoring.dashboard_port)

        if len(ports_used) != len(set(ports_used)):
            raise ConfigError(f"Port conflicts detected: {ports_used}")

        # Validate database configuration consistency
        if config.database.enabled:
            if config.database.backend == "sqlite":
                if not config.database.sqlite_path:
                    raise ConfigError("SQLite backend requires sqlite_path")
            else:
                if not all([config.database.host, config.database.username, config.database.password]):
                    raise ConfigError(f"{config.database.backend} backend requires host, username, and password")

        # Validate cache configuration consistency
        if config.cache.enabled and config.cache.backend == "redis":
            if not config.cache.redis_url and not config.cache.host:
                raise ConfigError("Redis cache backend requires redis_url or host")

        # Validate security configuration
        if config.security.api_key_required and not config.security.api_key:
            raise ConfigError("API key authentication is enabled but no API key is configured")

        # Validate directory permissions
        self._validate_directory_permissions(config)

        # Validate resource limits
        self._validate_resource_limits(config)

    def _validate_directory_permissions(self, config: BSEEConfig) -> None:
        """Validate directory permissions and existence."""
        directories_to_check = [
            config.engine.temp_directory,
        ]

        if config.cache.backend == "file" and config.cache.file_cache_path:
            cache_dir = Path(config.cache.file_cache_path).parent
            directories_to_check.append(str(cache_dir))

        if config.database.backend == "sqlite" and config.database.sqlite_path:
            db_dir = Path(config.database.sqlite_path).parent
            directories_to_check.append(str(db_dir))

        for directory in directories_to_check:
            try:
                dir_path = Path(directory)
                dir_path.mkdir(parents=True, exist_ok=True)

                # Test write permissions
                test_file = dir_path / ".bsee_write_test"
                test_file.touch()
                test_file.unlink()

            except (PermissionError, OSError) as e:
                raise ConfigError(f"Cannot write to directory {directory}: {e}")

    def _validate_resource_limits(self, config: BSEEConfig) -> None:
        """Validate resource limits are reasonable."""
        # Memory limits
        if config.engine.memory_limit_mb < 512:
            raise ConfigError("Memory limit should be at least 512MB for optimal performance")

        if config.cache.max_size_mb > config.engine.memory_limit_mb * 0.8:
            raise ConfigError("Cache size should not exceed 80% of memory limit")

        # Timeout limits
        if config.engine.timeout_seconds > 3600:
            raise ConfigError("Timeout should not exceed 1 hour for interactive use")

        # Worker limits
        if config.engine.max_workers > 100:
            raise ConfigError("Maximum workers should not exceed 100")

        # Rate limiting
        if config.api.rate_limit:
            try:
                rate_value, rate_unit = config.api.rate_limit.split('/')
                rate_value = int(rate_value)

                if rate_unit == "second" and rate_value > 1000:
                    raise ConfigError("Rate limit per second should not exceed 1000")
                elif rate_unit == "minute" and rate_value > 60000:
                    raise ConfigError("Rate limit per minute should not exceed 60000")

            except (ValueError, IndexError):
                raise ConfigError(f"Invalid rate limit format: {config.api.rate_limit}")

    def validate_operation_config(self, operation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation-specific configuration."""
        required_fields = ['name', 'type']
        for field in required_fields:
            if field not in operation_config:
                raise ConfigError(f"Operation config missing required field: {field}")

        # Validate operation type
        valid_types = [
            'transform', 'bitwise', 'compression', 'encoding',
            'encryption', 'custom', 'neural', 'plugin'
        ]
        if operation_config['type'] not in valid_types:
            raise ConfigError(f"Invalid operation type: {operation_config['type']}")

        return operation_config

    def validate_pipeline_config(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pipeline configuration."""
        required_fields = ['name', 'operations']
        for field in required_fields:
            if field not in pipeline_config:
                raise ConfigError(f"Pipeline config missing required field: {field}")

        if not isinstance(pipeline_config['operations'], list):
            raise ConfigError("Pipeline operations must be a list")

        if len(pipeline_config['operations']) == 0:
            raise ConfigError("Pipeline must have at least one operation")

        # Validate each operation in the pipeline
        for i, op_config in enumerate(pipeline_config['operations']):
            try:
                self.validate_operation_config(op_config)
            except ConfigError as e:
                raise ConfigError(f"Invalid operation at index {i}: {e}") from e

        return pipeline_config

    def get_validation_summary(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get a detailed validation summary for a configuration file.

        Returns:
            Dictionary with validation results and warnings
        """
        try:
            config = self.validate_config(config_path)

            return {
                "valid": True,
                "config_file": str(config_path),
                "summary": {
                    "engine": {
                        "max_iterations": config.engine.max_iterations,
                        "timeout_seconds": config.engine.timeout_seconds,
                        "parallel_processing": config.engine.parallel_processing,
                        "max_workers": config.engine.max_workers,
                        "memory_limit_mb": config.engine.memory_limit_mb,
                    },
                    "strategies": {
                        "default": config.strategies.default,
                        "mcts_configured": config.strategies.mcts is not None,
                        "genetic_configured": config.strategies.genetic is not None,
                        "beam_configured": config.strategies.beam is not None,
                    },
                    "cache": {
                        "enabled": config.cache.enabled,
                        "backend": config.cache.backend,
                        "ttl_seconds": config.cache.ttl_seconds,
                        "max_size_mb": config.cache.max_size_mb,
                    },
                    "database": {
                        "enabled": config.database.enabled,
                        "backend": config.database.backend,
                    },
                    "monitoring": {
                        "enabled": config.monitoring.enabled,
                        "metrics_port": config.monitoring.metrics_port,
                        "log_level": config.monitoring.log_level,
                    },
                    "api": {
                        "enabled": config.api.enabled,
                        "host": config.api.host,
                        "port": config.api.port,
                        "workers": config.api.workers,
                    }
                },
                "warnings": self._get_warnings(config),
                "recommendations": self._get_recommendations(config)
            }

        except ConfigError as e:
            return {
                "valid": False,
                "config_file": str(config_path),
                "error": str(e),
                "suggestions": self._get_error_suggestions(str(e))
            }

    def _get_warnings(self, config: BSEEConfig) -> List[str]:
        """Get configuration warnings."""
        warnings = []

        if config.engine.memory_limit_mb < 1024:
            warnings.append("Memory limit is low, consider increasing for better performance")

        if config.engine.max_workers > os.cpu_count():
            warnings.append(f"Max workers ({config.engine.max_workers}) exceeds CPU count ({os.cpu_count()})")

        if config.cache.enabled and config.cache.max_size_mb > config.engine.memory_limit_mb * 0.5:
            warnings.append("Cache size is large relative to memory limit")

        if config.api.enabled and config.api.host == "0.0.0.0":
            warnings.append("API bound to all interfaces, consider security implications")

        if config.monitoring.enabled and not config.monitoring.prometheus_enabled:
            warnings.append("Prometheus metrics disabled, consider enabling for better monitoring")

        if not config.security.api_key_required and config.api.enabled:
            warnings.append("API is not secured with authentication")

        return warnings

    def _get_recommendations(self, config: BSEEConfig) -> List[str]:
        """Get configuration recommendations."""
        recommendations = []

        if not config.database.enabled:
            recommendations.append("Enable database for persistent storage of results")

        if not config.cache.enabled:
            recommendations.append("Enable caching to improve performance")

        if config.engine.parallel_processing and config.engine.max_workers < 4:
            recommendations.append("Consider increasing workers for better parallel processing")

        if config.strategies.default == "mcts" and not config.strategies.mcts:
            recommendations.append("Configure MCTS strategy parameters for better performance")

        if config.monitoring.log_level == "DEBUG":
            recommendations.append("Consider using INFO log level for production")

        return recommendations

    def _get_error_suggestions(self, error_message: str) -> List[str]:
        """Get suggestions based on error message."""
        suggestions = []

        if "not found" in error_message.lower():
            suggestions.append("Check that the configuration file path is correct")
            suggestions.append("Ensure the configuration file exists and is readable")

        if "port conflicts" in error_message.lower():
            suggestions.append("Check for other services using the same ports")
            suggestions.append("Modify port numbers in configuration")

        if "permission" in error_message.lower():
            suggestions.append("Check directory permissions")
            suggestions.append("Ensure the application can read/write to required directories")

        if "validation failed" in error_message.lower():
            suggestions.append("Review configuration values against schema requirements")
            suggestions.append("Check data types and value ranges")

        return suggestions