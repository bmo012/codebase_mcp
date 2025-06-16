# AI Coding Agent Implementation Guide

## Project Overview

The AI Coding Agent is a sophisticated system that analyzes C# ASP.NET codebases to understand relationships between code elements and generates similar code patterns based on existing implementations. It uses a Model Context Protocol (MCP) server to provide structured context about code relationships to AI models.

## Architecture Components

### 1. MCP Server (`mcp_server/`)
- **Purpose**: Analyzes codebase and provides structured context
- **Technology**: Python with MCP SDK, NetworkX for graph analysis
- **Key Features**:
  - AST parsing of C# files
  - Database schema introspection
  - Code relationship mapping
  - Pattern recognition and template extraction

### 2. Code Graph Database
- **Storage**: SQLite database (`enhanced_code_graph.db`)
- **Structure**: Nodes (code elements) and Relationships (connections)
- **Node Types**: Classes, Methods, Properties, Stored Procedures, ASPX Pages, etc.
- **Relationship Types**: Inheritance, Method Calls, Database Access, etc.

### 3. Configuration (`config.json`)
- Database connection strings
- AI model configurations (OpenAI/Anthropic)
- Analysis parameters and thresholds
- File type filters and exclusion patterns

## Setup Instructions

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd code_graph_mcp

# Run the setup script
python setup.py

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys and database connection
```

### 2. Configuration

Edit `config.json` to match your environment:

```json
{
  "database": {
    "connection_string": "Server=localhost;Database=YourAppDB;Trusted_Connection=true;",
    "timeout": 30
  },
  "ai_models": {
    "openai": {
      "api_key": "${OPENAI_API_KEY}",
      "model": "gpt-4"
    }
  },
  "code_analysis": {
    "supported_extensions": [".cs", ".aspx", ".sql"],
    "exclude_patterns": ["bin/", "obj/", "packages/"]
  }
}
```

### 3. Start the MCP Server

```bash
# Windows
run_server.bat

# Unix/Linux/Mac
./run_server.sh
```

## Code Graph Creation

### Direct File Path Analysis

The enhanced MCP server supports analyzing specific files directly:

```python
# Example: Analyze specific files
file_paths = [
    "C:/MyProject/BusinessLogic/CustomerManager.cs",
    "C:/MyProject/Web/CustomerManagement.aspx",
    "C:/MyProject/Web/CustomerManagement.aspx.cs",
    "C:/MyProject/Database/sp_CustomerProcedures.sql"
]

# Call the MCP server
results = await mcp_client.call_tool("analyze_specific_files", {
    "file_paths": file_paths
})
```

### Node Types

The system recognizes the following node types:

| Node Type | Description | Example |
|-----------|-------------|---------|
| `class` | C# class definitions | `CustomerManager` |
| `method` | Methods within classes | `GetCustomerListAsync` |
| `property` | Class properties | `CustomerID` |
| `stored_procedure` | SQL stored procedures | `sp_GetCustomerList` |
| `table` | Database tables | `Customers` |
| `aspx_page` | ASPX web pages | `CustomerManagement.aspx` |
| `aspx_control` | ASP.NET controls | `gvCustomers` |
| `namespace` | C# namespaces | `YourApp.BusinessLogic` |

### Relationship Types

The system tracks these relationship types:

| Relationship | Description | Example |
|--------------|-------------|---------|
| `database_access` | Method calls stored procedure | `CustomerManager.GetCustomerListAsync` → `sp_GetCustomerList` |
| `codebehind` | ASPX page links to code-behind | `CustomerManagement.aspx` → `CustomerManagement.aspx.cs` |
| `contains` | Parent-child relationships | `CustomerManager` contains `GetCustomerListAsync` |
| `method_call` | Method calling another method | `Page_Load` calls `LoadCustomerData` |
| `inheritance` | Class inheritance | `CustomerPage` inherits `Page` |

## Pattern Examples

### 1. Database Layer Pattern

```sql
-- File: examples/stored_procedure_example.sql
CREATE PROCEDURE sp_GetCustomerList
    @CustomerID INT = NULL,
    @IsActive BIT = 1,
    @SearchName NVARCHAR(255) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        SELECT CustomerID, CustomerName, Email, Phone, IsActive, CreatedDate
        FROM Customers
        WHERE (@CustomerID IS NULL OR CustomerID = @CustomerID)
          AND IsActive = @IsActive
          AND (@SearchName IS NULL OR CustomerName LIKE '%' + @SearchName + '%')
        ORDER BY CustomerName
        
        RETURN 0
    END TRY
    BEGIN CATCH
        RETURN -1
    END CATCH
END
```

### 2. Business Logic Pattern

```csharp
// File: examples/business_logic_example.cs
public class CustomerManager
{
    private readonly ILogger<CustomerManager> _logger;
    private readonly string _connectionString;
    
    public CustomerManager(ILogger<CustomerManager> logger, IConfiguration configuration)
    {
        _logger = logger;
        _connectionString = configuration.GetConnectionString("DefaultConnection");
    }
    
    public async Task<List<Customer>> GetCustomerListAsync(int? customerId = null, bool isActive = true)
    {
        using (var connection = new SqlConnection(_connectionString))
        {
            using (var command = new SqlCommand("sp_GetCustomerList", connection))
            {
                command.CommandType = CommandType.StoredProcedure;
                command.Parameters.Add("@CustomerID", SqlDbType.Int).Value = customerId ?? (object)DBNull.Value;
                command.Parameters.Add("@IsActive", SqlDbType.Bit).Value = isActive;
                
                // ... database access logic
            }
        }
    }
}
```

### 3. Backend Page Pattern

```csharp
// File: examples/backend_codebehind_example.cs
public partial class CustomerManagement : System.Web.UI.Page
{
    private CustomerManager _customerManager;
    
    protected void Page_Load(object sender, EventArgs e)
    {
        if (!IsPostBack)
        {
            LoadCustomerData();
        }
    }
    
    protected void btnAddCustomer_Click(object sender, EventArgs e)
    {
        // Handle add customer button click
    }
    
    protected void gvCustomers_RowCommand(object sender, GridViewCommandEventArgs e)
    {
        if (e.CommandName == "EditCustomer")
        {
            int customerId = Convert.ToInt32(e.CommandArgument);
            EditCustomer(customerId);
        }
    }
}
```

### 4. Frontend ASPX Pattern

```aspx
<%-- File: examples/frontend_aspx_example.aspx --%>
<%@ Page Title="Customer Management" Language="C#" MasterPageFile="~/Site.Master" 
    CodeBehind="CustomerManagement.aspx.cs" Inherits="YourApp.Web.CustomerManagement" %>

<asp:Content ContentPlaceHolderID="MainContent" runat="server">
    <div class="container-fluid">
        <h2>Customer Management</h2>
        
        <asp:Button ID="btnAddCustomer" runat="server" 
            Text="Add New Customer" 
            CssClass="btn btn-primary"
            OnClick="btnAddCustomer_Click" />
        
        <asp:GridView ID="gvCustomers" runat="server" 
            CssClass="table table-striped"
            AutoGenerateColumns="false"
            OnRowCommand="gvCustomers_RowCommand">
            <Columns>
                <asp:BoundField DataField="CustomerName" HeaderText="Name" />
                <asp:BoundField DataField="Email" HeaderText="Email" />
                <asp:TemplateField HeaderText="Actions">
                    <ItemTemplate>
                        <asp:LinkButton CommandName="EditCustomer" 
                            CommandArgument='<%# Eval("CustomerID") %>'
                            Text="Edit" runat="server" />
                    </ItemTemplate>
                </asp:TemplateField>
            </Columns>
        </asp:GridView>
    </div>
</asp:Content>
```

## Using the MCP Server

### 1. Analyze Specific Files

```python
from mcp_client import MCPClient

client = MCPClient("localhost", 8000)

# Analyze your code files
result = await client.call_tool("analyze_specific_files", {
    "file_paths": [
        "/path/to/your/CustomerManager.cs",
        "/path/to/your/CustomerManagement.aspx",
        "/path/to/your/sp_Customers.sql"
    ]
})

print(f"Analysis complete: {result}")
```

### 2. Get Node Type Summary

```python
# Get summary of detected node types
summary = await client.call_tool("get_node_types_summary", {})
print(f"Node types found: {summary}")
```

### 3. Export Graph Data

```python
# Export graph for visualization
graph_data = await client.call_tool("export_graph_data", {
    "output_path": "my_code_graph.json"
})
```

## Cursor Integration

### 1. Configure Cursor IDE

Add to your Cursor settings (`cursor_mcp_config.json`):

```json
{
  "mcp": {
    "servers": {
      "code-graph-mcp": {
        "command": "python",
        "args": ["mcp_server/enhanced_code_graph_server.py"],
        "env": {
          "PYTHONPATH": "."
        }
      }
    }
  }
}
```

### 2. Use Custom Rules

The `.cursorrules` file provides AI context:

```
# When generating C# code:
1. Use established patterns from MCP server
2. Follow company naming conventions
3. Include proper error handling
4. Generate coordinated database/backend/frontend
5. Validate relationships and dependencies
```

## Code Generation Workflow

### 1. Pattern Recognition

The MCP server identifies patterns by:
- Grouping related files (e.g., `CustomerManager.cs`, `CustomerManagement.aspx`)
- Analyzing naming conventions (`sp_GetCustomers`, `SaveCustomer`, etc.)
- Tracking data flow between layers
- Recognizing CRUD operations

### 2. Template Extraction

For each pattern, the system extracts:
- **Entity Information**: Name, properties, relationships
- **Database Schema**: Tables, columns, stored procedures
- **UI Structure**: Controls, layout, validation
- **Business Rules**: Validation logic, error handling

### 3. Code Generation

When generating similar functionality:
1. **Find Similar Pattern**: Use semantic similarity to match requirements
2. **Extract Template**: Get the pattern structure and metadata
3. **Apply Substitutions**: Replace entity names, adjust business rules
4. **Generate Layers**: Create database → business logic → backend → frontend
5. **Validate Relationships**: Ensure proper connections between layers

## LLM Documentation Prompt

Use this prompt with your LLM to generate detailed documentation:

---

**PROMPT FOR LLM DOCUMENTATION GENERATION:**

```
You are a technical documentation expert. Analyze the following code pattern and create comprehensive documentation explaining how the system works.

**Code Pattern Analysis:**
- Database Layer: [SQL stored procedures with parameters, error handling, return codes]
- Business Logic Layer: [C# manager classes with dependency injection, logging, validation]
- Backend Layer: [ASP.NET code-behind with event handlers, data binding, user interaction]
- Frontend Layer: [ASPX pages with controls, styling, client-side validation]

**Generate Documentation That Includes:**

1. **System Architecture Overview**
   - How the layers interact
   - Data flow between components
   - Key design patterns used

2. **Component Analysis**
   - Purpose of each file/class/method
   - Input parameters and return values
   - Error handling strategies
   - Security considerations

3. **Data Flow Documentation**
   - User interaction → Backend → Business Logic → Database
   - Response path back to user
   - State management approach

4. **Code Relationships**
   - Method calls between layers
   - Database access patterns
   - Event handling mechanisms
   - Data binding strategies

5. **Business Logic Documentation**
   - Validation rules implemented
   - Error handling patterns
   - Logging and monitoring
   - Performance considerations

6. **User Interface Documentation**
   - Control hierarchy and purposes
   - User interaction flows
   - Validation feedback
   - Responsive design elements

7. **Database Integration**
   - Stored procedure purposes
   - Parameter usage patterns
   - Transaction handling
   - Error management

8. **Maintenance and Extension Guidelines**
   - How to add new functionality
   - Common modification patterns
   - Testing considerations
   - Deployment requirements

**Format the documentation as:**
- Clear section headers
- Code examples with explanations
- Bullet points for key concepts
- Diagrams (textual) showing relationships
- Best practices and recommendations

Please provide detailed, technical documentation that would help a developer understand and maintain this codebase effectively.
```

---

## Testing the Implementation

### 1. Basic Functionality Test

```python
# Test file analysis
python -c "
import asyncio
from mcp_server.enhanced_code_graph_server import EnhancedCodeGraphServer

async def test():
    server = EnhancedCodeGraphServer()
    result = server.analyze_specific_files(['examples/business_logic_example.cs'])
    print(f'Analysis result: {result}')

asyncio.run(test())
"
```

### 2. Graph Export Test

```python
# Test graph export
python -c "
from mcp_server.enhanced_code_graph_server import EnhancedCodeGraphServer

server = EnhancedCodeGraphServer()
server.analyze_specific_files(['examples/stored_procedure_example.sql'])
data = server.export_graph_data('test_graph.json')
print(f'Exported {len(data[\"nodes\"])} nodes')
"
```

## Troubleshooting

### Common Issues

1. **MCP Server Won't Start**
   - Check Python dependencies: `pip install -r requirements.txt`
   - Verify config.json syntax
   - Check port availability (default: 8000)

2. **File Analysis Fails**
   - Ensure file paths are correct and accessible
   - Check file encoding (UTF-8 expected)
   - Verify file permissions

3. **Database Connection Issues**
   - Validate connection string in config.json
   - Check database server availability
   - Verify authentication credentials

4. **Pattern Recognition Problems**
   - Ensure naming conventions are consistent
   - Check for required code patterns (Manager classes, sp_ procedures)
   - Verify file relationships are detectable

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. **Analyze Your Codebase**: Start with a small set of related files
2. **Review Generated Graph**: Use the export function to examine relationships
3. **Test Pattern Recognition**: Verify the system identifies your patterns correctly
4. **Integrate with Cursor**: Configure the MCP server connection
5. **Generate Similar Code**: Use the patterns to create new functionality

The next expected step is to run the setup script and configure the system with your specific codebase files and database connection details. 