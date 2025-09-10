"""Configuration management for SEO Image Converter."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration manager with YAML file support."""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration."""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Override with environment variables if present
            self._apply_env_overrides(config)
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
    
    def _apply_env_overrides(self, config: Dict[str, Any]):
        """Apply environment variable overrides."""
        # Ollama settings
        if os.getenv('OLLAMA_ENDPOINT'):
            config['ollama']['endpoint'] = os.getenv('OLLAMA_ENDPOINT')
        if os.getenv('OLLAMA_MODEL'):
            config['ollama']['model'] = os.getenv('OLLAMA_MODEL')
        
        # Processing settings
        if os.getenv('MAX_PARALLEL_JOBS'):
            config['processing']['parallel_jobs'] = int(os.getenv('MAX_PARALLEL_JOBS'))
        if os.getenv('LOG_LEVEL'):
            config['logging']['level'] = os.getenv('LOG_LEVEL')
    
    @property
    def ollama(self) -> Dict[str, Any]:
        """Ollama configuration."""
        return self._config.get('ollama', {})
    
    @property
    def image(self) -> Dict[str, Any]:
        """Image processing configuration."""
        return self._config.get('image', {})
    
    @property
    def seo(self) -> Dict[str, Any]:
        """SEO configuration."""
        return self._config.get('seo', {})
    
    @property
    def processing(self) -> Dict[str, Any]:
        """Processing configuration."""
        return self._config.get('processing', {})
    
    @property
    def logging(self) -> Dict[str, Any]:
        """Logging configuration."""
        return self._config.get('logging', {})
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot notation support."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def update(self, key: str, value: Any):
        """Update configuration value with dot notation support."""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save(self, path: str = None):
        """Save configuration to YAML file."""
        save_path = Path(path) if path else self.config_path
        
        with open(save_path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False, indent=2)

# Global config instance
config = Config()