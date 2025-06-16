#!/bin/bash
echo "Starting AI Coding Agent MCP Server..."
source venv/bin/activate
python mcp_server/code_graph_server.py
