#!/usr/bin/env python3
"""
Example usage of the AI Coding Agent with MCP Server

This script demonstrates how to:
1. Connect to the MCP server
2. Analyze an existing codebase
3. Find similar patterns
4. Generate new code based on patterns
"""

import asyncio
import json
from typing import Dict, List, Any

# This would typically be imported from the MCP client library
# For demonstration, we'll simulate the interactions

class MockMCPClient:
    """Mock MCP client for demonstration"""
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate MCP tool calls"""
        if tool_name == "analyze_codebase":
            return {
                "files_analyzed": 25,
                "relationships_found": 45,
                "patterns_identified": 12
            }
        elif tool_name == "find_similar_patterns":
            return [
                {
                    "pattern_id": "crud_pattern_1",
                    "pattern_type": "database_crud",
                    "files": ["Products.aspx", "Products.aspx.cs", "ProductManager.cs", "sp_GetProducts.sql"],
                    "template_data": {
                        "entity_name": "Product",
                        "table_name": "Products",
                        "primary_key": "ProductID",
                        "columns": ["ProductID", "ProductName", "CategoryID", "Price", "IsActive"],
                        "relationships": [
                            {"table": "Categories", "foreign_key": "CategoryID"}
                        ]
                    },
                    "similarity_score": 0.85
                }
            ]
        elif tool_name == "get_database_schema":
            return {
                "Customers": {
                    "table_name": "Customers",
                    "columns": [
                        {"name": "CustomerID", "type": "int", "nullable": "NO", "default": None},
                        {"name": "CustomerName", "type": "varchar", "nullable": "NO", "default": None},
                        {"name": "Email", "type": "varchar", "nullable": "YES", "default": None},
                        {"name": "IsActive", "type": "bit", "nullable": "NO", "default": "1"}
                    ],
                    "relationships": [],
                    "stored_procedures": ["sp_GetCustomers", "sp_SaveCustomer", "sp_DeleteCustomer"]
                }
            }

class AICodeGenerator:
    """AI-powered code generator using MCP server context"""
    
    def __init__(self, mcp_client: MockMCPClient):
        self.mcp_client = mcp_client
        
    async def generate_similar_feature(self, 
                                     description: str, 
                                     reference_pattern: str = None,
                                     entity_name: str = None) -> Dict[str, str]:
        """
        Generate a complete feature (database + backend + frontend) 
        based on similar existing patterns
        """
        
        print(f"🔍 Analyzing request: {description}")
        
        # Step 1: Find similar patterns
        patterns = await self.mcp_client.call_tool("find_similar_patterns", {
            "description": description,
            "pattern_type": "database_crud"
        })
        
        if not patterns:
            raise ValueError("No similar patterns found")
        
        best_pattern = patterns[0]  # Take the highest similarity score
        print(f"✅ Found similar pattern: {best_pattern['pattern_id']} (similarity: {best_pattern['similarity_score']})")
        
        # Step 2: Get database schema for context
        schema = await self.mcp_client.call_tool("get_database_schema", {
            "connection_string": "Server=localhost;Database=YourAppDB;Trusted_Connection=true;"
        })
        
        # Step 3: Generate code based on pattern
        generated_code = await self._generate_code_from_pattern(best_pattern, entity_name, schema)
        
        return generated_code
    
    async def _generate_code_from_pattern(self, 
                                        pattern: Dict[str, Any], 
                                        new_entity: str,
                                        schema: Dict[str, Any]) -> Dict[str, str]:
        """Generate code files based on the pattern template"""
        
        template_data = pattern["template_data"]
        original_entity = template_data["entity_name"]
        
        # Create mapping for template substitution
        substitutions = {
            "Entity": new_entity,
            "entity": new_entity.lower(),
            "TableName": f"{new_entity}s",
            "EntityID": f"{new_entity}ID"
        }
        
        generated_files = {}
        
        # Generate SQL stored procedure
        generated_files["stored_procedure"] = self._generate_stored_procedure(substitutions, schema)
        
        # Generate Manager class
        generated_files["manager_class"] = self._generate_manager_class(substitutions)
        
        # Generate ASPX page
        generated_files["aspx_page"] = self._generate_aspx_page(substitutions)
        
        # Generate Code-behind
        generated_files["codebehind"] = self._generate_codebehind(substitutions)
        
        return generated_files
    
    def _generate_stored_procedure(self, substitutions: Dict[str, str], schema: Dict[str, Any]) -> str:
        """Generate SQL stored procedure"""
        return f"""-- Generated stored procedure for {substitutions['Entity']} management
CREATE PROCEDURE sp_Get{substitutions['Entity']}List
    @{substitutions['EntityID']} INT = NULL,
    @IsActive BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        SELECT 
            {substitutions['EntityID']},
            {substitutions['Entity']}Name,
            CreatedDate,
            IsActive
        FROM {substitutions['TableName']}
        WHERE (@{substitutions['EntityID']} IS NULL OR {substitutions['EntityID']} = @{substitutions['EntityID']})
        AND IsActive = @IsActive
        ORDER BY {substitutions['Entity']}Name
        
        RETURN 0
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE()
        RAISERROR(@ErrorMessage, 16, 1)
        RETURN -1
    END CATCH
END

-- Save procedure
CREATE PROCEDURE sp_Save{substitutions['Entity']}
    @{substitutions['EntityID']} INT = NULL,
    @{substitutions['Entity']}Name NVARCHAR(255),
    @IsActive BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        IF @{substitutions['EntityID']} IS NULL
        BEGIN
            -- Insert new record
            INSERT INTO {substitutions['TableName']} ({substitutions['Entity']}Name, IsActive, CreatedDate)
            VALUES (@{substitutions['Entity']}Name, @IsActive, GETDATE())
            
            SELECT SCOPE_IDENTITY() as {substitutions['EntityID']}
        END
        ELSE
        BEGIN
            -- Update existing record
            UPDATE {substitutions['TableName']}
            SET {substitutions['Entity']}Name = @{substitutions['Entity']}Name,
                IsActive = @IsActive,
                ModifiedDate = GETDATE()
            WHERE {substitutions['EntityID']} = @{substitutions['EntityID']}
            
            SELECT @{substitutions['EntityID']} as {substitutions['EntityID']}
        END
        
        RETURN 0
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE()
        RAISERROR(@ErrorMessage, 16, 1)
        RETURN -1
    END CATCH
END"""

    def _generate_manager_class(self, substitutions: Dict[str, str]) -> str:
        """Generate Manager class"""
        return f"""using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace YourApp.BusinessLogic
{{
    /// <summary>
    /// Manager class for {substitutions['Entity']} operations
    /// Generated by AI Coding Agent
    /// </summary>
    public class {substitutions['Entity']}Manager
    {{
        private readonly ILogger<{substitutions['Entity']}Manager> _logger;
        private readonly string _connectionString;
        
        public {substitutions['Entity']}Manager(ILogger<{substitutions['Entity']}Manager> logger, 
                                               IConfiguration configuration)
        {{
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            _connectionString = configuration.GetConnectionString("DefaultConnection");
        }}
        
        /// <summary>
        /// Get list of {substitutions['entity']}s
        /// </summary>
        /// <param name="{substitutions['entity']}Id">Optional {substitutions['entity']} ID filter</param>
        /// <param name="isActive">Filter by active status</param>
        /// <returns>List of {substitutions['entity']}s</returns>
        public async Task<List<{substitutions['Entity']}>> Get{substitutions['Entity']}ListAsync(int? {substitutions['entity']}Id = null, bool isActive = true)
        {{
            try
            {{
                var {substitutions['entity']}List = new List<{substitutions['Entity']}>();
                
                using (var connection = new SqlConnection(_connectionString))
                {{
                    using (var command = new SqlCommand("sp_Get{substitutions['Entity']}List", connection))
                    {{
                        command.CommandType = CommandType.StoredProcedure;
                        command.Parameters.Add("@{substitutions['EntityID']}", SqlDbType.Int).Value = {substitutions['entity']}Id ?? (object)DBNull.Value;
                        command.Parameters.Add("@IsActive", SqlDbType.Bit).Value = isActive;
                        
                        await connection.OpenAsync();
                        
                        using (var reader = await command.ExecuteReaderAsync())
                        {{
                            while (await reader.ReadAsync())
                            {{
                                var {substitutions['entity']} = new {substitutions['Entity']}
                                {{
                                    {substitutions['EntityID']} = reader.GetInt32("{substitutions['EntityID']}"),
                                    {substitutions['Entity']}Name = reader.GetString("{substitutions['Entity']}Name"),
                                    CreatedDate = reader.GetDateTime("CreatedDate"),
                                    IsActive = reader.GetBoolean("IsActive")
                                }};
                                
                                {substitutions['entity']}List.Add({substitutions['entity']});
                            }}
                        }}
                    }}
                }}
                
                _logger.LogInformation($"Retrieved {{count}} {substitutions['entity']}s", {substitutions['entity']}List.Count);
                return {substitutions['entity']}List;
            }}
            catch (Exception ex)
            {{
                _logger.LogError(ex, "Error retrieving {substitutions['entity']} list");
                throw;
            }}
        }}
        
        /// <summary>
        /// Save {substitutions['entity']} (insert or update)
        /// </summary>
        /// <param name="{substitutions['entity']}">The {substitutions['entity']} to save</param>
        /// <returns>The saved {substitutions['entity']} with updated ID</returns>
        public async Task<{substitutions['Entity']}> Save{substitutions['Entity']}Async({substitutions['Entity']} {substitutions['entity']})
        {{
            if ({substitutions['entity']} == null)
                throw new ArgumentNullException(nameof({substitutions['entity']}));
                
            try
            {{
                using (var connection = new SqlConnection(_connectionString))
                {{
                    using (var command = new SqlCommand("sp_Save{substitutions['Entity']}", connection))
                    {{
                        command.CommandType = CommandType.StoredProcedure;
                        command.Parameters.Add("@{substitutions['EntityID']}", SqlDbType.Int).Value = 
                            {substitutions['entity']}.{substitutions['EntityID']} == 0 ? (object)DBNull.Value : {substitutions['entity']}.{substitutions['EntityID']};
                        command.Parameters.Add("@{substitutions['Entity']}Name", SqlDbType.NVarChar, 255).Value = {substitutions['entity']}.{substitutions['Entity']}Name;
                        command.Parameters.Add("@IsActive", SqlDbType.Bit).Value = {substitutions['entity']}.IsActive;
                        
                        await connection.OpenAsync();
                        var result = await command.ExecuteScalarAsync();
                        
                        {substitutions['entity']}.{substitutions['EntityID']} = Convert.ToInt32(result);
                    }}
                }}
                
                _logger.LogInformation("Saved {substitutions['entity']} with ID: {{{substitutions['EntityID']}}}", {substitutions['entity']}.{substitutions['EntityID']});
                return {substitutions['entity']};
            }}
            catch (Exception ex)
            {{
                _logger.LogError(ex, "Error saving {substitutions['entity']}");
                throw;
            }}
        }}
    }}
    
    /// <summary>
    /// {substitutions['Entity']} data model
    /// </summary>
    public class {substitutions['Entity']}
    {{
        public int {substitutions['EntityID']} {{ get; set; }}
        public string {substitutions['Entity']}Name {{ get; set; }}
        public DateTime CreatedDate {{ get; set; }}
        public DateTime? ModifiedDate {{ get; set; }}
        public bool IsActive {{ get; set; }}
    }}
}}"""

    def _generate_aspx_page(self, substitutions: Dict[str, str]) -> str:
        """Generate ASPX page"""
        return f"""<%@ Page Title="{substitutions['Entity']} Management" Language="C#" MasterPageFile="~/Site.Master" 
    AutoEventWireup="true" CodeBehind="{substitutions['Entity']}.aspx.cs" 
    Inherits="YourApp.Web.{substitutions['Entity']}Page" %>

<asp:Content ID="Content1" ContentPlaceHolderID="MainContent" runat="server">
    <div class="container-fluid">
        <div class="row">
            <div class="col-md-12">
                <h2><i class="fas fa-list"></i> {substitutions['Entity']} Management</h2>
                <p class="text-muted">Manage your {substitutions['entity']}s efficiently</p>
                
                <!-- Action Buttons -->
                <div class="mb-3">
                    <asp:Button ID="btnAdd{substitutions['Entity']}" runat="server" 
                        Text="Add New {substitutions['Entity']}" 
                        CssClass="btn btn-primary"
                        OnClick="btnAdd{substitutions['Entity']}_Click" />
                    <asp:Button ID="btnRefresh" runat="server" 
                        Text="Refresh" 
                        CssClass="btn btn-secondary ml-2"
                        OnClick="btnRefresh_Click" />
                </div>
                
                <!-- Search Panel -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5 class="mb-0">Search & Filter</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <label for="txt{substitutions['Entity']}Name">Search by Name:</label>
                                <asp:TextBox ID="txt{substitutions['Entity']}Name" runat="server" 
                                    CssClass="form-control" 
                                    placeholder="Enter {substitutions['entity']} name..."></asp:TextBox>
                            </div>
                            <div class="col-md-3">
                                <label for="ddlActiveStatus">Status:</label>
                                <asp:DropDownList ID="ddlActiveStatus" runat="server" CssClass="form-control">
                                    <asp:ListItem Text="All" Value=""></asp:ListItem>
                                    <asp:ListItem Text="Active" Value="true" Selected="true"></asp:ListItem>
                                    <asp:ListItem Text="Inactive" Value="false"></asp:ListItem>
                                </asp:DropDownList>
                            </div>
                            <div class="col-md-3">
                                <label>&nbsp;</label>
                                <div>
                                    <asp:Button ID="btnSearch" runat="server" 
                                        Text="Search" 
                                        CssClass="btn btn-info"
                                        OnClick="btnSearch_Click" />
                                    <asp:Button ID="btnClearSearch" runat="server" 
                                        Text="Clear" 
                                        CssClass="btn btn-outline-secondary ml-2"
                                        OnClick="btnClearSearch_Click" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Results Grid -->
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">{substitutions['Entity']} List</h5>
                    </div>
                    <div class="card-body">
                        <asp:GridView ID="gv{substitutions['Entity']}" runat="server" 
                            CssClass="table table-striped table-hover table-bordered"
                            AutoGenerateColumns="false"
                            AllowPaging="true"
                            PageSize="20"
                            OnPageIndexChanging="gv{substitutions['Entity']}_PageIndexChanging"
                            OnRowCommand="gv{substitutions['Entity']}_RowCommand"
                            OnRowDataBound="gv{substitutions['Entity']}_RowDataBound"
                            EmptyDataText="No {substitutions['entity']}s found.">
                            
                            <HeaderStyle CssClass="table-dark" />
                            <PagerStyle CssClass="pagination-wrapper" />
                            
                            <Columns>
                                <asp:BoundField DataField="{substitutions['EntityID']}" 
                                    HeaderText="ID" 
                                    ItemStyle-Width="80px" 
                                    ItemStyle-CssClass="text-center" />
                                    
                                <asp:BoundField DataField="{substitutions['Entity']}Name" 
                                    HeaderText="{substitutions['Entity']} Name" 
                                    ItemStyle-Width="200px" />
                                    
                                <asp:BoundField DataField="CreatedDate" 
                                    HeaderText="Created Date" 
                                    DataFormatString="{{0:MM/dd/yyyy}}"
                                    ItemStyle-Width="120px"
                                    ItemStyle-CssClass="text-center" />
                                    
                                <asp:TemplateField HeaderText="Status" ItemStyle-Width="100px" ItemStyle-CssClass="text-center">
                                    <ItemTemplate>
                                        <span class='<%# (bool)Eval("IsActive") ? "badge badge-success" : "badge badge-secondary" %>'>
                                            <%# (bool)Eval("IsActive") ? "Active" : "Inactive" %>
                                        </span>
                                    </ItemTemplate>
                                </asp:TemplateField>
                                
                                <asp:TemplateField HeaderText="Actions" ItemStyle-Width="150px" ItemStyle-CssClass="text-center">
                                    <ItemTemplate>
                                        <asp:LinkButton ID="lnkEdit" runat="server" 
                                            CommandName="EditRecord" 
                                            CommandArgument='<%# Eval("{substitutions['EntityID']}") %>'
                                            CssClass="btn btn-sm btn-outline-primary mr-1"
                                            ToolTip="Edit {substitutions['Entity']}">
                                            <i class="fas fa-edit"></i>
                                        </asp:LinkButton>
                                        
                                        <asp:LinkButton ID="lnkDelete" runat="server" 
                                            CommandName="DeleteRecord" 
                                            CommandArgument='<%# Eval("{substitutions['EntityID']}") %>'
                                            CssClass="btn btn-sm btn-outline-danger"
                                            ToolTip="Delete {substitutions['Entity']}"
                                            OnClientClick="return confirm('Are you sure you want to delete this {substitutions['entity']}?');">
                                            <i class="fas fa-trash"></i>
                                        </asp:LinkButton>
                                    </ItemTemplate>
                                </asp:TemplateField>
                            </Columns>
                        </asp:GridView>
                    </div>
                </div>
                
                <!-- Status Messages -->
                <asp:Panel ID="pnlMessage" runat="server" Visible="false" CssClass="mt-3">
                    <asp:Label ID="lblMessage" runat="server" CssClass="alert"></asp:Label>
                </asp:Panel>
            </div>
        </div>
    </div>
</asp:Content>"""

    def _generate_codebehind(self, substitutions: Dict[str, str]) -> str:
        """Generate code-behind file"""
        return f"""using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using Microsoft.Extensions.Logging;
using YourApp.BusinessLogic;

namespace YourApp.Web
{{
    /// <summary>
    /// {substitutions['Entity']} management page
    /// Generated by AI Coding Agent
    /// </summary>
    public partial class {substitutions['Entity']}Page : System.Web.UI.Page
    {{
        private readonly {substitutions['Entity']}Manager _{substitutions['entity']}Manager;
        private readonly ILogger<{substitutions['Entity']}Page> _logger;
        
        public {substitutions['Entity']}Page()
        {{
            // Dependency injection would be handled by your DI container
            // This is a simplified example
        }}
        
        protected async void Page_Load(object sender, EventArgs e)
        {{
            if (!IsPostBack)
            {{
                await Load{substitutions['Entity']}DataAsync();
            }}
        }}
        
        /// <summary>
        /// Load {substitutions['entity']} data into the grid
        /// </summary>
        private async Task Load{substitutions['Entity']}DataAsync()
        {{
            try
            {{
                // Get filter parameters
                string searchName = txt{substitutions['Entity']}Name.Text.Trim();
                bool? isActive = null;
                
                if (!string.IsNullOrEmpty(ddlActiveStatus.SelectedValue))
                {{
                    isActive = Convert.ToBoolean(ddlActiveStatus.SelectedValue);
                }}
                
                // Load data from manager
                var {substitutions['entity']}List = await _{substitutions['entity']}Manager.Get{substitutions['Entity']}ListAsync(null, isActive ?? true);
                
                // Apply search filter if provided
                if (!string.IsNullOrEmpty(searchName))
                {{
                    {substitutions['entity']}List = {substitutions['entity']}List
                        .Where(x => x.{substitutions['Entity']}Name.ToLower().Contains(searchName.ToLower()))
                        .ToList();
                }}
                
                // Bind to grid
                gv{substitutions['Entity']}.DataSource = {substitutions['entity']}List;
                gv{substitutions['Entity']}.DataBind();
                
                ShowMessage($"Loaded {{{substitutions['entity']}List.Count}} {substitutions['entity']}(s)", "success");
            }}
            catch (Exception ex)
            {{
                _logger?.LogError(ex, "Error loading {substitutions['entity']} data");
                ShowMessage("Error loading data. Please try again.", "danger");
            }}
        }}
        
        protected async void btnAdd{substitutions['Entity']}_Click(object sender, EventArgs e)
        {{
            // Redirect to add/edit page
            Response.Redirect($"~/Edit{substitutions['Entity']}.aspx");
        }}
        
        protected async void btnRefresh_Click(object sender, EventArgs e)
        {{
            await Load{substitutions['Entity']}DataAsync();
        }}
        
        protected async void btnSearch_Click(object sender, EventArgs e)
        {{
            await Load{substitutions['Entity']}DataAsync();
        }}
        
        protected void btnClearSearch_Click(object sender, EventArgs e)
        {{
            txt{substitutions['Entity']}Name.Text = "";
            ddlActiveStatus.SelectedValue = "true";
            // Reload data will happen on next postback
        }}
        
        protected async void gv{substitutions['Entity']}_PageIndexChanging(object sender, GridViewPageEventArgs e)
        {{
            gv{substitutions['Entity']}.PageIndex = e.NewPageIndex;
            await Load{substitutions['Entity']}DataAsync();
        }}
        
        protected async void gv{substitutions['Entity']}_RowCommand(object sender, GridViewCommandEventArgs e)
        {{
            if (e.CommandName == "EditRecord")
            {{
                int {substitutions['entity']}Id = Convert.ToInt32(e.CommandArgument);
                Response.Redirect($"~/Edit{substitutions['Entity']}.aspx?id={{{substitutions['entity']}Id}}");
            }}
            else if (e.CommandName == "DeleteRecord")
            {{
                int {substitutions['entity']}Id = Convert.ToInt32(e.CommandArgument);
                await Delete{substitutions['Entity']}Async({substitutions['entity']}Id);
            }}
        }}
        
        protected void gv{substitutions['Entity']}_RowDataBound(object sender, GridViewRowEventArgs e)
        {{
            if (e.Row.RowType == DataControlRowType.DataRow)
            {{
                // Add any custom row formatting here
                var {substitutions['entity']} = ({substitutions['Entity']})e.Row.DataItem;
                
                if (!{substitutions['entity']}.IsActive)
                {{
                    e.Row.CssClass += " table-secondary";
                }}
            }}
        }}
        
        /// <summary>
        /// Delete a {substitutions['entity']}
        /// </summary>
        /// <param name="{substitutions['entity']}Id">ID of the {substitutions['entity']} to delete</param>
        private async Task Delete{substitutions['Entity']}Async(int {substitutions['entity']}Id)
        {{
            try
            {{
                // For this example, we'll just mark as inactive
                // You might want to implement a proper delete method
                var {substitutions['entity']}List = await _{substitutions['entity']}Manager.Get{substitutions['Entity']}ListAsync({substitutions['entity']}Id);
                var {substitutions['entity']} = {substitutions['entity']}List.FirstOrDefault();
                
                if ({substitutions['entity']} != null)
                {{
                    {substitutions['entity']}.IsActive = false;
                    await _{substitutions['entity']}Manager.Save{substitutions['Entity']}Async({substitutions['entity']});
                    
                    ShowMessage("{substitutions['Entity']} deleted successfully", "success");
                    await Load{substitutions['Entity']}DataAsync();
                }}
                else
                {{
                    ShowMessage("{substitutions['Entity']} not found", "warning");
                }}
            }}
            catch (Exception ex)
            {{
                _logger?.LogError(ex, "Error deleting {substitutions['entity']} with ID: {{{substitutions['entity']}Id}}", {substitutions['entity']}Id);
                ShowMessage("Error deleting {substitutions['entity']}. Please try again.", "danger");
            }}
        }}
        
        /// <summary>
        /// Show a message to the user
        /// </summary>
        /// <param name="message">Message to display</param>
        /// <param name="type">Message type (success, danger, warning, info)</param>
        private void ShowMessage(string message, string type)
        {{
            lblMessage.Text = message;
            lblMessage.CssClass = $"alert alert-{{type}} alert-dismissible fade show";
            pnlMessage.Visible = true;
        }}
    }}
}}"""

async def main():
    """Demonstrate the AI coding agent workflow"""
    
    print("🚀 AI Coding Agent Demo")
    print("=" * 50)
    
    # Initialize MCP client (mock for demo)
    mcp_client = MockMCPClient()
    
    # Initialize AI code generator
    code_generator = AICodeGenerator(mcp_client)
    
    # Example 1: Generate customer management based on product management
    print("\\n📋 Example 1: Generate Customer Management System")
    print("-" * 50)
    
    try:
        generated_code = await code_generator.generate_similar_feature(
            description="Create a customer management page similar to the product management page, but for tracking customers with contact information",
            entity_name="Customer"
        )
        
        print("✅ Generated code files:")
        for file_type, code in generated_code.items():
            print(f"  📄 {file_type}: {len(code)} characters")
        
        # You could save these files to disk here
        # for file_type, code in generated_code.items():
        #     filename = f"generated_{file_type}.txt"
        #     with open(filename, 'w') as f:
        #         f.write(code)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\\n🎯 Next Steps:")
    print("1. Set up your actual MCP server")
    print("2. Analyze your existing codebase")
    print("3. Configure database connections")
    print("4. Integrate with Cursor AI")
    print("5. Start generating code!")

if __name__ == "__main__":
    asyncio.run(main()) 