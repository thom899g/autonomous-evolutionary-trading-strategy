"""
Configuration management for the Autonomous Evolutionary Trading System.
Centralized configuration with environment variable support and validation.
"""
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingMode(Enum):
    """Trading operation modes"""
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"


class ExchangeType(Enum):
    """Supported exchange types"""
    BINANCE = "binance"
    COINBASE = "coinbase"
    KRAKEN = "kraken"


@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")
    private_key_id: str = os.getenv("FIREBASE_PRIVATE_KEY_ID", "")
    private_key: str = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
    client_email: str = os.getenv("FIREBASE_CLIENT_EMAIL", "")
    client_id: str = os.getenv("FIREBASE_CLIENT_ID", "")
    database_url: str = os.getenv("FIREBASE_DATABASE_URL", "")

    def validate(self) -> bool:
        """Validate Firebase configuration"""
        required_fields = [self.project_id, self.private_key, self.client_email]
        if not all(required_fields):
            logger.warning("Firebase configuration incomplete. Some features may be disabled.")
            return False
        return True


@dataclass
class TradingConfig:
    """Trading-specific configuration"""
    mode: TradingMode = TradingMode.PAPER
    exchange: ExchangeType = ExchangeType.BINANCE
    api_key: str = os.getenv("EXCHANGE_API_KEY", "")
    api_secret: str = os.getenv("EXCHANGE_API_SECRET", "")
    
    # Risk management
    max_position_size: float = 0.1  # 10% of portfolio per trade
    max_daily_loss: float = 0.02  # 2% max daily loss
    max_open_positions: int = 5
    
    # Trading parameters
    default_symbols: list = field(default_factory=lambda: ["BTC/USDT", "ETH/USDT"])
    timeframe: str = "1h"
    
    def validate(self) -> None:
        """Validate trading configuration"""
        if self.mode == TradingMode.LIVE and (not self.api_key or not self.api_secret):
            raise ValueError("API credentials required for LIVE trading mode")
        
        if self.max_position_size > 0.5:
            logger.warning("Position size exceeds recommended maximum of 50%")


@dataclass
class SystemConfig:
    """System-wide configuration"""
    # Performance
    max_workers: int = 4
    cache_ttl: int = 300  # 5 minutes
    
    # Evolution parameters
    population_size: int = 50
    generations_per_epoch: int = 100
    mutation_rate: float = 0.1
    
    # Logging
    log_level: str = "INFO"
    enable_telegram_alerts: bool = True
    
    # Firebase
    use_firebase: bool = True
    firestore_collections: Dict[str, str] = field(default_factory=lambda: {
        "strategies": "evolutionary_strategies",
        "trades": "executed_trades",
        "market_data": "market_metrics",
        "performance": "strategy_performance"
    })


class ConfigManager:
    """Centralized configuration manager"""
    
    _instance: Optional['ConfigManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize configuration from environment"""
        self.firebase = FirebaseConfig()
        self.trading = TradingConfig()
        self.system = SystemConfig()
        
        # Validate configurations
        self._validate_configs()
        logger.info("Configuration initialized successfully")
    
    def _validate_configs(self):
        """Validate all configurations"""
        try:
            self.trading.validate()
            
            if self.system.use_firebase:
                if not self.firebase.validate():
                    logger.warning("Firebase configuration invalid. Disabling Firebase features.")
                    self.system.use_firebase = False
                    
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
    
    def update_from_dict(self, config_dict: Dict[str, Any]):
        """Update configuration from dictionary"""
        for section, values in config_dict.items():
            config_section = getattr(self, section, None)
            if config_section:
                for key, value in values.items():
                    if hasattr(config_section, key):
                        setattr(config_section, key, value)
        
        self._validate_configs()
        logger.info("Configuration updated from dictionary")


# Global configuration instance
config = ConfigManager()