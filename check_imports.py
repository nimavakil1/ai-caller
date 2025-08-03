#!/usr/bin/env python3
"""
Check what's available in livekit-agents
"""

import sys
print(f"Python version: {sys.version}")

try:
    import livekit
    print(f"\n✓ livekit version: {livekit.__version__}")
except Exception as e:
    print(f"\n✗ livekit import error: {e}")

try:
    import livekit.agents
    print(f"✓ livekit.agents imported successfully")
    
    # List what's available in livekit.agents
    print("\nAvailable in livekit.agents:")
    for item in dir(livekit.agents):
        if not item.startswith('_'):
            print(f"  - {item}")
            
except Exception as e:
    print(f"✗ livekit.agents import error: {e}")

# Try different import paths for VoiceAssistant
print("\n\nTrying different import paths for VoiceAssistant:")

paths_to_try = [
    ("from livekit.agents.voice_assistant import VoiceAssistant", "livekit.agents.voice_assistant"),
    ("from livekit.agents import VoiceAssistant", "livekit.agents"),
    ("from livekit.agents.voice import VoiceAssistant", "livekit.agents.voice"),
    ("from livekit.agents.assistant import VoiceAssistant", "livekit.agents.assistant"),
]

for import_statement, module_path in paths_to_try:
    try:
        exec(import_statement)
        print(f"✓ SUCCESS: {import_statement}")
        break
    except ImportError as e:
        print(f"✗ Failed: {import_statement}")
        # Try to see what's in that module
        try:
            parts = module_path.split('.')
            mod = __import__(module_path, fromlist=[parts[-1]])
            print(f"  Available in {module_path}:")
            for item in dir(mod):
                if not item.startswith('_') and 'voice' in item.lower() or 'assistant' in item.lower():
                    print(f"    - {item}")
        except:
            pass

print("\n\nChecking for voice-related modules:")
try:
    import pkgutil
    import livekit.agents
    for importer, modname, ispkg in pkgutil.iter_modules(livekit.agents.__path__, livekit.agents.__name__ + "."):
        if 'voice' in modname or 'assistant' in modname:
            print(f"Found module: {modname}")
except:
    pass
