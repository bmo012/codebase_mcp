#!/usr/bin/env python3
"""
Test script for Cursor MCP Server Integration

This script tests the MCP server functionality to ensure it works
correctly with Cursor IDE.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server.enhanced_code_graph_server import EnhancedCodeGraphServer

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing MCP Server Integration")
    print("-" * 40)
    
    try:
        # Initialize the server
        print("1. Initializing MCP server...")
        server = EnhancedCodeGraphServer()
        print("✅ Server initialized successfully")
        
        # Test file analysis
        print("\n2. Testing file analysis...")
        test_files = []
        
        # Check if test files exist
        test_dir = Path("test_files")
        if test_dir.exists():
            cs_file = test_dir / "CustomerManager.cs"
            sql_file = test_dir / "sp_CustomerProcedures.sql"
            
            if cs_file.exists():
                test_files.append(str(cs_file))
            if sql_file.exists():
                test_files.append(str(sql_file))
        
        if test_files:
            print(f"   Analyzing files: {test_files}")
            result = server.analyze_specific_files(test_files)
            print(f"✅ Analysis completed. Found {result.get('total_nodes', 0)} nodes and {result.get('total_relationships', 0)} relationships")
        else:
            print("⚠️  No test files found, skipping file analysis")
        
        # Test node types summary
        print("\n3. Testing node types summary...")
        node_summary = server.get_node_types_summary()
        print(f"✅ Node types: {json.dumps(node_summary, indent=2)}")
        
        # Test relationship types summary
        print("\n4. Testing relationship types summary...")
        rel_summary = server.get_relationship_types_summary()
        print(f"✅ Relationship types: {json.dumps(rel_summary, indent=2)}")
        
        # Test pattern finding
        print("\n5. Testing pattern finding...")
        patterns = server._identify_patterns()
        print(f"✅ Found {len(patterns)} patterns")
        for pattern in patterns[:3]:  # Show first 3 patterns
            print(f"   - {pattern.pattern_type}: {pattern.pattern_id}")
        
        # Test graph export
        print("\n6. Testing graph export...")
        export_path = "test_graph_export.json"
        export_data = server.export_graph_data(export_path)
        print(f"✅ Graph exported with {len(export_data['nodes'])} nodes")
        
        # Clean up test export
        if Path(export_path).exists():
            Path(export_path).unlink()
            print("   Cleaned up test export file")
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("✅ MCP Server is ready for Cursor integration")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cursor_mcp_config():
    """Test Cursor MCP configuration"""
    print("\n🔧 Testing Cursor MCP Configuration")
    print("-" * 40)
    
    # Check if .cursor/mcp.json exists
    cursor_config = Path(".cursor/mcp.json")
    if not cursor_config.exists():
        print("❌ Cursor MCP config not found at .cursor/mcp.json")
        return False
    
    try:
        with open(cursor_config, 'r') as f:
            config = json.load(f)
        
        # Validate config structure
        if "mcpServers" not in config:
            print("❌ Invalid config: missing 'mcpServers'")
            return False
        
        if "code-graph-mcp" not in config["mcpServers"]:
            print("❌ Invalid config: missing 'code-graph-mcp' server")
            return False
        
        server_config = config["mcpServers"]["code-graph-mcp"]
        
        # Check required fields
        required_fields = ["command", "args"]
        for field in required_fields:
            if field not in server_config:
                print(f"❌ Invalid config: missing '{field}' in server config")
                return False
        
        # Check if the server file exists
        server_file = Path(server_config["args"][0])
        if not server_file.exists():
            print(f"❌ Server file not found: {server_file}")
            return False
        
        print("✅ Cursor MCP configuration is valid")
        print(f"   Server file: {server_file}")
        print(f"   Command: {server_config['command']}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in Cursor config: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading Cursor config: {e}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n📦 Checking Dependencies")
    print("-" * 40)
    
    required_packages = [
        "mcp",
        "pydantic", 
        "networkx",
        "sqlalchemy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All required dependencies are installed")
    return True

def main():
    """Main test function"""
    print("🚀 Cursor MCP Server Integration Test")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependency check failed")
        return False
    
    # Test Cursor configuration
    if not test_cursor_mcp_config():
        print("\n❌ Cursor configuration test failed")
        return False
    
    # Test MCP server functionality
    result = asyncio.run(test_mcp_server())
    
    if result:
        print("\n🎯 NEXT STEPS:")
        print("1. Open Cursor IDE")
        print("2. Go to Settings → Features → Model Context Protocol")
        print("3. Verify 'code-graph-mcp' is listed and enabled")
        print("4. Test in chat: 'Use the MCP server to analyze test files'")
        print("\nReady for development! 🚀")
    else:
        print("\n❌ Tests failed. Check the errors above.")
        print("Refer to CURSOR_MCP_SETUP.md for troubleshooting.")
    
    return result

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 