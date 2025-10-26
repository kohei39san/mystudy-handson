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
                ),
                Tool(
                    name="search_issues",
                    description="Search for issues in Redmine with various filters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status_id": {
                                "type": "string",
                                "description": "Status ID or name (e.g., 'open', 'closed', '1')"
                            },
                            "tracker_id": {
                                "type": "string",
                                "description": "Tracker ID or name (e.g., 'bug', 'feature', '1')"
                            },
                            "assigned_to_id": {
                                "type": "string",
                                "description": "Assigned user ID or name"
                            },
                            "parent_id": {
                                "type": "string",
                                "description": "Parent issue ID"
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Project ID or identifier"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Search text in issue subject"
                            },
                            "description": {
                                "type": "string",
                                "description": "Search text in issue description"
                            },
                            "notes": {
                                "type": "string",
                                "description": "Search text in issue notes"
                            },
                            "q": {
                                "type": "string",
                                "description": "General text search across multiple fields"
                            },
                            "page": {
                                "type": "integer",
                                "description": "Page number for pagination (default: 1)",
                                "minimum": 1
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "Items per page (default: 25)",
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_issue_details",
                    description="Get detailed information about a specific issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_id": {
                                "type": "string",
                                "description": "Issue ID to retrieve details for"
                            }
                        },
                        "required": ["issue_id"]
                    }
                ),
                Tool(
                    name="get_available_trackers",
                    description="Get available tracker options from issue creation page",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {
                                "type": "string",
                                "description": "Project ID to get trackers for (optional)"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_available_statuses",
                    description="Get available status options for a specific issue",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_id": {
                                "type": "string",
                                "description": "Issue ID to get available statuses for"
                            }
                        },
                        "required": ["issue_id"]
                    }
                ),
                Tool(
                    name="update_issue",
                    description="Update an issue with new field values",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_id": {
                                "type": "string",
                                "description": "Issue ID to update"
                            },
                            "subject": {
                                "type": "string",
                                "description": "New subject/title for the issue"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description for the issue"
                            },
                            "status_id": {
                                "type": "string",
                                "description": "New status ID (e.g., '1', '2', '3')"
                            },
                            "priority_id": {
                                "type": "string",
                                "description": "New priority ID (e.g., '1', '2', '3')"
                            },
                            "assigned_to_id": {
                                "type": "string",
                                "description": "New assignee user ID"
                            },
                            "done_ratio": {
                                "type": "integer",
                                "description": "Progress percentage (0-100)",
                                "minimum": 0,
                                "maximum": 100
                            },
                            "notes": {
                                "type": "string",
                                "description": "Update notes/comment to add to the issue"
                            }
                        },
                        "required": ["issue_id"]
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
                elif name == "search_issues":
                    return await self._handle_search_issues(arguments)
                elif name == "get_issue_details":
                    return await self._handle_get_issue_details(arguments)
                elif name == "get_available_trackers":
                    return await self._handle_get_available_trackers(arguments)
                elif name == "get_available_statuses":
                    return await self._handle_get_available_statuses(arguments)
                elif name == "update_issue":
                    return await self._handle_update_issue(arguments)
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
    
    async def _handle_search_issues(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle search issues tool call"""
        logger.info("Searching for issues")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        # Extract search parameters
        search_params = {}
        for key in ['status_id', 'tracker_id', 'assigned_to_id', 'parent_id', 'project_id',
                   'subject', 'description', 'notes', 'q', 'page', 'per_page']:
            if key in arguments and arguments[key] is not None:
                search_params[key] = arguments[key]
        
        result = self.scraper.search_issues(**search_params)
        
        if result["success"]:
            issues = result["issues"]
            total_count = result["total_count"]
            page = result["page"]
            per_page = result["per_page"]
            total_pages = result["total_pages"]
            
            if not issues:
                response_text = "[SUCCESS] No issues found matching the search criteria."
            else:
                response_text = f"[SUCCESS] {result['message']}\n\n"
                response_text += "**Search Results:**\n"
                response_text += "=" * 50 + "\n"
                
                for i, issue in enumerate(issues, 1):
                    response_text += f"{i}. **#{issue.get('id', 'N/A')}** - {issue.get('subject', 'No subject')}\n"
                    if issue.get('tracker'):
                        response_text += f"   Tracker: {issue['tracker']}\n"
                    if issue.get('status'):
                        response_text += f"   Status: {issue['status']}\n"
                    if issue.get('priority'):
                        response_text += f"   Priority: {issue['priority']}\n"
                    if issue.get('assigned_to'):
                        response_text += f"   Assigned to: {issue['assigned_to']}\n"
                    if issue.get('updated_on'):
                        response_text += f"   Updated: {issue['updated_on']}\n"
                    if issue.get('url'):
                        response_text += f"   URL: {issue['url']}\n"
                    response_text += "\n"
                
                # Add pagination info
                response_text += "**Pagination:**\n"
                response_text += f"- Total issues: {total_count}\n"
                response_text += f"- Current page: {page} of {total_pages}\n"
                response_text += f"- Issues per page: {per_page}\n"
                response_text += f"- Showing issues: {len(issues)}\n"
        else:
            response_text = f"[ERROR] {result['message']}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_get_issue_details(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get issue details tool call"""
        issue_id = arguments.get("issue_id")
        
        if not issue_id:
            return [TextContent(
                type="text",
                text="[ERROR] Issue ID is required"
            )]
        
        logger.info(f"Fetching details for issue #{issue_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_issue_details(issue_id)
        
        if result["success"]:
            issue = result["issue"]
            response_text = f"[SUCCESS] {result['message']}\n\n"
            response_text += "**Issue Details:**\n"
            response_text += "=" * 50 + "\n"
            
            response_text += f"**ID:** #{issue.get('id', 'N/A')}\n"
            if issue.get('subject'):
                response_text += f"**Subject:** {issue['subject']}\n"
            if issue.get('tracker'):
                response_text += f"**Tracker:** {issue['tracker']}\n"
            if issue.get('status'):
                response_text += f"**Status:** {issue['status']}\n"
            if issue.get('priority'):
                response_text += f"**Priority:** {issue['priority']}\n"
            if issue.get('assigned_to'):
                response_text += f"**Assigned to:** {issue['assigned_to']}\n"
            if issue.get('category'):
                response_text += f"**Category:** {issue['category']}\n"
            if issue.get('start_date'):
                response_text += f"**Start Date:** {issue['start_date']}\n"
            if issue.get('due_date'):
                response_text += f"**Due Date:** {issue['due_date']}\n"
            if issue.get('done_ratio'):
                response_text += f"**Progress:** {issue['done_ratio']}\n"
            if issue.get('created_on'):
                response_text += f"**Created:** {issue['created_on']}\n"
            if issue.get('updated_on'):
                response_text += f"**Updated:** {issue['updated_on']}\n"
            
            if issue.get('description'):
                response_text += f"\n**Description:**\n{issue['description']}\n"
        else:
            response_text = f"[ERROR] {result['message']}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_get_available_trackers(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get available trackers tool call"""
        project_id = arguments.get("project_id")
        
        logger.info(f"Getting available trackers for project: {project_id or 'all'}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_available_trackers(project_id)
        
        if result["success"]:
            trackers = result["trackers"]
            response_text = f"[SUCCESS] {result['message']}\n\n"
            response_text += "**Available Trackers:**\n"
            response_text += "=" * 40 + "\n"
            
            if trackers:
                for i, tracker in enumerate(trackers, 1):
                    response_text += f"{i}. **{tracker['text']}** (ID: {tracker['value']})\n"
                
                response_text += "\n**Usage:**\n"
                response_text += "Use either the ID or text when searching issues by tracker:\n"
                response_text += f"- search_issues(tracker_id='1')\n"
                response_text += f"- search_issues(tracker_id='課題')\n"
            else:
                response_text += "No tracker options available.\n"
        else:
            response_text = f"[ERROR] {result['message']}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_get_available_statuses(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get available statuses tool call"""
        issue_id = arguments.get("issue_id")
        
        if not issue_id:
            return [TextContent(
                type="text",
                text="[ERROR] Issue ID is required"
            )]
        
        logger.info(f"Getting available statuses for issue #{issue_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        result = self.scraper.get_available_statuses(issue_id)
        
        if result["success"]:
            statuses = result["statuses"]
            response_text = f"[SUCCESS] {result['message']}\n\n"
            response_text += "**Available Statuses:**\n"
            response_text += "=" * 40 + "\n"
            
            if statuses:
                for i, status in enumerate(statuses, 1):
                    response_text += f"{i}. **{status['text']}** (ID: {status['value']})\n"
                
                response_text += "\n**Usage:**\n"
                response_text += "Use either the ID or text when updating issue status:\n"
                response_text += f"- update_issue(issue_id='{issue_id}', status_id='2')\n"
                response_text += f"- update_issue(issue_id='{issue_id}', status_id='In Progress')\n"
            else:
                response_text += "No status options available for this issue.\n"
        else:
            response_text = f"[ERROR] {result['message']}"
        
        return [TextContent(
            type="text",
            text=response_text
        )]
    
    async def _handle_update_issue(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle update issue tool call"""
        issue_id = arguments.get("issue_id")
        
        if not issue_id:
            return [TextContent(
                type="text",
                text="[ERROR] Issue ID is required"
            )]
        
        logger.info(f"Updating issue #{issue_id}")
        
        # Check if authenticated
        if not self.scraper.is_authenticated:
            return [TextContent(
                type="text",
                text="[ERROR] Not authenticated. Please login first using the redmine_login tool."
            )]
        
        # Extract update parameters
        update_params = {}
        for key in ['subject', 'description', 'status_id', 'priority_id', 'assigned_to_id', 'done_ratio', 'notes']:
            if key in arguments and arguments[key] is not None:
                update_params[key] = arguments[key]
        
        if not update_params:
            return [TextContent(
                type="text",
                text="[ERROR] At least one field to update must be provided"
            )]
        
        result = self.scraper.update_issue(issue_id, **update_params)
        
        if result["success"]:
            response_text = f"[SUCCESS] {result['message']}\n\n"
            if 'updated_fields' in result:
                response_text += "**Updated Fields:**\n"
                for field in result['updated_fields']:
                    response_text += f"- {field}\n"
        else:
            response_text = f"[ERROR] {result['message']}"
        
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