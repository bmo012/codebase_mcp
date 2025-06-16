#!/usr/bin/env python3
"""
Setup script for Cursor MCP Server Integration

This script automates the setup process for the Code Graph MCP server
to work with Cursor IDE.
"""

import os
import json
import subprocess
import sys
from pathlib import Path
import shutil

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} found")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        ".cursor",
        "logs",
        "generated_code",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def setup_cursor_mcp_config():
    """Setup Cursor MCP configuration"""
    cursor_dir = Path(".cursor")
    cursor_dir.mkdir(exist_ok=True)
    
    mcp_config = {
        "mcpServers": {
            "code-graph-mcp": {
                "command": "python",
                "args": [
                    "mcp_server/enhanced_code_graph_server.py"
                ],
                "env": {
                    "PYTHONPATH": ".",
                    "PYTHONUNBUFFERED": "1"
                }
            }
        }
    }
    
    config_path = cursor_dir / "mcp.json"
    with open(config_path, 'w') as f:
        json.dump(mcp_config, f, indent=2)
    
    print(f"✅ Created Cursor MCP configuration: {config_path}")

def create_env_template():
    """Create environment template file"""
    env_template = """# Code Graph MCP Server Environment Configuration

# Database Configuration
DATABASE_CONNECTION_STRING=Server=localhost;Database=YourAppDB;Trusted_Connection=true;

# Optional: AI Model Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=mcp_server.log
"""
    
    env_path = Path(".env.example")
    with open(env_path, 'w') as f:
        f.write(env_template)
    
    print(f"✅ Created environment template: {env_path}")
    
    # Create actual .env file if it doesn't exist
    if not Path(".env").exists():
        shutil.copy(env_path, ".env")
        print("✅ Created .env file from template")

def verify_mcp_server():
    """Verify MCP server can be imported and run"""
    print("🔍 Verifying MCP server...")
    try:
        # Try to import the server module
        sys.path.insert(0, os.getcwd())
        from mcp_server.enhanced_code_graph_server import EnhancedCodeGraphServer
        
        # Create a test server instance
        server = EnhancedCodeGraphServer()
        print("✅ MCP server can be imported successfully")
        
        # Test basic functionality
        summary = server.get_node_types_summary()
        print("✅ MCP server basic functionality working")
        
        return True
    except Exception as e:
        print(f"❌ MCP server verification failed: {e}")
        return False

def create_test_files():
    """Create sample test files for demonstration"""
    test_files_dir = Path("test_files")
    test_files_dir.mkdir(exist_ok=True)
    
    # Sample C# class
    sample_cs = '''using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace TestApp.BusinessLogic
{
    public class CustomerManager
    {
        private readonly string _connectionString;
        
        public CustomerManager(string connectionString)
        {
            _connectionString = connectionString;
        }
        
        public async Task<List<Customer>> GetCustomersAsync()
        {
            // Implementation here
            return new List<Customer>();
        }
        
        public async Task<bool> SaveCustomerAsync(Customer customer)
        {
            // Implementation here
            return true;
        }
    }
    
    public class Customer
    {
        public int CustomerID { get; set; }
        public string CustomerName { get; set; }
        public string Email { get; set; }
        public bool IsActive { get; set; }
    }
}'''
    
    # Sample SQL
    sample_sql = '''-- Customer Management Stored Procedures

CREATE PROCEDURE sp_GetCustomers
    @CustomerID INT = NULL,
    @IsActive BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        SELECT CustomerID, CustomerName, Email, IsActive
        FROM Customers
        WHERE (@CustomerID IS NULL OR CustomerID = @CustomerID)
        AND IsActive = @IsActive
        ORDER BY CustomerName
        
        RETURN 0
    END TRY
    BEGIN CATCH
        RETURN -1
    END CATCH
END
GO

CREATE PROCEDURE sp_SaveCustomer
    @CustomerID INT = NULL,
    @CustomerName NVARCHAR(255),
    @Email NVARCHAR(255),
    @IsActive BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        IF @CustomerID IS NULL
            INSERT INTO Customers (CustomerName, Email, IsActive)
            VALUES (@CustomerName, @Email, @IsActive)
        ELSE
            UPDATE Customers 
            SET CustomerName = @CustomerName,
                Email = @Email,
                IsActive = @IsActive
            WHERE CustomerID = @CustomerID
            
        RETURN 0
    END TRY
    BEGIN CATCH
        RETURN -1
    END CATCH
END'''
    
    with open(test_files_dir / "CustomerManager.cs", 'w') as f:
        f.write(sample_cs)
    
    with open(test_files_dir / "sp_CustomerProcedures.sql", 'w') as f:
        f.write(sample_sql)
    
    print(f"✅ Created test files in: {test_files_dir}")

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "="*60)
    print("🎉 CURSOR MCP SERVER SETUP COMPLETE!")
    print("="*60)
    print("\nNext Steps:")
    print("1. ✅ Open Cursor IDE")
    print("2. ✅ Go to Settings → Features → Model Context Protocol")
    print("3. ✅ Verify 'code-graph-mcp' server is listed and enabled")
    print("4. ✅ Edit the .env file with your database connection string")
    print("5. ✅ Test the integration by asking Cursor to:")
    print("      'Analyze the test files using the MCP server'")
    print("\nExample Commands to Try in Cursor Chat:")
    print("- 'Use the MCP server to analyze the CustomerManager.cs file'")
    print("- 'Show me a summary of code elements using the MCP server'")
    print("- 'Find database CRUD patterns using the MCP server'")
    print("\nFor detailed usage instructions, see: CURSOR_MCP_SETUP.md")
    print("\nTroubleshooting: Check logs in mcp_server.log")

def main():
    """Main setup function"""
    print("🚀 Setting up Cursor MCP Server Integration...")
    print("-" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    # Setup steps
    steps = [
        ("Creating directories", create_directories),
        ("Installing dependencies", install_dependencies), 
        ("Setting up Cursor MCP config", setup_cursor_mcp_config),
        ("Creating environment template", create_env_template),
        ("Creating test files", create_test_files),
        ("Verifying MCP server", verify_mcp_server)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        try:
            result = step_func()
            if result is False:
                print(f"❌ Setup failed at: {step_name}")
                return False
        except Exception as e:
            print(f"❌ Error during {step_name}: {e}")
            return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 