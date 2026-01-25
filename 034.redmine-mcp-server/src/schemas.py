"""
Pydantic schemas for Redmine MCP Server
All input validation and JSON schema definitions for MCP tools
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


# Request schemas (used for inputSchema)
class EmptyRequest(BaseModel):
    """Base model for tools that don't require parameters"""
    pass


class SearchIssuesRequest(BaseModel):
    """Search issues request schema"""
    status_id: Optional[str] = Field(None, description="Status ID or name")
    project_id: Optional[str] = Field(None, description="Project ID or identifier")
    tracker_id: Optional[int] = Field(None, description="Tracker ID (numeric only)")
    assigned_to_id: Optional[str] = Field(None, description="Assigned user ID or name")
    q: Optional[str] = Field(None, description="General text search (searches across multiple fields)")
    subject: Optional[str] = Field(None, description="Subject text search")
    description: Optional[str] = Field(None, description="Description text search")
    notes: Optional[str] = Field(None, description="Notes text search")
    parent_id: Optional[str] = Field(None, description="Parent issue ID")
    page: int = Field(1, ge=1, description="Page number for pagination (default: 1)")


class CreateIssueRequest(BaseModel):
    """Create issue request schema"""
    project_id: str = Field(description="Project ID to create issue in")
    issue_tracker_id: str = Field(description="Tracker ID (required)")
    issue_subject: str = Field(description="Issue subject/title (required)")
    fields: Optional[dict] = Field(None, description="Additional issue fields as key-value pairs (e.g., issue_description, issue_status_id, issue_assigned_to_id, custom fields)")


class UpdateIssueRequest(BaseModel):
    """Update issue request schema"""
    issue_id: str = Field(description="Issue ID to update")
    fields: Optional[dict] = Field(None, description="Fields to update as key-value pairs (e.g., subject, description, status_id, assigned_to_id, notes)")


class IssueIdRequest(BaseModel):
    """Request schema for operations requiring only issue ID"""
    issue_id: str = Field(description="Issue ID to retrieve details for")


class ProjectIdRequest(BaseModel):
    """Request schema for operations requiring only project ID"""
    project_id: str = Field(description="Project ID to get members for")


class TrackerFieldsRequest(BaseModel):
    """Request schema for getting tracker fields"""
    project_id: str = Field(description="Project ID")
    issue_tracker_id: str = Field(description="Tracker ID (required)")


class TimeEntriesRequest(BaseModel):
    """Time entries request schema"""
    project_id: str = Field(description="Project ID to get time entries for (required)")
    user_id: Optional[int] = Field(None, description="Numeric user ID to filter by (optional)")
    start_date: Optional[str] = Field(None, description="Start date for filtering in YYYY-MM-DD format (optional)")
    end_date: Optional[str] = Field(None, description="End date for filtering in YYYY-MM-DD format (optional)")
    page: int = Field(1, ge=1, description="Page number for pagination (default: 1)")


class CreationStatusesRequest(BaseModel):
    """Request schema for getting creation statuses"""
    project_id: str = Field(description="Project ID")
    tracker_id: str = Field(description="Tracker ID")


class AvailableStatusesRequest(BaseModel):
    """Request schema for getting available statuses for an issue"""
    issue_id: str = Field(description="Issue ID to get available statuses for")


class OptionalProjectIdRequest(BaseModel):
    """Request schema for operations with optional project ID"""
    project_id: Optional[str] = Field(None, description="Project ID to get trackers for (optional)")


# Response schemas (used for return values)
class LoginResponse(BaseModel):
    """Login operation response"""
    success: bool
    message: str
    redirect_url: Optional[str] = None
    current_user_id: Optional[str] = None


class ProjectInfo(BaseModel):
    """Single project information"""
    name: str
    id: str  # Changed from 'identifier' to match actual Redmine data
    description: Optional[str] = None
    url: Optional[str] = None
    created_on: Optional[str] = None
    status: Optional[str] = None


class ProjectsResponse(BaseModel):
    """Projects list response"""
    success: bool
    message: str
    projects: List[ProjectInfo]


class MemberInfo(BaseModel):
    """Project member information"""
    name: str
    roles: List[str] = Field(default_factory=list, description="List of member roles in the project")
    id: Optional[str] = Field(None, description="User ID")
    is_current_user: Optional[bool] = Field(None, description="Whether this member is the currently logged in user")
    additional_info: Optional[str] = Field(None, description="Additional member information")


class ProjectMembersResponse(BaseModel):
    """Project members response"""
    success: bool
    message: str
    members: List[MemberInfo]


class IssueInfo(BaseModel):
    """Issue information"""
    id: str
    subject: str
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    tracker: Optional[str] = None
    assigned_to: Optional[str] = None
    created_on: Optional[str] = None
    updated_on: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    target_version: Optional[str] = None
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    estimated_time: Optional[str] = None
    progress: Optional[str] = None
    spent_time: Optional[str] = None
    custom_fields: Optional[Dict[str, str]] = None


class IssuesResponse(BaseModel):
    """Issues search response"""
    success: bool
    message: str
    issues: List[IssueInfo]
    total_count: Optional[int] = None
    current_page: Optional[int] = None
    has_next: Optional[bool] = None


class IssueDetailResponse(BaseModel):
    """Issue detail response"""
    success: bool
    message: str
    issue: Optional[IssueInfo] = None
    journals: Optional[List[dict]] = None


class TrackerInfo(BaseModel):
    """Tracker information"""
    id: str
    name: str
    description: Optional[str] = None
    fields: Optional[List[Dict[str, Any]]] = None
    required_fields: Optional[List[Dict[str, Any]]] = None
    optional_fields: Optional[List[Dict[str, Any]]] = None


class TrackersResponse(BaseModel):
    """Trackers response"""
    success: bool
    message: str
    trackers: List[TrackerInfo]


class StatusInfo(BaseModel):
    """Status information"""
    id: str
    name: str
    is_closed: Optional[bool] = None


class StatusesResponse(BaseModel):
    """Statuses response"""
    success: bool
    message: str
    statuses: List[StatusInfo]


class FieldInfo(BaseModel):
    """Field information"""
    name: str
    type: str
    required: bool
    options: Optional[List[dict]] = None
    value: Optional[str] = None


class FieldsResponse(BaseModel):
    """Fields response"""
    success: bool
    message: str
    fields: List[FieldInfo]


class TimeEntryInfo(BaseModel):
    """Time entry information"""
    id: Optional[str] = None
    spent_on: Optional[str] = None
    hours: Optional[str] = None  # Changed from float to str to match actual data format (e.g. "0:15")
    activity: Optional[str] = None
    user: Optional[str] = None
    user_id: Optional[int] = None  # Numeric user ID for filtering
    issue: Optional[str] = None  # Full issue description with number
    issue_id: Optional[str] = None
    issue_subject: Optional[str] = None
    comments: Optional[str] = None


class TimeEntriesResponse(BaseModel):
    """Time entries response"""
    success: bool
    message: str
    time_entries: List[TimeEntryInfo]
    total_count: Optional[int] = None
    current_page: Optional[int] = None
    has_next: Optional[bool] = None


class CreateIssueResponse(BaseModel):
    """Create issue response"""
    success: bool
    message: str
    issue_id: Optional[str] = None
    issue_url: Optional[str] = None


class UpdateIssueResponse(BaseModel):
    """Update issue response"""
    success: bool
    message: str
    issue_id: Optional[str] = None
    issue_url: Optional[str] = None


class ServerInfo(BaseModel):
    """Server information"""
    version: Optional[str] = None
    database: Optional[str] = None
    environment: Optional[str] = None
    scm: Optional[List[str]] = None
    filesystem_encoding: Optional[str] = None
    redmine_plugins: Optional[List[dict]] = None


class ServerInfoResponse(BaseModel):
    """Server info response"""
    success: bool
    message: str
    server_info: Optional[ServerInfo] = None


class GeneralResponse(BaseModel):
    """General success/error response"""
    success: bool
    message: str