#!/usr/bin/env python3
"""
Quick Start Script for AI Coding Agent

This script demonstrates how to:
1. Set up the enhanced MCP server
2. Analyze code files directly
3. Export the code graph
4. View the analysis results
"""

import asyncio
import json
import os
from pathlib import Path

# Import the enhanced MCP server
from mcp_server.enhanced_code_graph_server import EnhancedCodeGraphServer

def print_banner():
    """Print a welcome banner"""
    print("=" * 60)
    print("🚀 AI Coding Agent - Quick Start Demo")
    print("=" * 60)

def print_section(title):
    """Print a section header"""
    print(f"\n📋 {title}")
    print("-" * 50)

async def demo_file_analysis():
    """Demonstrate file analysis capabilities"""
    print_banner()
    
    # Initialize the enhanced server
    print_section("Initializing Enhanced MCP Server")
    server = EnhancedCodeGraphServer()
    print("✅ Enhanced MCP Server initialized")
    
    # Get example files
    example_files = []
    examples_dir = Path("examples")
    
    if examples_dir.exists():
        for file_path in examples_dir.iterdir():
            if file_path.suffix in ['.cs', '.sql', '.aspx']:
                example_files.append(str(file_path))
                print(f"   📄 Found: {file_path}")
    
    if not example_files:
        print("⚠️  No example files found. Creating sample files...")
        create_sample_files()
        example_files = [
            "examples/stored_procedure_example.sql",
            "examples/business_logic_example.cs"
        ]
    
    # Analyze the files
    print_section("Analyzing Code Files")
    results = server.analyze_specific_files(example_files)
    
    print(f"✅ Analysis completed:")
    print(f"   Files analyzed: {results['files_analyzed']}")
    print(f"   Nodes created: {results['nodes_created']}")
    print(f"   Errors: {len(results['errors'])}")
    
    if results['errors']:
        print("   Errors encountered:")
        for error in results['errors']:
            print(f"     ❌ {error}")
    
    # Get node type summary
    print_section("Node Types Summary")
    node_types = server.get_node_types_summary()
    
    if node_types:
        print("📊 Detected node types:")
        for node_type, count in node_types.items():
            print(f"   {node_type}: {count} nodes")
    else:
        print("   No nodes detected")
    
    # Export graph data
    print_section("Exporting Graph Data")
    graph_data = server.export_graph_data("quick_start_graph.json")
    
    print(f"✅ Graph exported to: quick_start_graph.json")
    print(f"   Total nodes: {len(graph_data['nodes'])}")
    
    # Display sample nodes
    if graph_data['nodes']:
        print("\n🔍 Sample nodes detected:")
        for i, node in enumerate(graph_data['nodes'][:5]):  # Show first 5 nodes
            print(f"   {i+1}. {node['type']}: {node['name']} (Line {node['line_number']})")
        
        if len(graph_data['nodes']) > 5:
            print(f"   ... and {len(graph_data['nodes']) - 5} more nodes")
    
    return graph_data

def create_sample_files():
    """Create sample files if examples don't exist"""
    os.makedirs("examples", exist_ok=True)
    
    # Simple SQL example
    sql_content = """-- Sample stored procedure
CREATE PROCEDURE sp_GetCustomers
    @CustomerID INT = NULL
AS
BEGIN
    SELECT CustomerID, CustomerName, Email
    FROM Customers
    WHERE (@CustomerID IS NULL OR CustomerID = @CustomerID)
END"""
    
    with open("examples/sample_procedure.sql", "w") as f:
        f.write(sql_content)
    
    # Simple C# example
    cs_content = """using System;
using System.Collections.Generic;

namespace YourApp.BusinessLogic
{
    public class CustomerManager
    {
        public List<Customer> GetCustomers()
        {
            // Business logic here
            return new List<Customer>();
        }
    }
    
    public class Customer
    {
        public int CustomerID { get; set; }
        public string CustomerName { get; set; }
    }
}"""
    
    with open("examples/sample_manager.cs", "w") as f:
        f.write(cs_content)

def print_usage_instructions():
    """Print instructions for using the system"""
    print_section("Next Steps")
    print("🎯 To use this system with your own code:")
    print()
    print("1. Configure your environment:")
    print("   - Copy .env.example to .env")
    print("   - Add your API keys and database connection")
    print()
    print("2. Analyze your own files:")
    print("   ```python")
    print("   file_paths = [")
    print("       'path/to/your/BusinessLogic/Manager.cs',")
    print("       'path/to/your/Database/procedures.sql',")
    print("       'path/to/your/Web/Page.aspx'")
    print("   ]")
    print("   results = server.analyze_specific_files(file_paths)")
    print("   ```")
    print()
    print("3. Start the MCP server:")
    print("   - Windows: run_server.bat")
    print("   - Unix/Linux: ./run_server.sh")
    print()
    print("4. Configure Cursor IDE:")
    print("   - Add cursor_mcp_config.json to your Cursor settings")
    print("   - Use the .cursorrules for C# ASP.NET development")
    print()
    print("📚 See IMPLEMENTATION_GUIDE.md for detailed instructions")

async def main():
    """Main function"""
    try:
        # Run the demo
        graph_data = await demo_file_analysis()
        
        # Print usage instructions
        print_usage_instructions()
        
        # Final summary
        print_section("Demo Complete")
        print("✅ Quick start demo completed successfully!")
        print(f"📄 Graph data saved to: quick_start_graph.json")
        print("🔧 MCP server is ready for integration with Cursor IDE")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("Please check the setup and try again.")

if __name__ == "__main__":
    asyncio.run(main()) 