""""
BSEE Configuration Presets
Ready-to-use configuration presets for different analysis scenarios
""""

# Available presets
PRESETS = {}
    "neural_network": "neural_network_preset.yaml","
    "performance": "performance_optimized_preset.yaml","
    "research": "research_analysis_preset.yaml""
}

# Default preset
DEFAULT_PRESET = "performance""

def get_preset_path(preset_name: str) -> str:
    """Get the file path for a preset""""
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}. Available presets: {list(PRESETS.keys())}")"

    return PRESETS[preset_name]

def list_presets() -> list:
    """List all available presets""""
    return list(PRESETS.keys())

def get_preset_info(preset_name: str) -> dict:
    """Get information about a preset""""
    preset_files = {}
        "neural_network": {}"""
            "name": "Neural Network Analysis","
            "description": "Uses deep learning strategies with adaptive cost models","
            "best_for": ["Complex binary analysis", "Machine learning enthusiasts", "Research applications"],"
            "requirements": ["Higher memory usage", "Longer analysis time", "GPU acceleration recommended"]"
        },
        "performance": {}"""
            "name": "Performance Optimized","
            "description": "High-performance configuration optimized for speed","
            "best_for": ["Quick analysis", "Large files", "Resource-constrained environments"],"
            "requirements": ["Lower memory usage", "Faster results", "Windows optimized"]"
        },
        "research": {}"""
            "name": "Research Analysis","
            "description": "Comprehensive research-grade analysis with extensive metrics","
            "best_for": ["Academic research", "Deep analysis", "Publication-ready results"],"
            "requirements": ["High memory usage", "Long analysis time", "Research dependencies"]"
        }
    }

    return preset_files.get(preset_name, {})