"""
Niche manager for handling content niches.

This module manages niche selection, configuration, and statistics.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.utils import (
    bold, cyan, dark_grey, green, light_grey, red,
    get_config, ensure_dir
)


class NicheManager:
    """Manages content niches and their configurations."""
    
    def __init__(self, niches_base_path: Optional[str] = None):
        """
        Initialize niche manager.
        
        Args:
            niches_base_path: Base path for niches directory
        """
        config = get_config()
        self.niches_base_path = niches_base_path or config.get('paths.niches_dir', 'data/niches')
        ensure_dir(self.niches_base_path)
    
    def list_niches(self) -> List[str]:
        """
        List all available niches.
        
        Returns:
            List of niche names
        """
        if not os.path.exists(self.niches_base_path):
            return []
        
        niches = []
        for item in os.listdir(self.niches_base_path):
            item_path = os.path.join(self.niches_base_path, item)
            if os.path.isdir(item_path):
                # Check if it has config or is a legacy niche (starts with !)
                config_path = os.path.join(item_path, 'config.yaml')
                if os.path.exists(config_path) or item.startswith('!'):
                    niches.append(item)
        
        return sorted(niches)
    
    def select_niche(self) -> Optional[str]:
        """
        Prompt user to select a niche.
        
        Returns:
            Selected niche path or None if cancelled
        """
        niches = self.list_niches()
        
        if not niches:
            print(red("No niches found. Please create a niche first."))
            return None
        
        print(bold("\nWhat niche do you want to work with?"))
        for i, niche in enumerate(niches, start=1):
            # Remove ! prefix for display if present
            display_name = niche[1:] if niche.startswith('!') else niche
            print(f"    {i}. {cyan(display_name)}")
        
        try:
            choice = int(input("> ").strip())
            if 1 <= choice <= len(niches):
                selected_niche = niches[choice - 1]
                return os.path.join(self.niches_base_path, selected_niche)
            else:
                print(red("Invalid choice. Please select a valid number from the list."))
                return None
        except ValueError:
            print(red("Invalid input. Please enter a number."))
            return None
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None
    
    def get_niche_config(self, niche_path: str) -> Dict:
        """
        Get configuration for a specific niche.
        
        Args:
            niche_path: Path to niche directory
            
        Returns:
            Niche configuration dictionary
        """
        config_path = os.path.join(niche_path, 'config.yaml')
        config = get_config()
        
        if os.path.exists(config_path):
            return config.load_niche_config(niche_path)
        
        # Return default configuration for legacy niches
        return self._get_default_niche_config(niche_path)
    
    def get_credentials(self, niche_path: str) -> Dict:
        """
        Load credentials for a niche.
        
        Args:
            niche_path: Path to niche directory
            
        Returns:
            Credentials dictionary
        """
        credentials_path = os.path.join(niche_path, 'credentials.json')
        
        # Also check for Credentials.json (legacy)
        if not os.path.exists(credentials_path):
            legacy_path = os.path.join(niche_path, 'Credentials.json')
            if os.path.exists(legacy_path):
                credentials_path = legacy_path
        
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(
                f"Credentials file not found for niche. Please create: {credentials_path}"
            )
        
        with open(credentials_path, 'r') as f:
            return json.load(f)
    
    def get_upload_log(self, niche_path: str) -> Dict:
        """
        Load upload log for a niche.
        
        Args:
            niche_path: Path to niche directory
            
        Returns:
            Upload log dictionary
        """
        upload_log_path = os.path.join(niche_path, 'upload_log.json')
        
        if os.path.exists(upload_log_path):
            with open(upload_log_path, 'r') as f:
                return json.load(f)
        
        # Return default empty log
        return {
            'last_video_number_youtube': 0,
            'last_schedule_time_youtube': 'N/A',
            'last_video_number_tiktok': 0,
            'last_schedule_time_tiktok': 'N/A'
        }
    
    def update_upload_log(self, niche_path: str, log_data: Dict) -> None:
        """
        Update upload log for a niche.
        
        Args:
            niche_path: Path to niche directory
            log_data: Upload log data to save
        """
        upload_log_path = os.path.join(niche_path, 'upload_log.json')
        
        with open(upload_log_path, 'w') as f:
            json.dump(log_data, f, indent=4)
    
    def get_niche_summary(self, niche_path: str) -> None:
        """
        Display summary information about a niche.
        
        Args:
            niche_path: Path to niche directory
        """
        niche_name = os.path.basename(niche_path)
        # Remove ! prefix if present
        if niche_name.startswith('!'):
            niche_name = niche_name[1:]
        
        # Get last made video
        final_videos_path = self._get_folder_path(niche_path, 'final_videos', 'Meme-Final')
        last_made = self._get_last_video_number(final_videos_path, '_long.mp4')
        
        # Get upload log
        upload_log = self.get_upload_log(niche_path)
        
        youtube_number = f"meme_{upload_log.get('last_video_number_youtube', 0):04d}"
        youtube_time = self._format_datetime(upload_log.get('last_schedule_time_youtube', 'N/A'))
        
        tiktok_number = f"meme_{upload_log.get('last_video_number_tiktok', 0):04d}"
        tiktok_time = self._format_datetime(upload_log.get('last_schedule_time_tiktok', 'N/A'))
        
        print('\n')
        print(dark_grey(bold(f"Info about niche {light_grey(niche_name)}:")))
        print(dark_grey(f"* Last made video number: {bold(light_grey(last_made))}"))
        print(dark_grey(f"* Last video uploaded to YouTube: {bold(light_grey(youtube_number))} — {bold(light_grey(youtube_time))}"))
        print(dark_grey(f"* Last video uploaded to TikTok: {bold(light_grey(tiktok_number))} — {bold(light_grey(tiktok_time))}"))
        print('\n')
    
    def ensure_niche_structure(self, niche_path: str) -> None:
        """
        Ensure all required directories exist for a niche.
        
        Args:
            niche_path: Path to niche directory
        """
        directories = [
            'raw_images',
            'meme_images',
            'fade_videos',
            'final_videos',
            'tiktok_sounds',
            'descriptions'
        ]
        
        # Also support legacy names
        legacy_dirs = {
            'raw_images': 'Raw-Images',
            'meme_images': 'Meme-Images',
            'fade_videos': 'Meme-Fade',
            'final_videos': 'Meme-Final',
            'tiktok_sounds': 'TikTok-Sounds',
            'descriptions': 'Meme-Description'
        }
        
        for directory in directories:
            new_path = os.path.join(niche_path, directory)
            legacy_path = os.path.join(niche_path, legacy_dirs.get(directory, directory))
            
            # Use legacy path if it exists, otherwise create new path
            if not os.path.exists(new_path) and not os.path.exists(legacy_path):
                ensure_dir(new_path)
    
    def _get_folder_path(self, niche_path: str, new_name: str, legacy_name: str) -> str:
        """Get folder path, checking both new and legacy names."""
        new_path = os.path.join(niche_path, new_name)
        legacy_path = os.path.join(niche_path, legacy_name)
        
        if os.path.exists(new_path):
            return new_path
        elif os.path.exists(legacy_path):
            return legacy_path
        else:
            ensure_dir(new_path)
            return new_path
    
    def _get_last_video_number(self, folder: str, suffix: str) -> str:
        """Get the last video number from a folder."""
        if not os.path.exists(folder):
            return "meme_0000"
        
        files = [f for f in os.listdir(folder) if f.startswith('meme_') and f.endswith(suffix)]
        
        if not files:
            return "meme_0000"
        
        latest = max(files, key=lambda x: int(x.split('_')[1]))
        return latest.split('_')[1].split('.')[0] if '_' in latest else "0000"
    
    def _format_datetime(self, dt_string: str) -> str:
        """Format datetime string for display."""
        if dt_string == 'N/A' or not dt_string:
            return 'N/A'
        
        try:
            dt = datetime.fromisoformat(dt_string)
            return f"{dt.strftime('%H:%M')} ({dt.strftime('%d %b %Y')})"
        except (ValueError, AttributeError):
            return dt_string
    
    def _get_default_niche_config(self, niche_path: str) -> Dict:
        """Get default configuration for legacy niches."""
        niche_name = os.path.basename(niche_path)
        if niche_name.startswith('!'):
            niche_name = niche_name[1:]
        
        return {
            'niche': {
                'name': niche_name.lower(),
                'display_name': niche_name.capitalize(),
                'enabled': True
            },
            'paths': {
                'raw_images': 'Raw-Images',
                'meme_images': 'Meme-Images',
                'fade_videos': 'Meme-Fade',
                'final_videos': 'Meme-Final',
                'tiktok_sounds': 'TikTok-Sounds',
                'descriptions': 'Meme-Description',
                'quotes': 'Quotes.txt',
                'tiktok_sounds_list': 'TikTok-Sounds.txt'
            },
            'content': {
                'hashtags': {
                    'youtube': '#meme #funny #viral',
                    'tiktok': '#meme #fyp #funny',
                    'instagram': '#meme #funny #viral'
                }
            },
            'schedule': {
                'time_set': 'set_1',
                'youtube': {'enabled': True, 'videos_per_day': 3},
                'tiktok': {'enabled': True, 'videos_per_day': 3}
            }
        }
