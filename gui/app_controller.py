"""
Application controller for GUI-BSEE integration.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class AppController:
    """Controller managing GUI application state and BSEE integration."""

    def __init__(self):
        """Initialize controller with default folders and settings."""
        self.app_dir = Path.cwd()
        self.setup_directories()
        self.load_settings()

    def setup_directories(self):
        """Create default directory structure."""
        self.directories = {
            'inputs': self.app_dir / 'inputs',
            'results': self.app_dir / 'results',
            'presets': self.app_dir / 'presets',
            'history': self.app_dir / 'history',
            'logs': self.app_dir / 'logs',
            'temp': self.app_dir / 'temp'
        }

        for directory in self.directories.values():
            directory.mkdir(exist_ok=True)

    def load_settings(self):
        """Load application settings."""
        settings_file = self.app_dir / 'gui_settings.json'
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.settings = self._get_default_settings()
        else:
            self.settings = self._get_default_settings()
            self.save_settings()

    def save_settings(self):
        """Save application settings."""
        settings_file = self.app_dir / 'gui_settings.json'
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save settings

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings."""
        return {
            'window_size': {'width': 1400, 'height': 900},
            'window_position': {'x': 100, 'y': 100},
            'last_input_folder': str(self.directories['inputs']),
            'default_strategy': 'greedy',
            'default_max_operations': 1000,
            'default_max_cost': 10000,
            'default_metrics': 'file_ideality_score,entropy_global,lz77_ratio',
            'default_target_metrics': 'file_ideality_score=max,entropy_global=min',
            'auto_refresh_visualization': True,
            'terminal_max_lines': 1000,
            'bit_display_bytes_per_row': 16,
            'theme': 'winnative',
            'recent_files': [],
            'presets': {}
        }

    def get_input_folder(self) -> str:
        """Get input folder path."""
        return str(self.directories['inputs'])

    def get_results_folder(self) -> str:
        """Get results folder path."""
        return str(self.directories['results'])

    def create_test_file(self, filename: str) -> None:
        """Create a test binary file with known patterns."""
        test_data = self._generate_test_data()
        with open(filename, 'wb') as f:
            f.write(test_data)

    def _generate_test_data(self) -> bytes:
        """Generate interesting test binary data."""
        import random
        import struct

        data = bytearray()

        # Add some repeated patterns
        data.extend(b'\xAA\x55\xAA\x55' * 64)  # Alternating pattern
        data.extend(b'\x00\xFF\x00\xFF' * 64)  # Complementary pattern
        data.extend(b'\x12\x34\x56\x78' * 32)  # Sequential pattern

        # Add some random data
        data.extend(bytes([random.randint(0, 255) for _ in range(256)]))

        # Add some structured data
        for i in range(64):
            data.extend(struct.pack('<I', i))  # Little-endian integers

        # Add some ASCII text
        data.extend(b"Hello, BSEE! This is a test binary file for analysis.\x00" * 8)

        # Add some high-entropy data
        data.extend(os.urandom(512))

        return bytes(data)

    def save_preset(self, name: str, config: Dict[str, Any]) -> None:
        """Save a configuration preset."""
        if 'presets' not in self.settings:
            self.settings['presets'] = {}

        self.settings['presets'][name] = {
            'name': name,
            'config': config,
            'created_at': datetime.now().isoformat()
        }

        # Also save to preset file
        preset_file = self.directories['presets'] / f'{name}.json'
        with open(preset_file, 'w') as f:
            json.dump(self.settings['presets'][name], f, indent=2)

        self.save_settings()

    def load_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a configuration preset."""
        if 'presets' not in self.settings:
            return None

        preset = self.settings['presets'].get(name)
        if preset:
            return preset.get('config')

        # Try loading from file
        preset_file = self.directories['presets'] / f'{name}.json'
        if preset_file.exists():
            try:
                with open(preset_file, 'r') as f:
                    preset = json.load(f)
                    return preset.get('config')
            except (json.JSONDecodeError, IOError):
                pass

        return None

    def list_presets(self) -> list:
        """List available presets."""
        presets = []
        if 'presets' in self.settings:
            presets.extend(self.settings['presets'].keys())

        # Also scan preset directory
        for preset_file in self.directories['presets'].glob('*.json'):
            name = preset_file.stem
            if name not in presets:
                presets.append(name)

        return sorted(presets)

    def add_recent_file(self, filepath: str) -> None:
        """Add file to recent files list."""
        if 'recent_files' not in self.settings:
            self.settings['recent_files'] = []

        # Remove if already exists
        if filepath in self.settings['recent_files']:
            self.settings['recent_files'].remove(filepath)

        # Add to beginning
        self.settings['recent_files'].insert(0, filepath)

        # Keep only last 10 files
        self.settings['recent_files'] = self.settings['recent_files'][:10]

        self.save_settings()

    def get_recent_files(self) -> list:
        """Get recent files list."""
        return self.settings.get('recent_files', [])

    def update_setting(self, key: str, value: Any) -> None:
        """Update a specific setting."""
        self.settings[key] = value
        self.save_settings()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting."""
        return self.settings.get(key, default)