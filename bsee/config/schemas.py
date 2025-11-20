"""
Configuration schemas for BSEE engine.
Defines Pydantic models for configuration validation.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class LogLevel(str, Enum):
    """Supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StrategyType(str, Enum):
    """Supported strategy types."""
    MCTS = "mcts"
    GENETIC = "genetic"
    BEAM = "beam"
    RANDOM = "random"
    NEURAL = "neural"


class CacheBackend(str, Enum):
    """Supported cache backends."""
    REDIS = "redis"
    MEMORY = "memory"
    FILE = "file"


class DatabaseBackend(str, Enum):
    """Supported database backends."""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"


class MCTSConfig(BaseModel):
    """Monte Carlo Tree Search configuration."""
    exploration_weight: float = Field(default=1.414, ge=0.0, le=10.0)
    max_iterations: int = Field(default=1000, ge=1, le=100000)
    simulation_depth: int = Field(default=10, ge=1, le=1000)
    rollout_strategy: str = Field(default="random", pattern="^(random|greedy|epsilon_greedy)$")
    ucb_constant: float = Field(default=1.414, ge=0.0, le=10.0)


class GeneticConfig(BaseModel):
    """Genetic Algorithm configuration."""
    population_size: int = Field(default=100, ge=10, le=10000)
    mutation_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    crossover_rate: float = Field(default=0.7, ge=0.0, le=1.0)
    elitism_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    max_generations: int = Field(default=100, ge=1, le=10000)
    selection_strategy: str = Field(default="tournament", pattern="^(tournament|roulette|rank)$")
    crossover_strategy: str = Field(default="single_point", pattern="^(single_point|two_point|uniform)$")


class BeamConfig(BaseModel):
    """Beam Search configuration."""
    beam_width: int = Field(default=10, ge=1, le=1000)
    max_depth: int = Field(default=50, ge=1, le=1000)
    pruning_strategy: str = Field(default="threshold", pattern="^(threshold|top_k|diversity)$")
    diversity_weight: float = Field(default=0.1, ge=0.0, le=1.0)


class StrategyConfig(BaseModel):
    """Strategy configuration."""
    default: StrategyType = Field(default=StrategyType.MCTS)
    mcts: Optional[MCTSConfig] = None
    genetic: Optional[GeneticConfig] = None
    beam: Optional[BeamConfig] = None

    class Config:
        use_enum_values = True


class CacheConfig(BaseModel):
    """Cache configuration."""
    enabled: bool = True
    backend: CacheBackend = Field(default=CacheBackend.MEMORY)
    ttl_seconds: int = Field(default=3600, ge=1, le=86400)
    max_size_mb: int = Field(default=1000, ge=1, le=100000)
    redis_url: Optional[str] = None
    redis_db: int = Field(default=0, ge=0, le=15)
    redis_password: Optional[str] = None
    file_cache_path: Optional[str] = None


class DatabaseConfig(BaseModel):
    """Database configuration."""
    enabled: bool = False
    backend: DatabaseBackend = Field(default=DatabaseBackend.SQLITE)
    host: Optional[str] = None
    port: Optional[int] = Field(default=None, ge=1, le=65535)
    database: str = Field(default="bsee")
    username: Optional[str] = None
    password: Optional[str] = None
    ssl_mode: str = Field(default="prefer", regex="^(disable|allow|prefer|require)$")
    pool_size: int = Field(default=5, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=100)
    sqlite_path: Optional[str] = None

    @validator('port')
    def validate_port_for_backend(cls, v, values):
        if v and 'backend' in values:
            if values['backend'] == DatabaseBackend.SQLITE:
                raise ValueError("SQLite doesn't use port")
        return v

    @validator('host', 'username', 'password')
    def validate_required_for_non_sqlite(cls, v, values, field):
        if values.get('backend') != DatabaseBackend.SQLITE and not v:
            raise ValueError(f"{field.name} is required for {values.get('backend')}")
        return v


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""
    enabled: bool = True
    metrics_port: int = Field(default=8080, ge=1024, le=65535)
    log_level: LogLevel = Field(default=LogLevel.INFO)
    metrics_retention_hours: int = Field(default=24, ge=1, le=8760)
    alert_thresholds: Dict[str, Union[float, str]] = Field(default_factory=dict)
    prometheus_enabled: bool = False
    prometheus_port: int = Field(default=9090, ge=1024, le=65535)
    dashboard_enabled: bool = True
    dashboard_port: int = Field(default=3000, ge=1024, le=65535)


class APIConfig(BaseModel):
    """API configuration."""
    enabled: bool = True
    host: str = Field(default="0.0.0.0", regex=r"^[\d\.]+$|^localhost$|^[\w\.-]+$")
    port: int = Field(default=8000, ge=1024, le=65535)
    workers: int = Field(default=1, ge=1, le=100)
    reload: bool = False
    log_level: LogLevel = Field(default=LogLevel.INFO)
    rate_limit: str = Field(default="100/hour", regex=r"^[\d]+/(second|minute|hour|day)$")
    max_file_size: str = Field(default="100MB", regex=r"^[\d]+[KMGT]?B$")
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    cors_origins: List[str] = Field(default_factory=list)
    api_key_required: bool = False
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"])


class SecurityConfig(BaseModel):
    """Security configuration."""
    api_key: Optional[str] = None
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = Field(default="HS256", regex=r"^(HS|RS)\d+$")
    jwt_expiration_hours: int = Field(default=24, ge=1, le=8760)
    bcrypt_rounds: int = Field(default=12, ge=4, le=31)
    max_login_attempts: int = Field(default=5, ge=1, le=100)
    lockout_duration_minutes: int = Field(default=15, ge=1, le=1440)


class EngineConfig(BaseModel):
    """Main engine configuration."""
    max_iterations: int = Field(default=1000, ge=1, le=100000)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    parallel_processing: bool = True
    max_workers: int = Field(default=4, ge=1, le=100)
    memory_limit_mb: int = Field(default=2048, ge=128, le=32768)
    temp_directory: str = Field(default="/tmp/bsee")
    log_format: str = Field(default="json", regex="^(json|text|structured)$")

    @validator('temp_directory')
    def validate_temp_directory(cls, v):
        import os
        if not os.path.exists(v):
            try:
                os.makedirs(v, exist_ok=True)
            except PermissionError:
                raise ValueError(f"Cannot create temp directory: {v}")
        return v


class BSEEConfig(BaseModel):
    """Complete BSEE configuration."""
    engine: EngineConfig = Field(default_factory=EngineConfig)
    strategies: StrategyConfig = Field(default_factory=StrategyConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    class Config:
        extra = "allow"  # Allow extra fields for future expansion