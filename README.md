# AI Coding Agent with Code Graph MCP Server

## Project Overview
An AI coding agent that generates C# web applications (ASP.NET) by understanding code relationships through a Model Context Protocol (MCP) server. The agent creates coordinated database procedures, backend classes, and frontend pages based on existing patterns.

## Architecture

### 1. MCP Server (Model Context Protocol)
- **Purpose**: Provides structured context about code relationships
- **Technology**: Python/TypeScript with MCP SDK
- **Data Sources**: 
  - Code graph (file dependencies, API calls)
  - Database schema and relationships
  - Existing code patterns

### 2. Code Graph Builder
- **AST Analysis**: Parse C# files for method calls, dependencies
- **Database Mapping**: Link stored procedures to class methods
- **API Relationship Mapping**: Track frontend-backend connections
- **Pattern Recognition**: Identify reusable code templates

### 3. AI Agent
- **Technology**: OpenAI GPT-4/Claude with custom prompts
- **Context Window**: Enhanced with MCP server data
- **Generation Pipeline**: Database → Backend → Frontend
- **Validation**: Syntax checking and relationship verification

### 4. Cursor Integration
- **Custom Rules**: `.cursorrules` for C# ASP.NET patterns
- **MCP Integration**: Connect to local MCP server
- **Template Library**: Reusable component patterns

## Technology Stack

### Core Technologies
- **MCP Server**: Python with `mcp` library
- **Code Analysis**: Tree-sitter or Roslyn analyzers
- **Database**: SQL Server with schema introspection
- **AI Integration**: OpenAI API or Anthropic Claude
- **Frontend**: ASP.NET Web Forms (.aspx)
- **Backend**: C# (.aspx.cs, class libraries)

### Development Tools
- **Cursor AI**: Primary development environment
- **Custom MCP Server**: Local context provider
- **Graph Database**: Neo4j or SQLite for code relationships
- **Schema Tools**: SQL Server Management Objects (SMO)

## Implementation Phases

### Phase 1: MCP Server Foundation
1. Create MCP server with code graph capabilities
2. Implement AST parsing for C# files
3. Database schema introspection
4. Basic relationship mapping

### Phase 2: Code Pattern Recognition
1. Analyze existing codebase patterns
2. Create template extraction system
3. Build pattern similarity matching
4. Establish generation rules

### Phase 3: AI Agent Development
1. Custom prompt engineering for C# patterns
2. Multi-step generation pipeline
3. Context integration with MCP server
4. Validation and error handling

### Phase 4: Cursor Integration
1. MCP server connection setup
2. Custom `.cursorrules` configuration
3. Template library integration
4. Workflow optimization

## Key Features

### Code Generation Capabilities
- **Database Layer**: Stored procedures with proper parameters
- **Business Logic**: Class methods with dependency injection
- **Backend Pages**: ASP.NET code-behind files
- **Frontend**: ASPX pages with controls and styling
- **API Integration**: Proper error handling and validation

### Intelligence Features
- **Pattern Matching**: Find similar existing implementations
- **Relationship Awareness**: Understand data flow between layers
- **Business Rule Adaptation**: Modify logic while maintaining structure
- **Consistency Enforcement**: Naming conventions and coding standards

## Getting Started

### Prerequisites
- Visual Studio or VS Code with C# extension
- SQL Server (local or remote)
- Python 3.8+ for MCP server
- Node.js (if using TypeScript MCP server)
- Cursor AI (recommended)

### Installation
```bash
# Clone and setup MCP server
git clone <your-repo>
cd code_graph_mcp
pip install -r requirements.txt

# Setup database connection
# Configure connection strings in config.json

# Install MCP server locally
npm install -g @modelcontextprotocol/cli
```

## Example Usage

### Input: Business Requirements
```
Create a customer order management page similar to the product inventory page, 
but for tracking customer orders with approval workflow.
```

### Generated Output:
1. **Database**: `sp_GetCustomerOrders`, `sp_UpdateOrderStatus`
2. **Backend**: `CustomerOrderManager.cs`, `OrdersPage.aspx.cs`
3. **Frontend**: `Orders.aspx` with grid, filters, and approval buttons
4. **Integration**: Proper error handling, logging, and validation

## Benefits

### Development Speed
- **10x Faster**: Generate full-stack features in minutes
- **Consistency**: Maintain coding standards across team
- **Pattern Reuse**: Leverage existing successful implementations
- **Error Reduction**: Template-based generation reduces bugs

### Code Quality
- **Relationship Awareness**: Proper data flow and dependencies
- **Best Practices**: Built-in security and performance patterns
- **Documentation**: Auto-generated comments and documentation
- **Testing**: Template-based unit test generation

## Technical Deep Dive

### MCP Server Implementation
The MCP server acts as a bridge between your codebase knowledge and the AI agent:

```python
# Example MCP server endpoint
class CodeGraphMCP:
    def get_similar_patterns(self, description: str):
        # Find similar code patterns
        # Return context about relationships
        # Provide generation templates
        pass
    
    def get_database_schema(self, table_name: str):
        # Return table structure
        # Include relationships and constraints
        # Provide stored procedure templates
        pass
```

### Cursor Integration
Custom `.cursorrules` file provides context-aware assistance:

```
# C# ASP.NET Code Generation Rules
When generating C# code:
1. Use established patterns from MCP server
2. Follow company naming conventions
3. Include proper error handling
4. Generate coordinated database/backend/frontend
5. Validate relationships and dependencies
```

This approach combines the power of graph-based code understanding with AI generation capabilities, creating a sophisticated development acceleration tool. 