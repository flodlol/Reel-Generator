"""
Configuration management utilities.

This module handles loading and managing configuration files.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_dir: str = "config", env_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
            env_file: Path to .env file (optional)
        """
        self.config_dir = config_dir
        self.config: Dict[str, Any] = {}
        
        # Load environment variables
        if env_file and os.path.exists(env_file):
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from default .env if exists
        
        # Load main configuration
        self.load_main_config()
    
    def load_main_config(self) -> None:
        """Load the main configuration file."""
        config_file = os.path.join(self.config_dir, "config.yaml")
        
        if not os.path.exists(config_file):
            # Try example file
            example_file = os.path.join(self.config_dir, "config.example.yaml")
            if os.path.exists(example_file):
                raise FileNotFoundError(
                    f"Configuration file not found. Please copy {example_file} to {config_file}"
                )
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f) or {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'app.name' or 'video.duration')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        # Check environment variable override
        env_key = '_'.join(keys).upper()
        env_value = os.getenv(env_key)
        if env_value is not None:
            return self._convert_type(env_value, type(value))
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: Section name (e.g., 'video', 'upload')
            
        Returns:
            Configuration section dictionary
        """
        return self.config.get(section, {})
    
    def load_niche_config(self, niche_path: str) -> Dict[str, Any]:
        """
        Load configuration for a specific niche.
        
        Args:
            niche_path: Path to niche directory
            
        Returns:
            Niche configuration dictionary
        """
        config_file = os.path.join(niche_path, "config.yaml")
        
        if not os.path.exists(config_file):
            return {}
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def load_credentials(self, credentials_path: str) -> Dict[str, Any]:
        """
        Load credentials from a JSON file.
        
        Args:
            credentials_path: Path to credentials.json file
            
        Returns:
            Credentials dictionary
        """
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
        
        with open(credentials_path, 'r') as f:
            return json.load(f)
    
    def save_json(self, data: Dict[str, Any], file_path: str) -> None:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            file_path: Path to save file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, file_path, indent=4)
    
    @staticmethod
    def _convert_type(value: str, target_type: type) -> Any:
        """Convert string value to target type."""
        if target_type == bool:
            return value.lower() in ('true', '1', 'yes', 'on')
        elif target_type == int:
            try:
                return int(value)
            except ValueError:
                return value
        elif target_type == float:
            try:
                return float(value)
            except ValueError:
                return value
        return value


# Global configuration instance
_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get the global configuration instance.
    
    Returns:
        ConfigManager instance
    """
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config


def init_config(config_dir: str = "config", env_file: Optional[str] = None) -> ConfigManager:
    """
    Initialize the global configuration instance.
    
    Args:
        config_dir: Directory containing configuration files
        env_file: Path to .env file
        
    Returns:
        ConfigManager instance
    """
    global _config
    _config = ConfigManager(config_dir, env_file)
    return _config
