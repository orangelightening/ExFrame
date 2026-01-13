"""
Configuration management for Autonomous Learning System.

Loads and validates configuration from YAML files with:
- Default configuration
- Environment-specific overrides
- Validation of required fields
- Type-safe access to config values
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

import yaml


class SurveyLevel(str, Enum):
    """Survey hierarchy levels."""
    DOMAIN = "domain"
    NEIGHBOURHOOD = "neighbourhood"
    UNIVERSE = "universe"


class SurveyStatus(str, Enum):
    """Survey status values."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SupervisorConfig:
    """AI Supervisor configuration."""
    api_url: str = None
    model: str = "glm-4"
    max_tokens: int = 4096
    temperature: float = 0.7
    heartbeat_interval: int = 30
    heartbeat_timeout: int = 10
    max_missed_heartbeats: int = 3
    focus_window_size: int = 10
    focus_drift_threshold: float = 0.3
    focus_repetition_threshold: float = 0.95

    def __post_init__(self):
        if self.api_url is None:
            self.api_url = os.getenv("LLM_API_ENDPOINT", "https://api.z.ai/api/coding/paas/v4/chat/completions")


@dataclass
class JudgeConfig:
    """Individual judge configuration."""
    name: str
    role: str
    api_url: str
    model: str
    temperature: float
    weight: float = 1.0
    is_human: bool = False


@dataclass
class CertificationConfig:
    """Certification panel configuration."""
    judges: List[JudgeConfig] = field(default_factory=list)
    certified_threshold: float = 0.8
    provisional_threshold: float = 0.6
    unanimous_bonus: float = 0.1
    skeptic_veto_critical: bool = True

    def __post_init__(self):
        # Set default judges if none provided
        if not self.judges:
            api_url = os.getenv("LLM_API_ENDPOINT", "https://api.z.ai/api/coding/paas/v4/chat/completions")
            self.judges = [
                JudgeConfig(
                    name="generalist",
                    role="structure_review",
                    api_url=api_url,
                    model="glm-4",
                    temperature=0.3,
                    weight=1.0
                ),
                JudgeConfig(
                    name="specialist",
                    role="domain_accuracy",
                    api_url=api_url,
                    model="glm-4",
                    temperature=0.2,
                    weight=1.0
                ),
                JudgeConfig(
                    name="skeptic",
                    role="critical_analysis",
                    api_url=api_url,
                    model="glm-4",
                    temperature=0.5,
                    weight=1.5  # Higher weight for critical issues
                ),
                JudgeConfig(
                    name="contextualist",
                    role="context_fit",
                    api_url=api_url,
                    model="glm-4",
                    temperature=0.4,
                    weight=1.0
                ),
                JudgeConfig(
                    name="human",
                    role="last_resort",
                    api_url="",
                    model="",
                    temperature=0.0,
                    weight=1.0,
                    is_human=True
                ),
            ]


@dataclass
class ScrapingConfig:
    """Scraping engine configuration."""
    requests_per_second: int = 1
    burst: int = 5
    exponential_backoff: bool = True
    max_retries: int = 3
    skip_404: bool = True
    backoff_429: bool = True
    enable_stealth: bool = True
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    ])
    jitter_percent: int = 20
    warm_up_requests: int = 3
    pilot_domain: str = "cooking"


@dataclass
class IngestionConfig:
    """Pattern ingestion configuration."""
    strict_mode: bool = True
    required_fields: List[str] = field(default_factory=lambda: ["name", "description", "problem", "solution", "steps"])
    similarity_threshold: float = 0.85
    dedup_method: str = "text_based"  # word_overlap, jaccard
    pattern_directory: str = "data/patterns/{domain}/"
    backup_enabled: bool = True


@dataclass
class ResearchHooksConfig:
    """Research generator hooks configuration."""
    enabled: bool = False
    pattern_storage_field: str = "research_id"


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    log_dir: Optional[str] = None
    json_output: bool = True


@dataclass
class Config:
    """Main configuration class."""

    # Component configs
    supervisor: SupervisorConfig = field(default_factory=SupervisorConfig)
    certification: CertificationConfig = field(default_factory=CertificationConfig)
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    research_hooks: ResearchHooksConfig = field(default_factory=ResearchHooksConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Hierarchy
    universe: str = "default"
    neighbourhood: str = "parksville_bc"
    domain: str = "cooking"

    # Paths
    config_dir: Path = field(default_factory=lambda: Path("config"))
    data_dir: Path = field(default_factory=lambda: Path("data"))

    @classmethod
    def from_yaml(cls, config_path: Path) -> "Config":
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Config instance
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """
        Create Config from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            Config instance
        """
        config = cls()

        # Load supervisor config
        if "supervisor" in data:
            supervisor_data = data["supervisor"]
            config.supervisor = SupervisorConfig(
                api_url=supervisor_data.get("api", {}).get("url", config.supervisor.api_url),
                model=supervisor_data.get("api", {}).get("model", config.supervisor.model),
                max_tokens=supervisor_data.get("api", {}).get("max_tokens", config.supervisor.max_tokens),
                temperature=supervisor_data.get("api", {}).get("temperature", config.supervisor.temperature),
                heartbeat_interval=supervisor_data.get("heartbeat", {}).get("interval", config.supervisor.heartbeat_interval),
                heartbeat_timeout=supervisor_data.get("heartbeat", {}).get("timeout", config.supervisor.heartbeat_timeout),
                max_missed_heartbeats=supervisor_data.get("heartbeat", {}).get("max_missed", config.supervisor.max_missed_heartbeats),
                focus_window_size=supervisor_data.get("focus", {}).get("window_size", config.supervisor.focus_window_size),
                focus_drift_threshold=supervisor_data.get("focus", {}).get("drift_threshold", config.supervisor.focus_drift_threshold),
                focus_repetition_threshold=supervisor_data.get("focus", {}).get("repetition_threshold", config.supervisor.focus_repetition_threshold),
            )

        # Load certification config
        if "certification" in data:
            cert_data = data["certification"]
            judges = []
            for judge_data in cert_data.get("judges", []):
                judges.append(JudgeConfig(
                    name=judge_data.get("name"),
                    role=judge_data.get("role"),
                    api_url=judge_data.get("api_url"),
                    model=judge_data.get("model"),
                    temperature=judge_data.get("temperature"),
                    weight=judge_data.get("weight", 1.0),
                    is_human=judge_data.get("type") == "human",
                ))
            config.certification = CertificationConfig(
                judges=judges,
                certified_threshold=cert_data.get("thresholds", {}).get("certified", 0.8),
                provisional_threshold=cert_data.get("thresholds", {}).get("provisional", 0.6),
                unanimous_bonus=cert_data.get("thresholds", {}).get("unanimous_bonus", 0.1),
                skeptic_veto_critical=cert_data.get("thresholds", {}).get("skeptic_veto_critical", True),
            )

        # Load scraping config
        if "scraping" in data:
            scraping_data = data["scraping"]
            config.scraping = ScrapingConfig(
                requests_per_second=scraping_data.get("rate_limit", {}).get("requests_per_second", 1),
                burst=scraping_data.get("rate_limit", {}).get("burst", 5),
                exponential_backoff=scraping_data.get("rate_limit", {}).get("exponential_backoff", True),
                max_retries=scraping_data.get("error_handling", {}).get("max_retries", 3),
                skip_404=scraping_data.get("error_handling", {}).get("skip_404", True),
                backoff_429=scraping_data.get("error_handling", {}).get("backoff_429", True),
                enable_stealth=scraping_data.get("stealth", {}).get("enable", True),
                user_agents=scraping_data.get("stealth", {}).get("user_agents", config.scraping.user_agents),
                jitter_percent=scraping_data.get("stealth", {}).get("jitter_percent", 20),
                warm_up_requests=scraping_data.get("stealth", {}).get("warm_up_requests", 3),
                pilot_domain=scraping_data.get("pilot_domain", "cooking"),
            )

        # Load ingestion config
        if "ingestion" in data:
            ingestion_data = data["ingestion"]
            config.ingestion = IngestionConfig(
                strict_mode=ingestion_data.get("validation", {}).get("strict_mode", True),
                required_fields=ingestion_data.get("validation", {}).get("required_fields", config.ingestion.required_fields),
                similarity_threshold=ingestion_data.get("deduplication", {}).get("similarity_threshold", 0.85),
                dedup_method=ingestion_data.get("deduplication", {}).get("method", "text_based"),
                pattern_directory=ingestion_data.get("storage", {}).get("pattern_directory", config.ingestion.pattern_directory),
                backup_enabled=ingestion_data.get("storage", {}).get("backup_enabled", True),
            )

        # Load logging config
        if "logging" in data:
            logging_data = data["logging"]
            config.logging = LoggingConfig(
                level=logging_data.get("level", "INFO"),
                log_dir=logging_data.get("log_dir"),
                json_output=logging_data.get("json_output", True),
            )

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "supervisor": {
                "api": {
                    "url": self.supervisor.api_url,
                    "model": self.supervisor.model,
                    "max_tokens": self.supervisor.max_tokens,
                    "temperature": self.supervisor.temperature,
                },
                "heartbeat": {
                    "interval": self.supervisor.heartbeat_interval,
                    "timeout": self.supervisor.heartbeat_timeout,
                    "max_missed": self.supervisor.max_missed_heartbeats,
                },
                "focus": {
                    "window_size": self.supervisor.focus_window_size,
                    "drift_threshold": self.supervisor.focus_drift_threshold,
                    "repetition_threshold": self.supervisor.focus_repetition_threshold,
                },
            },
            "certification": {
                "judges": [
                    {
                        "name": j.name,
                        "role": j.role,
                        "api_url": j.api_url,
                        "model": j.model,
                        "temperature": j.temperature,
                        "weight": j.weight,
                        "type": "human" if j.is_human else "ai",
                    }
                    for j in self.certification.judges
                ],
                "thresholds": {
                    "certified": self.certification.certified_threshold,
                    "provisional": self.certification.provisional_threshold,
                    "unanimous_bonus": self.certification.unanimous_bonus,
                    "skeptic_veto_critical": self.certification.skeptic_veto_critical,
                },
            },
            "scraping": {
                "rate_limit": {
                    "requests_per_second": self.scraping.requests_per_second,
                    "burst": self.scraping.burst,
                    "exponential_backoff": self.scraping.exponential_backoff,
                },
                "error_handling": {
                    "max_retries": self.scraping.max_retries,
                    "skip_404": self.scraping.skip_404,
                    "backoff_429": self.scraping.backoff_429,
                },
                "stealth": {
                    "enable": self.scraping.enable_stealth,
                    "user_agents": self.scraping.user_agents,
                    "jitter_percent": self.scraping.jitter_percent,
                    "warm_up_requests": self.scraping.warm_up_requests,
                },
                "pilot_domain": self.scraping.pilot_domain,
            },
            "ingestion": {
                "validation": {
                    "strict_mode": self.ingestion.strict_mode,
                    "required_fields": self.ingestion.required_fields,
                },
                "deduplication": {
                    "similarity_threshold": self.ingestion.similarity_threshold,
                    "method": self.ingestion.dedup_method,
                },
                "storage": {
                    "pattern_directory": self.ingestion.pattern_directory,
                    "backup_enabled": self.ingestion.backup_enabled,
                },
            },
            "logging": {
                "level": self.logging.level,
                "log_dir": self.logging.log_dir,
                "json_output": self.logging.json_output,
            },
        }


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from file or use defaults.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Config instance
    """
    # Default config paths to check
    default_paths = [
        Path("config/autonomous_learning.yaml"),
        Path("autonomous_learning.yaml"),
        Path("/etc/eeFrame/autonomous_learning.yaml"),
    ]

    # Use provided path or search for default
    if config_path and config_path.exists():
        return Config.from_yaml(config_path)

    for path in default_paths:
        if path.exists():
            return Config.from_yaml(path)

    # Return default config
    return Config()
