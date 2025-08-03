#!/usr/bin/env python3
"""
Check installed versions of all packages
"""

import subprocess
import sys

def get_package_version(package_name):
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True
        )
        for line in result.stdout.split('\n'):
            if line.startswith('Version:'):
                return line.split(':')[1].strip()
    except:
        return "Not installed"
    return "Unknown"

packages = [
    "livekit",
    "livekit-agents", 
    "livekit-plugins-openai",
    "livekit-plugins-elevenlabs",
    "livekit-api",
    "livekit-protocol",
    "openai",
    "python-dotenv"
]

print("📦 Installed Package Versions:")
print("=" * 50)

for package in packages:
    version = get_package_version(package)
    print(f"{package}: {version}")

print("\n" + "=" * 50)
print("\n💡 If you're having issues, try updating to the latest versions:")
print("pip install --upgrade livekit livekit-agents livekit-plugins-openai livekit-plugins-elevenlabs")