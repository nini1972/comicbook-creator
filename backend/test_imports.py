#!/usr/bin/env python3

# Test script to isolate the CrewAI import issue
print("Starting import test...")

try:
    print("1. Importing basic modules...")
    import sys
    import os
    from pathlib import Path
    print("   ✓ Basic modules imported")
    
    print("2. Adding backend directory to path...")
    sys.path.append(str(Path(__file__).resolve().parent))
    print("   ✓ Path added")
    
    print("3. Importing FastAPI...")
    import uvicorn
    from fastapi import FastAPI
    print("   ✓ FastAPI imported")
    
    print("4. Importing CrewAI...")
    import crewai
    print("   ✓ CrewAI imported")
    
    print("5. Importing our crew module...")
    from src.visual_comic_crew.crew import VisualComicCrew
    print("   ✓ VisualComicCrew imported")
    
    print("6. Creating crew instance...")
    crew_instance = VisualComicCrew()
    print("   ✓ VisualComicCrew instance created")
    
    print("7. Creating FastAPI app...")
    app = FastAPI()
    print("   ✓ FastAPI app created")
    
    print("\n✅ All imports successful! The issue might be elsewhere.")
    
except Exception as e:
    print(f"\n❌ Error at step: {e}")
    import traceback
    traceback.print_exc()
