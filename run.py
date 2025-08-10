#!/usr/bin/env python3
"""
ADGM Corporate Agent - Startup Script
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add app directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def create_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "outputs", 
        "data",
        "data/chroma_db",
        "data/adgm_knowledge"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True, parents=True)
        print(f"✓ Created directory: {directory}")

def check_environment():
    """Check environment configuration"""
    required_env_vars = ["GEMINI_API_KEY"]
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file based on .env.example")
        return False
    
    print("✓ Environment variables configured")
    return True

def main():
    """Main startup function"""
    print("🚀 Starting ADGM Corporate Agent...")
    print("=" * 50)
    
    # Create directories
    print("Creating directories...")
    create_directories()
    
    # Check environment
    print("Checking environment...")
    if not check_environment():
        sys.exit(1)
    
    # Start server
    print("Starting FastAPI server...")
    print("=" * 50)
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("📖 API Documentation at: http://localhost:8000/docs")
    print("🔍 Interactive API at: http://localhost:8000/redoc")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            reload=os.getenv("DEBUG_MODE", "true").lower() == "true",
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 ADGM Corporate Agent stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()