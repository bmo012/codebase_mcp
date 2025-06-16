#!/usr/bin/env python3
"""
Enhanced AI Coding Agent MCP Server with Direct File Path Support

This enhanced server provides improved code graph analysis with:
- Direct file path specification
- Detailed node typing for different code elements
- Better relationship extraction
- Pattern matching and template generation
"""

import json
import logging
import sqlite3
import re
from typing import Dict, List, Optional, Any, Set, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

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

class NodeType(Enum):
    """Types of nodes in the code graph"""
    CLASS = "class"
    METHOD = "method"
    PROPERTY = "property"
    FIELD = "field"
    STORED_PROCEDURE = "stored_procedure"
    TABLE = "table"
    ASPX_PAGE = "aspx_page"
    ASPX_CONTROL = "aspx_control"
    NAMESPACE = "namespace"
    INTERFACE = "interface"
    ENUM = "enum"
    CONSTANT = "constant"
    EVENT = "event"
    DELEGATE = "delegate"

class RelationshipType(Enum):
    """Types of relationships between code elements"""
    INHERITANCE = "inheritance"
    IMPLEMENTS = "implements"
    METHOD_CALL = "method_call"
    DATABASE_ACCESS = "database_access"
    PROPERTY_ACCESS = "property_access"
    CODEBEHIND = "codebehind"
    CONTAINS = "contains"
    REFERENCES = "references"
    USES = "uses"
    DEPENDS_ON = "depends_on"
    FOREIGN_KEY = "foreign_key"
    COMPOSITION = "composition"
    AGGREGATION = "aggregation"

@dataclass
class CodeNode:
    """Represents a node in the code graph"""
    id: str
    name: str
    node_type: NodeType
    file_path: str
    line_number: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "metadata": self.metadata
        }

@dataclass
class CodeRelationship:
    """Represents a relationship between code elements"""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    metadata: Dict[str, Any]
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relationship_type": self.relationship_type.value,
            "metadata": self.metadata,
            "confidence": self.confidence
        }

@dataclass
class CodePattern:
    """Represents a reusable code pattern"""
    pattern_id: str
    pattern_type: str
    files: List[str]
    nodes: List[CodeNode]
    relationships: List[CodeRelationship]
    template_data: Dict[str, Any]
    similarity_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "files": self.files,
            "nodes": [node.to_dict() for node in self.nodes],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "template_data": self.template_data,
            "similarity_score": self.similarity_score
        }

class EnhancedCodeGraphServer:
    """Enhanced MCP server for code graph analysis"""
    
    def __init__(self, config_path: str = "config.json"):
        self.server = Server("enhanced-code-graph-mcp")
        self.code_graph = nx.DiGraph()
        self.nodes: Dict[str, CodeNode] = {}
        self.relationships: List[CodeRelationship] = []
        self.patterns: List[CodePattern] = []
        self.config = self._load_config(config_path)
        self.db_connection = None
        self._setup_database()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                "code_analysis": {
                    "supported_extensions": [".cs", ".aspx", ".sql", ".js", ".css"],
                    "exclude_patterns": ["bin/", "obj/", "packages/", ".git/"],
                    "max_file_size_mb": 10
                },
                "pattern_matching": {
                    "similarity_threshold": 0.7,
                    "max_patterns_returned": 5
                }
            }
    
    def _setup_database(self):
        """Initialize SQLite database for storing analysis results"""
        self.db_connection = sqlite3.connect("enhanced_code_graph.db", check_same_thread=False)
        cursor = self.db_connection.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_nodes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                node_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line_number INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                metadata TEXT,
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES code_nodes (id),
                FOREIGN KEY (target_id) REFERENCES code_nodes (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                files TEXT NOT NULL,
                template_data TEXT,
                similarity_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.db_connection.commit()
        logger.info("Enhanced database initialized")
    
    def analyze_specific_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Analyze specific files and build code graph"""
        analysis_results = {
            "files_analyzed": 0,
            "nodes_created": 0,
            "relationships_found": 0,
            "patterns_identified": 0,
            "errors": []
        }
        
        for file_path in file_paths:
            try:
                path_obj = Path(file_path)
                if not path_obj.exists():
                    analysis_results["errors"].append(f"File not found: {file_path}")
                    continue
                
                nodes, relationships = self._analyze_file_detailed(path_obj)
                
                # Add nodes to graph
                for node in nodes:
                    self.nodes[node.id] = node
                    self.code_graph.add_node(node.id, **node.to_dict())
                    analysis_results["nodes_created"] += 1
                
                # Add relationships to graph
                for rel in relationships:
                    self.relationships.append(rel)
                    self.code_graph.add_edge(rel.source_id, rel.target_id, **rel.to_dict())
                    analysis_results["relationships_found"] += 1
                
                analysis_results["files_analyzed"] += 1
                
            except Exception as e:
                error_msg = f"Error analyzing {file_path}: {str(e)}"
                logger.error(error_msg)
                analysis_results["errors"].append(error_msg)
        
        # Save to database
        self._save_analysis_to_db()
        
        # Identify patterns
        patterns = self._identify_patterns()
        analysis_results["patterns_identified"] = len(patterns)
        
        return analysis_results
    
    def _analyze_file_detailed(self, file_path: Path) -> Tuple[List[CodeNode], List[CodeRelationship]]:
        """Detailed analysis of a single file"""
        nodes = []
        relationships = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            logger.warning(f"Could not read file {file_path} with UTF-8 encoding")
            return nodes, relationships
        
        if file_path.suffix == '.cs':
            nodes, relationships = self._analyze_csharp_detailed(file_path, content)
        elif file_path.suffix == '.aspx':
            nodes, relationships = self._analyze_aspx_detailed(file_path, content)
        elif file_path.suffix == '.sql':
            nodes, relationships = self._analyze_sql_detailed(file_path, content)
        
        return nodes, relationships
    
    def _analyze_csharp_detailed(self, file_path: Path, content: str) -> Tuple[List[CodeNode], List[CodeRelationship]]:
        """Detailed analysis of C# files"""
        nodes = []
        relationships = []
        lines = content.split('\n')
        
        current_namespace = None
        current_class = None
        in_method = False
        brace_count = 0
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Count braces for scope tracking
            brace_count += line_stripped.count('{') - line_stripped.count('}')
            
            # Namespace detection
            namespace_match = re.match(r'namespace\s+([a-zA-Z0-9_.]+)', line_stripped)
            if namespace_match:
                namespace_name = namespace_match.group(1)
                current_namespace = namespace_name
                node_id = f"{file_path}:namespace:{namespace_name}"
                nodes.append(CodeNode(
                    id=node_id,
                    name=namespace_name,
                    node_type=NodeType.NAMESPACE,
                    file_path=str(file_path),
                    line_number=line_num,
                    metadata={"scope": "namespace"}
                ))
            
            # Class detection
            class_match = re.match(r'(?:public|private|protected|internal)?\s*(?:partial\s+)?(?:static\s+)?class\s+([a-zA-Z0-9_]+)', line_stripped)
            if class_match:
                class_name = class_match.group(1)
                current_class = class_name
                node_id = f"{file_path}:class:{class_name}"
                nodes.append(CodeNode(
                    id=node_id,
                    name=class_name,
                    node_type=NodeType.CLASS,
                    file_path=str(file_path),
                    line_number=line_num,
                    metadata={
                        "namespace": current_namespace,
                        "access_modifier": self._extract_access_modifier(line_stripped)
                    }
                ))
                
                # Add namespace-class relationship
                if current_namespace:
                    relationships.append(CodeRelationship(
                        source_id=f"{file_path}:namespace:{current_namespace}",
                        target_id=node_id,
                        relationship_type=RelationshipType.CONTAINS,
                        metadata={"scope": "namespace_contains_class"}
                    ))
            
            # Method detection
            method_match = re.match(r'(?:public|private|protected|internal)?\s*(?:static\s+)?(?:async\s+)?(?:override\s+)?(?:virtual\s+)?[a-zA-Z0-9_<>\[\]]+\s+([a-zA-Z0-9_]+)\s*\(', line_stripped)
            if method_match and current_class and not line_stripped.startswith('//'):
                method_name = method_match.group(1)
                node_id = f"{file_path}:method:{current_class}:{method_name}"
                nodes.append(CodeNode(
                    id=node_id,
                    name=method_name,
                    node_type=NodeType.METHOD,
                    file_path=str(file_path),
                    line_number=line_num,
                    metadata={
                        "class": current_class,
                        "access_modifier": self._extract_access_modifier(line_stripped),
                        "is_static": "static" in line_stripped,
                        "is_async": "async" in line_stripped
                    }
                ))
                
                # Add class-method relationship
                if current_class:
                    relationships.append(CodeRelationship(
                        source_id=f"{file_path}:class:{current_class}",
                        target_id=node_id,
                        relationship_type=RelationshipType.CONTAINS,
                        metadata={"scope": "class_contains_method"}
                    ))
            
            # Database access detection
            if any(keyword in line_stripped for keyword in ['SqlCommand', 'SqlConnection', 'ExecuteNonQuery', 'ExecuteScalar']):
                # Extract stored procedure calls
                proc_match = re.search(r'["\']([a-zA-Z0-9_]+)["\']', line_stripped)
                if proc_match and (proc_match.group(1).startswith('sp_') or proc_match.group(1).startswith('usp_')):
                    proc_name = proc_match.group(1)
                    proc_node_id = f"database:procedure:{proc_name}"
                    
                    # Create stored procedure node if not exists
                    if proc_node_id not in [n.id for n in nodes]:
                        nodes.append(CodeNode(
                            id=proc_node_id,
                            name=proc_name,
                            node_type=NodeType.STORED_PROCEDURE,
                            file_path="database",
                            line_number=0,
                            metadata={"database_object": True}
                        ))
                    
                    # Add database access relationship
                    if in_method and current_class:
                        source_id = f"{file_path}:method:{current_class}:*"  # Wildcard for any method
                        relationships.append(CodeRelationship(
                            source_id=source_id,
                            target_id=proc_node_id,
                            relationship_type=RelationshipType.DATABASE_ACCESS,
                            metadata={"line_number": line_num}
                        ))
        
        return nodes, relationships
    
    def _analyze_aspx_detailed(self, file_path: Path, content: str) -> Tuple[List[CodeNode], List[CodeRelationship]]:
        """Detailed analysis of ASPX files"""
        nodes = []
        relationships = []
        
        # Create ASPX page node
        page_name = file_path.stem
        page_node_id = f"{file_path}:page:{page_name}"
        nodes.append(CodeNode(
            id=page_node_id,
            name=page_name,
            node_type=NodeType.ASPX_PAGE,
            file_path=str(file_path),
            line_number=1,
            metadata={"page_type": "aspx"}
        ))
        
        # Extract codebehind reference
        codebehind_match = re.search(r'CodeBehind="([^"]+)"', content)
        if codebehind_match:
            codebehind_file = codebehind_match.group(1)
            codebehind_path = file_path.parent / codebehind_file
            
            relationships.append(CodeRelationship(
                source_id=page_node_id,
                target_id=f"{codebehind_path}:class:*",  # Wildcard for any class in codebehind
                relationship_type=RelationshipType.CODEBEHIND,
                metadata={"codebehind_file": str(codebehind_path)}
            ))
        
        # Extract controls
        control_patterns = [
            r'<asp:([a-zA-Z]+)\s+[^>]*ID="([^"]+)"',
            r'<asp:([a-zA-Z]+)\s+[^>]*id="([^"]+)"'
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in control_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    control_type = match.group(1)
                    control_id = match.group(2)
                    control_node_id = f"{file_path}:control:{control_id}"
                    
                    nodes.append(CodeNode(
                        id=control_node_id,
                        name=control_id,
                        node_type=NodeType.ASPX_CONTROL,
                        file_path=str(file_path),
                        line_number=line_num,
                        metadata={"control_type": control_type}
                    ))
                    
                    # Add page-control relationship
                    relationships.append(CodeRelationship(
                        source_id=page_node_id,
                        target_id=control_node_id,
                        relationship_type=RelationshipType.CONTAINS,
                        metadata={"scope": "page_contains_control"}
                    ))
        
        return nodes, relationships
    
    def _analyze_sql_detailed(self, file_path: Path, content: str) -> Tuple[List[CodeNode], List[CodeRelationship]]:
        """Detailed analysis of SQL files"""
        nodes = []
        relationships = []
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper().strip()
            
            # Stored procedure detection
            if line_upper.startswith('CREATE PROCEDURE'):
                proc_match = re.search(r'CREATE\s+PROCEDURE\s+([a-zA-Z0-9_\[\]]+)', line_upper)
                if proc_match:
                    proc_name = proc_match.group(1).strip('[]')
                    node_id = f"database:procedure:{proc_name}"
                    
                    nodes.append(CodeNode(
                        id=node_id,
                        name=proc_name,
                        node_type=NodeType.STORED_PROCEDURE,
                        file_path=str(file_path),
                        line_number=line_num,
                        metadata={"database_object": True}
                    ))
            
            # Table references
            table_patterns = [
                r'FROM\s+([a-zA-Z0-9_\[\]]+)',
                r'JOIN\s+([a-zA-Z0-9_\[\]]+)',
                r'UPDATE\s+([a-zA-Z0-9_\[\]]+)',
                r'INSERT\s+INTO\s+([a-zA-Z0-9_\[\]]+)'
            ]
            
            for pattern in table_patterns:
                matches = re.finditer(pattern, line_upper)
                for match in matches:
                    table_name = match.group(1).strip('[]')
                    table_node_id = f"database:table:{table_name}"
                    
                    # Create table node if not exists
                    if table_node_id not in [n.id for n in nodes]:
                        nodes.append(CodeNode(
                            id=table_node_id,
                            name=table_name,
                            node_type=NodeType.TABLE,
                            file_path="database",
                            line_number=0,
                            metadata={"database_object": True}
                        ))
        
        return nodes, relationships
    
    def _extract_access_modifier(self, line: str) -> str:
        """Extract access modifier from a line of code"""
        line_lower = line.lower()
        if 'private' in line_lower:
            return 'private'
        elif 'protected' in line_lower:
            return 'protected'
        elif 'internal' in line_lower:
            return 'internal'
        elif 'public' in line_lower:
            return 'public'
        else:
            return 'default'
    
    def _save_analysis_to_db(self):
        """Save analysis results to database"""
        cursor = self.db_connection.cursor()
        
        # Save nodes
        for node in self.nodes.values():
            cursor.execute("""
                INSERT OR REPLACE INTO code_nodes 
                (id, name, node_type, file_path, line_number, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                node.id, node.name, node.node_type.value, 
                node.file_path, node.line_number, json.dumps(node.metadata)
            ))
        
        # Save relationships
        for rel in self.relationships:
            cursor.execute("""
                INSERT INTO code_relationships 
                (source_id, target_id, relationship_type, metadata, confidence)
                VALUES (?, ?, ?, ?, ?)
            """, (
                rel.source_id, rel.target_id, rel.relationship_type.value,
                json.dumps(rel.metadata), rel.confidence
            ))
        
        self.db_connection.commit()
        logger.info(f"Saved {len(self.nodes)} nodes and {len(self.relationships)} relationships to database")
    
    def _identify_patterns(self) -> List[CodePattern]:
        """Identify code patterns from the analyzed graph"""
        patterns = []
        
        # CRUD Pattern Detection
        crud_patterns = self._find_crud_patterns()
        patterns.extend(crud_patterns)
        
        # ASPX Page Patterns
        page_patterns = self._find_page_patterns()
        patterns.extend(page_patterns)
        
        return patterns
    
    def _find_crud_patterns(self) -> List[CodePattern]:
        """Find CRUD operation patterns"""
        patterns = []
        
        # Group nodes by entity (based on naming conventions)
        entity_groups = {}
        for node in self.nodes.values():
            if node.node_type == NodeType.CLASS:
                # Extract entity name from class name (e.g., ProductManager -> Product)
                if node.name.endswith('Manager'):
                    entity_name = node.name[:-7]  # Remove 'Manager'
                    if entity_name not in entity_groups:
                        entity_groups[entity_name] = []
                    entity_groups[entity_name].append(node)
        
        # For each entity group, create a CRUD pattern
        for entity_name, nodes in entity_groups.items():
            if len(nodes) > 0:  # At least one related node
                pattern_files = list(set([node.file_path for node in nodes]))
                
                pattern = CodePattern(
                    pattern_id=f"crud_{entity_name.lower()}",
                    pattern_type="database_crud",
                    files=pattern_files,
                    nodes=nodes,
                    relationships=[rel for rel in self.relationships 
                                 if any(rel.source_id == node.id or rel.target_id == node.id for node in nodes)],
                    template_data={
                        "entity_name": entity_name,
                        "table_name": f"{entity_name}s",
                        "primary_key": f"{entity_name}ID",
                        "manager_class": f"{entity_name}Manager"
                    },
                    similarity_score=0.8
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _find_page_patterns(self) -> List[CodePattern]:
        """Find ASPX page patterns"""
        patterns = []
        
        # Find ASPX pages with their related components
        aspx_pages = [node for node in self.nodes.values() if node.node_type == NodeType.ASPX_PAGE]
        
        for page_node in aspx_pages:
            # Find related nodes (codebehind, controls, etc.)
            related_nodes = [page_node]
            related_relationships = []
            
            for rel in self.relationships:
                if rel.source_id == page_node.id or rel.target_id == page_node.id:
                    related_relationships.append(rel)
                    # Add the related node
                    other_node_id = rel.target_id if rel.source_id == page_node.id else rel.source_id
                    if other_node_id in self.nodes:
                        related_nodes.append(self.nodes[other_node_id])
            
            if len(related_nodes) > 1:  # Page + at least one related component
                pattern = CodePattern(
                    pattern_id=f"page_{page_node.name.lower()}",
                    pattern_type="aspx_page",
                    files=list(set([node.file_path for node in related_nodes])),
                    nodes=related_nodes,
                    relationships=related_relationships,
                    template_data={
                        "page_name": page_node.name,
                        "control_count": len([n for n in related_nodes if n.node_type == NodeType.ASPX_CONTROL])
                    },
                    similarity_score=0.7
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def get_node_types_summary(self) -> Dict[str, int]:
        """Get summary of node types in the graph"""
        type_counts = {}
        for node in self.nodes.values():
            node_type = node.node_type.value
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        return type_counts
    
    def get_relationship_types_summary(self) -> Dict[str, int]:
        """Get summary of relationship types in the graph"""
        type_counts = {}
        for rel in self.relationships:
            rel_type = rel.relationship_type.value
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        return type_counts
    
    def export_graph_data(self, output_path: str = "code_graph.json"):
        """Export graph data for visualization"""
        export_data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "patterns": [pattern.to_dict() for pattern in self.patterns],
            "summary": {
                "node_types": self.get_node_types_summary(),
                "relationship_types": self.get_relationship_types_summary()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Graph data exported to {output_path}")
        return export_data
    
    def setup_tools(self):
        """Setup MCP tools for the enhanced server"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            return [
                Tool(
                    name="analyze_specific_files",
                    description="Analyze specific files and build detailed code graph with typed nodes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_paths": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of file paths to analyze"
                            }
                        },
                        "required": ["file_paths"]
                    }
                ),
                Tool(
                    name="get_node_types_summary",
                    description="Get summary of node types in the code graph",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="get_relationship_types_summary", 
                    description="Get summary of relationship types in the code graph",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="export_graph_data",
                    description="Export graph data for visualization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "output_path": {
                                "type": "string",
                                "description": "Path to save the graph data"
                            }
                        }
                    }
                ),
                Tool(
                    name="find_patterns_by_type",
                    description="Find code patterns by type",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern_type": {
                                "type": "string",
                                "description": "Type of pattern to find (database_crud, aspx_page, etc.)"
                            }
                        },
                        "required": ["pattern_type"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
            if name == "analyze_specific_files":
                results = self.analyze_specific_files(arguments["file_paths"])
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            elif name == "get_node_types_summary":
                summary = self.get_node_types_summary()
                return [TextContent(
                    type="text",
                    text=json.dumps(summary, indent=2)
                )]
            elif name == "get_relationship_types_summary":
                summary = self.get_relationship_types_summary()
                return [TextContent(
                    type="text",
                    text=json.dumps(summary, indent=2)
                )]
            elif name == "export_graph_data":
                output_path = arguments.get("output_path", "code_graph.json")
                data = self.export_graph_data(output_path)
                return [TextContent(
                    type="text",
                    text=json.dumps(data, indent=2)
                )]
            elif name == "find_patterns_by_type":
                pattern_type = arguments["pattern_type"]
                matching_patterns = [p for p in self.patterns if p.pattern_type == pattern_type]
                return [TextContent(
                    type="text",
                    text=json.dumps([p.to_dict() for p in matching_patterns], indent=2)
                )]
            else:
                raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main server entry point"""
    server_instance = EnhancedCodeGraphServer()
    server_instance.setup_tools()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="enhanced-code-graph-mcp",
                server_version="2.0.0",
                capabilities=server_instance.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 