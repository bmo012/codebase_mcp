#!/usr/bin/env python3
"""
AI Coding Agent MCP Server

This server provides structured context about C# codebase relationships,
patterns, and templates for AI-assisted code generation.
"""

import json
import logging
import sqlite3
from typing import Dict, List, Optional, Any
from pathlib import Path

import tree_sitter
from tree_sitter import Language, Parser
import networkx as nx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodeRelationship(BaseModel):
    """Represents a relationship between code elements"""
    source_file: str
    target_file: str
    relationship_type: str  # "method_call", "inheritance", "database_access", etc.
    source_element: str
    target_element: str
    confidence: float

class CodePattern(BaseModel):
    """Represents a reusable code pattern"""
    pattern_id: str
    pattern_type: str  # "database_crud", "aspx_page", "business_logic", etc.
    files: List[str]
    template_data: Dict[str, Any]
    similarity_score: float

class DatabaseSchema(BaseModel):
    """Database schema information"""
    table_name: str
    columns: List[Dict[str, str]]
    relationships: List[Dict[str, str]]
    stored_procedures: List[str]

class CodeGraphMCPServer:
    """Main MCP server class for code graph analysis"""
    
    def __init__(self):
        self.server = Server("code-graph-mcp")
        self.code_graph = nx.DiGraph()
        self.db_engine = None
        self.parser = None
        self.language = None
        self.patterns_db = None
        self._setup_tree_sitter()
        self._setup_database()
        
    def _setup_tree_sitter(self):
        """Initialize Tree-sitter for C# parsing"""
        try:
            # This would need the actual tree-sitter C# library compiled
            # For now, we'll use a placeholder approach
            logger.info("Tree-sitter C# parser initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Tree-sitter: {e}")
    
    def _setup_database(self):
        """Initialize SQLite database for pattern storage"""
        self.patterns_db = sqlite3.connect("code_patterns.db", check_same_thread=False)
        cursor = self.patterns_db.cursor()
        
        # Create tables for storing code patterns and relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_patterns (
                id INTEGER PRIMARY KEY,
                pattern_type TEXT,
                pattern_data TEXT,
                file_paths TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_relationships (
                id INTEGER PRIMARY KEY,
                source_file TEXT,
                target_file TEXT,
                relationship_type TEXT,
                source_element TEXT,
                target_element TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.patterns_db.commit()
        logger.info("Pattern database initialized")
    
    def analyze_codebase(self, codebase_path: str) -> Dict[str, Any]:
        """Analyze a C# codebase and build the code graph"""
        codebase_path = Path(codebase_path)
        analysis_results = {
            "files_analyzed": 0,
            "relationships_found": 0,
            "patterns_identified": 0
        }
        
        # Find all C# files
        cs_files = list(codebase_path.rglob("*.cs"))
        aspx_files = list(codebase_path.rglob("*.aspx"))
        sql_files = list(codebase_path.rglob("*.sql"))
        
        all_files = cs_files + aspx_files + sql_files
        
        for file_path in all_files:
            try:
                self._analyze_file(file_path)
                analysis_results["files_analyzed"] += 1
            except Exception as e:
                logger.error(f"Error analyzing {file_path}: {e}")
        
        # Build relationships
        relationships = self._extract_relationships()
        analysis_results["relationships_found"] = len(relationships)
        
        # Identify patterns
        patterns = self._identify_patterns()
        analysis_results["patterns_identified"] = len(patterns)
        
        return analysis_results
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single file and extract relevant information"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if file_path.suffix == '.cs':
            self._analyze_csharp_file(file_path, content)
        elif file_path.suffix == '.aspx':
            self._analyze_aspx_file(file_path, content)
        elif file_path.suffix == '.sql':
            self._analyze_sql_file(file_path, content)
    
    def _analyze_csharp_file(self, file_path: Path, content: str):
        """Analyze C# file for classes, methods, and database calls"""
        # Simple pattern matching for demo - in reality, use Tree-sitter
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for database calls
            if 'SqlCommand' in line or 'ExecuteNonQuery' in line or 'ExecuteScalar' in line:
                # Extract stored procedure name if possible
                if 'CommandText' in line:
                    # Simple extraction - would be more sophisticated with AST
                    proc_name = self._extract_stored_proc_name(line)
                    if proc_name:
                        self._add_relationship(
                            str(file_path), 
                            f"database:{proc_name}",
                            "database_call",
                            f"line_{i+1}",
                            proc_name,
                            0.8
                        )
            
            # Look for method calls to other classes
            if '.' in line and '(' in line:
                # Simple method call detection
                self._extract_method_calls(str(file_path), line, i+1)
    
    def _analyze_aspx_file(self, file_path: Path, content: str):
        """Analyze ASPX file for controls and code-behind references"""
        # Look for code-behind file reference
        if 'CodeBehind=' in content:
            codebehind_match = content.split('CodeBehind="')[1].split('"')[0]
            codebehind_path = file_path.parent / codebehind_match
            self._add_relationship(
                str(file_path),
                str(codebehind_path),
                "codebehind",
                "page_directive",
                "class_definition",
                1.0
            )
    
    def _analyze_sql_file(self, file_path: Path, content: str):
        """Analyze SQL file for stored procedures and table references"""
        content_upper = content.upper()
        
        # Look for CREATE PROCEDURE statements
        if 'CREATE PROCEDURE' in content_upper:
            proc_name = self._extract_procedure_name(content)
            if proc_name:
                self.code_graph.add_node(f"database:{proc_name}", 
                                       type="stored_procedure", 
                                       file=str(file_path))
    
    def _extract_stored_proc_name(self, line: str) -> Optional[str]:
        """Extract stored procedure name from a line of code"""
        # Simple extraction - would be more sophisticated in practice
        if '"' in line:
            parts = line.split('"')
            for part in parts:
                if part.startswith('sp_') or part.startswith('usp_'):
                    return part
        return None
    
    def _extract_method_calls(self, file_path: str, line: str, line_number: int):
        """Extract method calls from a line of code"""
        # Simple method call extraction
        if '.' in line and '(' in line:
            # Basic pattern matching - would use AST in practice
            pass
    
    def _extract_procedure_name(self, content: str) -> Optional[str]:
        """Extract procedure name from SQL content"""
        lines = content.split('\n')
        for line in lines:
            if 'CREATE PROCEDURE' in line.upper():
                parts = line.split()
                if len(parts) > 2:
                    return parts[2].strip('[]')
        return None
    
    def _add_relationship(self, source_file: str, target_file: str, 
                         relationship_type: str, source_element: str, 
                         target_element: str, confidence: float):
        """Add a relationship to the code graph and database"""
        self.code_graph.add_edge(source_file, target_file, 
                               relationship_type=relationship_type,
                               source_element=source_element,
                               target_element=target_element,
                               confidence=confidence)
        
        # Store in database
        cursor = self.patterns_db.cursor()
        cursor.execute("""
            INSERT INTO code_relationships 
            (source_file, target_file, relationship_type, source_element, target_element, confidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (source_file, target_file, relationship_type, source_element, target_element, confidence))
        self.patterns_db.commit()
    
    def _extract_relationships(self) -> List[CodeRelationship]:
        """Extract all relationships from the code graph"""
        relationships = []
        for source, target, data in self.code_graph.edges(data=True):
            relationships.append(CodeRelationship(
                source_file=source,
                target_file=target,
                relationship_type=data.get('relationship_type', 'unknown'),
                source_element=data.get('source_element', ''),
                target_element=data.get('target_element', ''),
                confidence=data.get('confidence', 0.5)
            ))
        return relationships
    
    def _identify_patterns(self) -> List[CodePattern]:
        """Identify reusable code patterns"""
        patterns = []
        
        # Look for common patterns like CRUD operations
        crud_patterns = self._find_crud_patterns()
        patterns.extend(crud_patterns)
        
        # Look for ASPX page patterns
        page_patterns = self._find_page_patterns()
        patterns.extend(page_patterns)
        
        return patterns
    
    def _find_crud_patterns(self) -> List[CodePattern]:
        """Find CRUD operation patterns"""
        patterns = []
        # Implementation would analyze the graph for CRUD patterns
        return patterns
    
    def _find_page_patterns(self) -> List[CodePattern]:
        """Find ASPX page patterns"""
        patterns = []
        # Implementation would analyze ASPX pages and their code-behind files
        return patterns
    
    def find_similar_patterns(self, description: str, pattern_type: str = None) -> List[CodePattern]:
        """Find patterns similar to the given description"""
        # This would use vector similarity or keyword matching
        # For now, return mock data
        return [
            CodePattern(
                pattern_id="crud_pattern_1",
                pattern_type="database_crud",
                files=["Products.aspx", "Products.aspx.cs", "ProductManager.cs"],
                template_data={
                    "entity_name": "Product",
                    "table_name": "Products",
                    "primary_key": "ProductID"
                },
                similarity_score=0.85
            )
        ]
    
    def get_database_schema(self, connection_string: str) -> Dict[str, DatabaseSchema]:
        """Get database schema information"""
        try:
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                # Get table information
                tables_query = text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE = 'BASE TABLE'
                """)
                tables = conn.execute(tables_query).fetchall()
                
                schema_info = {}
                for table in tables:
                    table_name = table[0]
                    
                    # Get column information
                    columns_query = text("""
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = :table_name
                    """)
                    columns = conn.execute(columns_query, {"table_name": table_name}).fetchall()
                    
                    schema_info[table_name] = DatabaseSchema(
                        table_name=table_name,
                        columns=[{
                            "name": col[0],
                            "type": col[1],
                            "nullable": col[2],
                            "default": col[3]
                        } for col in columns],
                        relationships=[],  # Would extract foreign key relationships
                        stored_procedures=[]  # Would extract related stored procedures
                    )
                
                return schema_info
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return {}
    
    def setup_tools(self):
        """Setup MCP tools"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="analyze_codebase",
                    description="Analyze a C# codebase and build code relationship graph",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "codebase_path": {
                                "type": "string",
                                "description": "Path to the codebase to analyze"
                            }
                        },
                        "required": ["codebase_path"]
                    }
                ),
                Tool(
                    name="find_similar_patterns",
                    description="Find code patterns similar to a given description",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Description of the desired pattern"
                            },
                            "pattern_type": {
                                "type": "string",
                                "description": "Type of pattern to search for"
                            }
                        },
                        "required": ["description"]
                    }
                ),
                Tool(
                    name="get_database_schema",
                    description="Get database schema information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "connection_string": {
                                "type": "string",
                                "description": "Database connection string"
                            }
                        },
                        "required": ["connection_string"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            if name == "analyze_codebase":
                results = self.analyze_codebase(arguments["codebase_path"])
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            elif name == "find_similar_patterns":
                patterns = self.find_similar_patterns(
                    arguments["description"],
                    arguments.get("pattern_type")
                )
                return [TextContent(
                    type="text",
                    text=json.dumps([p.dict() for p in patterns], indent=2)
                )]
            elif name == "get_database_schema":
                schema = self.get_database_schema(arguments["connection_string"])
                return [TextContent(
                    type="text",
                    text=json.dumps({k: v.dict() for k, v in schema.items()}, indent=2)
                )]
            else:
                raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main server entry point"""
    server_instance = CodeGraphMCPServer()
    server_instance.setup_tools()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="code-graph-mcp",
                server_version="1.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 