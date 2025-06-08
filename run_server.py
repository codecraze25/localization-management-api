#!/usr/bin/env python3
"""
Simple script to run the Localization Management API server
"""

import uvicorn
import os
from src.localization_management_api.config import get_settings

def main():
    """Run the FastAPI server"""
    settings = get_settings()

    print("🚀 Starting Localization Management API")
    print(f"📍 Host: {settings.api_host}")
    print(f"🔌 Port: {settings.api_port}")
    print(f"🐛 Debug: {settings.debug}")
    print(f"🌐 Frontend URL: {settings.frontend_url}")
    print("=" * 50)

    uvicorn.run(
        "src.localization_management_api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )

if __name__ == "__main__":
    main()