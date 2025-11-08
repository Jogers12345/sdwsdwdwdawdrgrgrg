"""
Configuration manager for BSEE engine.
Handles loading, validation, and management of configuration.
"""

import os
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
from contextlib import contextmanager

from .validator import ConfigValidator, ConfigError
from .schemas import BSEEConfig


class ConfigManager:
    """Manages BSEE configuration with hot-reload support."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file
        """
        self._validator = ConfigValidator()
        self._config_path: Optional[Path] = None
        self._config: Optional[BSEEConfig] = None
        self._logger = logging.getLogger(__name__)

        if config_path:
            self.load_config(config_path)
        else:
            self._load_default_config()

    def load_config(self, config_path: Union[str, Path]) -> BSEEConfig:
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            Loaded and validated configuration

        Raises:
            ConfigError: If configuration is invalid
        """
        config_path = Path(config_path)
        self._config_path = config_path

        try:
            self._config = self._validator.validate_config(config_path)
            self._logger.info(f"Configuration loaded from {config_path}")
            return self._config

        except ConfigError as e:
            self._logger.error(f"Failed to load configuration: {e}")
            raise

    def load_config_from_dict(self, config_dict: Dict[str, Any]) -> BSEEConfig:
        """
        Load configuration from dictionary.

        Args:
            config_dict: Configuration dictionary

        Returns:
            Loaded and validated configuration
        """
        try:
            self._config = self._validator.validate_config(config_dict)
            self._logger.info("Configuration loaded from dictionary")
            return self._config

        except ConfigError as e:
            self._logger.error(f"Failed to load configuration: {e}")
            raise

    def _load_default_config(self) -> BSEEConfig:
        """Load default configuration."""
        self._config = BSEEConfig()
        self._logger.info("Loaded default configuration")
        return self._config

    def get_config(self) -> BSEEConfig:
        """
        Get current configuration.

        Returns:
            Current configuration instance

        Raises:
            RuntimeError: If no configuration is loaded
        """
        if self._config is None:
            raise RuntimeError("No configuration loaded")
        return self._config

    def reload_config(self) -> BSEEConfig:
        """
        Reload configuration from file.

        Returns:
            Reloaded configuration

        Raises:
            RuntimeError: If no configuration file is set
            ConfigError: If configuration is invalid
        """
        if self._config_path is None:
            raise RuntimeError("No configuration file path set")

        return self.load_config(self._config_path)

    def save_config(self, output_path: Union[str, Path], format: str = "yaml") -> None:
        """
        Save current configuration to file.

        Args:
            output_path: Output file path
            format: Output format ("yaml" or "json")
        """
        if self._config is None:
            raise RuntimeError("No configuration to save")

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        config_dict = self._config.dict()

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if format.lower() == "yaml":
                    import yaml
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                elif format.lower() == "json":
                    import json
                    json.dump(config_dict, f, indent=2)
                else:
                    raise ValueError(f"Unsupported format: {format}")

            self._logger.info(f"Configuration saved to {output_path}")

        except Exception as e:
            self._logger.error(f"Failed to save configuration: {e}")
            raise

    def update_config(self, updates: Dict[str, Any]) -> BSEEConfig:
        """
        Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates

        Returns:
            Updated configuration

        Raises:
            ConfigError: If updates are invalid
        """
        if self._config is None:
            raise RuntimeError("No configuration loaded")

        # Merge updates with current config
        current_dict = self._config.dict()
        merged_dict = self._deep_merge(current_dict, updates)

        # Validate merged configuration
        try:
            self._config = self._validator.validate_config(merged_dict)
            self._logger.info("Configuration updated successfully")
            return self._config

        except ConfigError as e:
            self._logger.error(f"Failed to update configuration: {e}")
            raise

    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_env_overrides(self) -> Dict[str, Any]:
        """
        Get configuration overrides from environment variables.

        Returns:
            Dictionary of environment variable overrides
        """
        overrides = {}
        env_prefix = "BSEE_"

        for key, value in os.environ.items():
            if key.startswith(env_prefix):
                config_key = key[len(env_prefix):].lower()
                config_path = config_key.split('_')

                # Convert value to appropriate type
                converted_value = self._convert_env_value(value)

                # Build nested dictionary
                current = overrides
                for part in config_path[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[config_path[-1]] = converted_value

        return overrides

    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable value to appropriate type."""
        # Boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False

        # Integer values
        try:
            return int(value)
        except ValueError:
            pass

        # Float values
        try:
            return float(value)
        except ValueError:
            pass

        # String value
        return value

    def apply_env_overrides(self) -> BSEEConfig:
        """
        Apply environment variable overrides to current configuration.

        Returns:
            Configuration with overrides applied
        """
        overrides = self.get_env_overrides()
        if overrides:
            return self.update_config(overrides)
        return self.get_config()

    def validate_current_config(self) -> Dict[str, Any]:
        """
        Validate current configuration and return summary.

        Returns:
            Validation summary
        """
        if self._config is None:
            return {
                "valid": False,
                "error": "No configuration loaded"
            }

        if self._config_path:
            return self._validator.get_validation_summary(self._config_path)
        else:
            return {
                "valid": True,
                "source": "default",
                "warnings": self._validator._get_warnings(self._config),
                "recommendations": self._validator._get_recommendations(self._config)
            }

    @contextmanager
    def temporary_config(self, temp_config: Dict[str, Any]):
        """
        Context manager for temporary configuration changes.

        Args:
            temp_config: Temporary configuration overrides
        """
        original_config = self._config
        try:
            self.update_config(temp_config)
            yield self._config
        finally:
            self._config = original_config

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get summary of current configuration.

        Returns:
            Configuration summary
        """
        if self._config is None:
            return {"error": "No configuration loaded"}

        return {
            "source": str(self._config_path) if self._config_path else "default",
            "engine": {
                "max_iterations": self._config.engine.max_iterations,
                "timeout_seconds": self._config.engine.timeout_seconds,
                "parallel_processing": self._config.engine.parallel_processing,
                "max_workers": self._config.engine.max_workers,
            },
            "strategies": {
                "default": self._config.strategies.default,
                "mcts": self._config.strategies.mcts is not None,
                "genetic": self._config.strategies.genetic is not None,
                "beam": self._config.strategies.beam is not None,
            },
            "cache": {
                "enabled": self._config.cache.enabled,
                "backend": self._config.cache.backend,
            },
            "api": {
                "enabled": self._config.api.enabled,
                "host": self._config.api.host,
                "port": self._config.api.port,
            },
            "monitoring": {
                "enabled": self._config.monitoring.enabled,
                "metrics_port": self._config.monitoring.metrics_port,
            }
        }

    def export_config_template(self, output_path: Union[str, Path], format: str = "yaml") -> None:
        """
        Export configuration template with documentation.

        Args:
            output_path: Output file path
            format: Output format ("yaml" or "json")
        """
        # Create a sample configuration with comments
        template_config = {
            "engine": {
                "max_iterations": 1000,
                "timeout_seconds": 300,
                "parallel_processing": True,
                "max_workers": 4,
                "memory_limit_mb": 2048,
                "temp_directory": "/tmp/bsee",
                "log_format": "json"
            },
            "strategies": {
                "default": "mcts",
                "mcts": {
                    "exploration_weight": 1.414,
                    "max_iterations": 1000,
                    "simulation_depth": 10
                },
                "genetic": {
                    "population_size": 100,
                    "mutation_rate": 0.1,
                    "crossover_rate": 0.7
                }
            },
            "cache": {
                "enabled": True,
                "backend": "memory",
                "ttl_seconds": 3600,
                "max_size_mb": 1000
            },
            "database": {
                "enabled": False,
                "backend": "sqlite",
                "sqlite_path": "bsee.db"
            },
            "monitoring": {
                "enabled": True,
                "metrics_port": 8080,
                "log_level": "INFO"
            },
            "api": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 1,
                "rate_limit": "100/hour"
            }
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if format.lower() == "yaml":
                    import yaml
                    yaml.dump(template_config, f, default_flow_style=False, indent=2)

                    # Add header comment
                    content = f.read() if 'f' in locals() else ''
                    with open(output_path, 'r') as read_file:
                        content = read_file.read()

                    with open(output_path, 'w') as write_file:
                        write_file.write(
                            "# BSEE Configuration Template\n"
                            "# Copy this file and modify values as needed\n"
                            "# See documentation for detailed explanations\n\n"
                        )
                        write_file.write(content)

                elif format.lower() == "json":
                    import json
                    json.dump(template_config, f, indent=2)

            self._logger.info(f"Configuration template exported to {output_path}")

        except Exception as e:
            self._logger.error(f"Failed to export template: {e}")
            raise


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def load_config(config_path: Union[str, Path]) -> BSEEConfig:
    """Load configuration using global manager."""
    return get_config_manager().load_config(config_path)


def get_config() -> BSEEConfig:
    """Get current configuration using global manager."""
    return get_config_manager().get_config()