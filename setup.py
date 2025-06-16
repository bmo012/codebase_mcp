#!/usr/bin/env python3
"""
Setup script for AI Coding Agent with MCP Server
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error {description}: {e.stderr}")
        return None

def setup_python_environment():
    """Setup Python virtual environment and install dependencies"""
    print("🐍 Setting up Python environment")
    
    # Create virtual environment
    if not os.path.exists("venv"):
        run_command("python -m venv venv", "Creating virtual environment")
    
    # Activate virtual environment and install dependencies
    if sys.platform == "win32":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies")
    
    return python_cmd

def setup_directories():
    """Create necessary directories"""
    print("📁 Creating directory structure")
    
    directories = [
        "templates",
        "generated_code",
        "logs",
        "data",
        "examples"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ Created {directory}/")

def setup_mcp_server():
    """Setup MCP server configuration"""
    print("🔗 Setting up MCP server")
    
    # Create environment file
    env_content = """# AI Coding Agent Environment Variables
# Copy this to .env and fill in your values

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database Configuration
DATABASE_CONNECTION_STRING=Server=localhost;Database=YourAppDB;Trusted_Connection=true;

# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/mcp_server.log
"""
    
    with open(".env.example", "w") as f:
        f.write(env_content)
    
    print("  ✅ Created .env.example file")
    print("  📝 Please copy .env.example to .env and fill in your configuration")

def create_run_scripts():
    """Create convenience scripts to run the server"""
    print("📜 Creating run scripts")
    
    # Windows batch file
    windows_script = """@echo off
echo Starting AI Coding Agent MCP Server...
venv\\Scripts\\python mcp_server\\code_graph_server.py
pause
"""
    
    with open("run_server.bat", "w") as f:
        f.write(windows_script)
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting AI Coding Agent MCP Server..."
source venv/bin/activate
python mcp_server/code_graph_server.py
"""
    
    with open("run_server.sh", "w") as f:
        f.write(unix_script)
    
    # Make shell script executable on Unix systems
    if sys.platform != "win32":
        os.chmod("run_server.sh", 0o755)
    
    print("  ✅ Created run_server.bat (Windows)")
    print("  ✅ Created run_server.sh (Unix/Linux/Mac)")

def create_cursor_config():
    """Create Cursor IDE configuration"""
    print("🎯 Creating Cursor configuration")
    
    cursor_config = {
        "mcp": {
            "servers": {
                "code-graph-mcp": {
                    "command": "python",
                    "args": ["mcp_server/code_graph_server.py"],
                    "env": {
                        "PYTHONPATH": "."
                    }
                }
            }
        }
    }
    
    import json
    with open("cursor_mcp_config.json", "w") as f:
        json.dump(cursor_config, f, indent=2)
    
    print("  ✅ Created cursor_mcp_config.json")
    print("  📝 Add this configuration to your Cursor settings")

def main():
    """Main setup function"""
    print("🚀 AI Coding Agent Setup")
    print("=" * 50)
    
    try:
        # Setup Python environment
        python_cmd = setup_python_environment()
        
        # Create directories
        setup_directories()
        
        # Setup MCP server
        setup_mcp_server()
        
        # Create run scripts
        create_run_scripts()
        
        # Create Cursor config
        create_cursor_config()
        
        print("\\n🎉 Setup completed successfully!")
        print("\\n📋 Next Steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Add your OpenAI or Anthropic API keys")
        print("3. Configure your database connection string")
        print("4. Run the MCP server using run_server.bat (Windows) or run_server.sh (Unix)")
        print("5. Configure Cursor IDE to use the MCP server")
        print("6. Start generating code!")
        
        print("\\n📚 Quick Start:")
        print("  # Test the installation")
        if sys.platform == "win32":
            print("  python example_usage.py")
        else:
            print("  ./venv/bin/python example_usage.py")
        
        print("\\n  # Start the MCP server")
        if sys.platform == "win32":
            print("  run_server.bat")
        else:
            print("  ./run_server.sh")
            
    except Exception as e:
        print(f"\\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 