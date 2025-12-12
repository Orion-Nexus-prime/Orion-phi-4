"""
Configuration management for Orion Phi-4 system
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Configuration manager for system and trading configs"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.config_dir = Path("configs")
            self.configs: Dict[str, Dict[str, Any]] = {}
            self._load_configs()
    
    def _load_configs(self):
        """Load all configuration files"""
        config_files = {
            'system': 'system_config.yaml',
            'trading': 'trading_config.yaml'
        }
        
        for config_name, filename in config_files.items():
            config_path = self.config_dir / filename
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        self.configs[config_name] = yaml.safe_load(f)
                    logger.info(f"Loaded {config_name} configuration from {filename}")
                except Exception as e:
                    logger.error(f"Error loading {config_name} config: {e}")
                    self.configs[config_name] = {}
            else:
                logger.warning(f"Configuration file not found: {config_path}")
                self.configs[config_name] = {}
    
    def get(self, config_type: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            config_type: Type of config ('system' or 'trading')
            key: Configuration key (supports nested keys with dots)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        if config_type not in self.configs:
            return default
        
        config = self.configs[config_type]
        keys = key.split('.')
        
        for k in keys:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return default
        
        return config
    
    def set(self, config_type: str, key: str, value: Any):
        """
        Set configuration value
        
        Args:
            config_type: Type of config ('system' or 'trading')
            key: Configuration key (supports nested keys with dots)
            value: Value to set
        """
        if config_type not in self.configs:
            self.configs[config_type] = {}
        
        config = self.configs[config_type]
        keys = key.split('.')
        
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, config_type: str):
        """
        Save configuration to file
        
        Args:
            config_type: Type of config to save
        """
        if config_type not in self.configs:
            logger.error(f"Configuration type not found: {config_type}")
            return
        
        filename = f"{config_type}_config.yaml"
        config_path = self.config_dir / filename
        
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(config_path, 'w') as f:
                yaml.dump(self.configs[config_type], f, default_flow_style=False)
            logger.info(f"Saved {config_type} configuration to {filename}")
        except Exception as e:
            logger.error(f"Error saving {config_type} config: {e}")
    
    def reload(self):
        """Reload all configurations"""
        self.configs.clear()
        self._load_configs()
        logger.info("Reloaded all configurations")


# Global config manager instance
config_manager = ConfigManager()


def get_config(config_type: str, key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config_manager.get(config_type, key, default)


def set_config(config_type: str, key: str, value: Any):
    """Set configuration value"""
    config_manager.set(config_type, key, value)
