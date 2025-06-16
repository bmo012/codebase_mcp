# Cursor MCP Server Setup Guide

This guide will help you set up and use the Code Graph MCP server with Cursor IDE for enhanced C# ASP.NET development.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Cursor IDE** with MCP support enabled
3. **Required Python packages** (will be installed via setup)

## Setup Steps

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_CONNECTION_STRING=Server=localhost;Database=YourAppDB;Trusted_Connection=true;

# AI Model Configuration (Optional)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### 3. Configure Cursor MCP

The MCP server is configured in `.cursor/mcp.json`:

```json
{
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
```

### 4. Verify Installation

1. Open Cursor IDE
2. Go to Settings → Features → Model Context Protocol
3. You should see "code-graph-mcp" listed as an available server
4. Make sure it's enabled

## Available MCP Tools

### 1. analyze_specific_files
Analyzes specific files to build a detailed code graph.

**Usage in Cursor Chat:**
```
Please analyze these files using the MCP server:
- /path/to/CustomerManager.cs
- /path/to/CustomerManagement.aspx
- /path/to/CustomerManagement.aspx.cs
```

### 2. find_patterns_by_type
Finds code patterns by type (database_crud, aspx_page, business_logic).

**Usage in Cursor Chat:**
```
Find all database CRUD patterns using the MCP server
```

### 3. get_node_types_summary
Gets a summary of all node types in the code graph.

**Usage in Cursor Chat:**
```
Show me a summary of all code elements using the MCP server
```

### 4. get_relationship_types_summary
Gets a summary of all relationship types between code elements.

**Usage in Cursor Chat:**
```
Show me how code elements are connected using the MCP server
```

### 5. export_graph_data
Exports the complete graph data for visualization.

**Usage in Cursor Chat:**
```
Export the code graph data for visualization
```

## How to Use with Cursor

### Step 1: Analyze Your Codebase

Start by analyzing your existing code files:

```
I need to create a new Product Management feature similar to Customer Management. 
First, please analyze the existing customer management files using the MCP server to understand the pattern.
```

### Step 2: Request Code Generation

After analysis, request code generation:

```
Based on the pattern analysis from the MCP server, generate a complete Product Management system including:
1. Database stored procedures
2. ProductManager business logic class
3. ProductManagement.aspx.cs code-behind
4. ProductManagement.aspx frontend page

Follow the same pattern structure identified by the MCP server.
```

### Step 3: Verify Relationships

Use the MCP server to verify the generated code follows proper patterns:

```
Use the MCP server to analyze the generated Product Management files and verify they follow the same relationship patterns as the existing code.
```

## Example Workflow

### Creating a New Entity Management System

1. **Analyze Existing Pattern**
   ```
   Please use the MCP server to analyze these existing files and identify the pattern:
   - BusinessLogic/CustomerManager.cs
   - Web/CustomerManagement.aspx
   - Web/CustomerManagement.aspx.cs
   - Database/sp_CustomerProcedures.sql
   ```

2. **Request Code Generation**
   ```
   Based on the pattern analysis, generate a complete Order Management system following the same structure. Include all four layers: database procedures, business logic, code-behind, and frontend.
   ```

3. **Verify Generated Code**
   ```
   Use the MCP server to verify the generated Order Management files maintain the same relationships and patterns as the Customer Management system.
   ```

## Advanced Usage

### Pattern-Based Development

The MCP server recognizes these pattern types:
- `database_crud`: Database CRUD operations
- `aspx_page`: ASP.NET Web Forms pages
- `business_logic`: Business logic manager classes
- `api_endpoint`: API endpoint patterns
- `validation_logic`: Validation patterns

### Troubleshooting

#### MCP Server Not Found
1. Check that Python is in your PATH
2. Verify the file path in `.cursor/mcp.json`
3. Ensure all dependencies are installed

#### Tools Not Working
1. Check Cursor's MCP settings page
2. Verify the server is enabled
3. Look for error messages in Cursor's output panel

#### Analysis Fails
1. Ensure file paths are correct and accessible
2. Check file permissions
3. Verify files contain valid C#/ASPX/SQL code

### Best Practices

1. **Start Small**: Begin by analyzing a few related files
2. **Follow Patterns**: Always use the MCP server to identify patterns before generating code
3. **Verify Relationships**: Use the relationship analysis tools to ensure proper connections
4. **Maintain Consistency**: Follow the established naming conventions and patterns

## Integration with Cursor Rules

The `.cursorrules` file works together with the MCP server to:
- Provide context about your coding standards
- Define the expected patterns and structures
- Guide the AI in generating consistent code

## Next Steps

1. **Test the Setup**: Use the MCP server to analyze some existing files
2. **Generate Sample Code**: Create a simple management system to test the workflow
3. **Refine Patterns**: Adjust the pattern recognition based on your specific codebase
4. **Scale Up**: Use the system for larger code generation tasks

## Support

If you encounter issues:
1. Check the logs in `mcp_server.log`
2. Verify your configuration in `config.json`
3. Ensure all dependencies are properly installed
4. Review the Cursor MCP documentation for updates

The MCP server provides powerful pattern recognition and code generation capabilities that integrate seamlessly with Cursor's AI coding assistant. 