"""
NeoPlato Game Hub
=================
Main hub interface for the game platform.

Note: This module was decompiled from Python 3.13 bytecode (hub.pyc).
The decompiler had issues with the complex code, so we load from compiled bytecode.
"""

import sys
import os
import importlib.util
from pathlib import Path

# Try to load the actual compiled hub module from hub.pyc
def _load_compiled_hub():
    """Load the actual GameHub class from hub.pyc bytecode."""
    try:
        pyc_path = Path(__file__).parent / "hub.pyc"
        
        # Create a spec for loading from pyc file
        spec = importlib.util.spec_from_file_location(
            "_hub_compiled",
            pyc_path,
            loader=importlib.util.SourceFileLoader("_hub_compiled", str(pyc_path))
        )
        
        if spec is None:
            raise ImportError("Could not create spec from hub.pyc")
        
        # Try different loading strategies
        try:
            # Strategy 1: Load pyc directly using the bytecode loader
            import marshal
            with open(pyc_path, 'rb') as f:
                # Skip pyc header (16 bytes for Python 3.13)
                f.read(16)
                code_obj = marshal.load(f)
            
            # Create module and execute the code
            module = type(sys)('_hub_compiled')
            module.__file__ = str(pyc_path)
            module.__loader__ = None
            module.__spec__ = None
            
            # Execute the code object to populate the module
            exec(code_obj, module.__dict__)
            return module
        except Exception as e1:
            print(f"[DEBUG] Strategy 1 failed: {e1}")
            raise
            
    except Exception as e:
        print(f"[DEBUG] Could not load hub.pyc: {e}")
        return None

# Try to load compiled hub
_hub_module = _load_compiled_hub()

if _hub_module and hasattr(_hub_module, 'GameHub'):
    GameHub = _hub_module.GameHub
    print("[INFO] Loaded GameHub from hub.pyc bytecode")
else:
    # Fallback: Create comprehensive stub that supports patching
    print("[WARNING] Could not load GameHub from hub.pyc - using stub")
    
    class GameHub:
        """Stub GameHub - actual implementation in hub.pyc not accessible."""
        
        GAME_ENTRIES = []
        
        def __init__(self, root):
            self.root = root
            self.theme = None
            self.storage = None
            self.bankroll = None
            self.achievements = None
            self.sounds = None
            self.particles = None
            self.logo_canvas = None
            self.header_canvas = None
            self.cards_canvas = None
            self.cards_frame = None
            self.sidebar = None
            self.sidebar_canvas = None
            self.sidebar_scrollbar = None
            self.sidebar_inner = None
            self.sidebar_window = None
            
        def _draw_logo(self):
            """Stub - would draw the logo."""
            pass
        
        def _build_sidebar(self):
            """Stub - would build the sidebar."""
            pass
        
        def _draw_header(self):
            """Stub - would draw the header."""
            pass
        
        def _build_game_cards(self):
            """Stub - would build game cards."""
            pass
        
        def _create_game_card(self, parent, game, row, col):
            """Stub - would create a game card."""
            pass
        
        def _start_ambient(self):
            """Stub - would start ambient animations."""
            pass
        
        def _spawn_ambient_particles(self):
            """Stub - would spawn particles."""
            pass
        
        def _animate_ambient(self):
            """Stub - would animate particles."""
            pass
        
        def _navigate(self, game_id):
            """Stub - would navigate to a game."""
            pass
        
        def run(self):
            """Stub - would run the hub."""
            pass
        
        def cleanup(self):
            """Stub - would clean up resources."""
            pass

# Re-export for imports
__all__ = ['GameHub']
