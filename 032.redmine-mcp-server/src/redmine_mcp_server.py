#!/usr/bin/env python3
"""
Redmine MCP Server
A Model Context Protocol server for interacting with Redmine via web scraping
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    ServerCapabilities
)
from pydantic import BaseModel, Field

# Import our modules with proper error handling
try:
    from redmine_selenium import RedmineSeleniumScraper
    from config import config
except ImportError:
    # Try relative imports if absolute imports fail
    try:
        from .redmine_selenium import RedmineSeleniumScraper
        from .config import config
    except ImportError as e:
        print(f"Failed to import required modules: {e}")
        print("Please ensure you're running from the correct directory and all dependencies are installed.")
        sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO if config.debug else logging.WARNING)
logger = logging.getLogger(__name__)

class RedmineMCPServer:
    """Redmine MCP Server implementation"""
    
    def __init__(self):
        self.server = Server("redmine-mcp-server")
        self.scraper = RedmineSeleniumScraper()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="redmine_login",
                    description="Login to Redmine using username and password",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {
                                "type": "string",
                                "description": "Redmine username"
                            },
                            "password": {
                                "type": "string",
                                "description": "Redmine password"
                            }
                        },
                        "required": ["username", "password"]
                    }
                ),
                Tool(
                    name="get_projects",
                    description="Get list of projects from Redmine (requires authentication)",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="logout",
                    description="Logout from Redmine and clear session",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_server_info",
                    description="Get information about the Redmine server configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "redmine_login":
                    return await self._handle_login(arguments)
                elif name == "get_projects":
                    return await self._handle_get_projects(arguments)
                elif name == "logout":
                    return await self._handle_logout(arguments)
                elif name == "get_server_info":
                    return await self._handle_get_server_info(arguments)
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def _handle_login(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle login tool call"""
        username = arguments.get("username")
        password = arguments.get("password")
        
        if not username or not password:
            return [TextContent(
                type="text",
                text="Error: Both username and password are required"
            )]
        
        logger.info(f"Login attempt for user: {username}")
        result = self.scraper.login(username, password)
        
        if result["success"]:
            response_text = f"[SUCCESS] {result['message']}"
            if "redirect_url" in result:
                response_text += f"\nRedirected to: {result['redirect_url']}"
        else:
            response_text = f"[ERROR] {result['message']}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_get_projects(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get projects tool call"""
        logger.info("Fetching projects list")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_projects()
        
        if result["success"]:
            projects = result["projects"]
            if not projects:
                response_text = "[SUCCESS] Successfully connected, but no projects found or user has no access to projects."
            else:
                response_text = f"[SUCCESS] {result['message']}\n\n"
                response_text += "**Projects List:**\n"
                response_text += "=" * 50 + "\n"
                
                for i, project in enumerate(projects, 1):
                    response_text += f"{i}. **{project['name']}**\n"
                    if project['id']:
                        response_text += f"   ID: {project['id']}\n"
                    if project['description']:
                        response_text += f"   Description: {project['description']}\n"
                    if project['url']:
                        response_text += f"   URL: {project['url']}\n"
                    response_text += "\n"
                
                # Add summary
                response_text += f"**Summary:** {len(projects)} project(s) found"
        else:
            response_text = f"[ERROR] {result['message']}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_logout(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle logout tool call"""
        logger.info("Logout requested")
        result = self.scraper.logout()
        
        response_text = f"[SUCCESS] {result['message']}" if result["success"] else f"[ERROR] {result['message']}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_get_server_info(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get server info tool call"""
        info = {
            "server_url": config.base_url,
            "login_url": config.login_url,
            "projects_url": config.projects_url,
            "session_timeout": config.session_timeout,
            "request_timeout": config.request_timeout,
            "authenticated": self.scraper.is_authenticated,
            "session_valid": self.scraper.is_authenticated
        }
        
        response_text = "**Redmine Server Information:**\n"
        response_text += "=" * 40 + "\n"
        response_text += f"Server URL: {info['server_url']}\n"
        response_text += f"Login URL: {info['login_url']}\n"
        response_text += f"Projects URL: {info['projects_url']}\n"
        response_text += f"Session Timeout: {info['session_timeout']} seconds\n"
        response_text += f"Request Timeout: {info['request_timeout']} seconds\n"
        response_text += f"Authentication Status: {'[AUTH] Authenticated' if info['authenticated'] else '[NO-AUTH] Not Authenticated'}\n"
        response_text += f"Session Valid: {'[VALID] Valid' if info['session_valid'] else '[INVALID] Invalid/Expired'}\n"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
    

    async def run(self):
        """Run the MCP server"""
        logger.info(f"Starting Redmine MCP Server for {config.base_url}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="redmine-mcp-server",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(
                        tools={}
                    )
                )
            )

async def main():
    """Main entry point"""
    server = RedmineMCPServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)