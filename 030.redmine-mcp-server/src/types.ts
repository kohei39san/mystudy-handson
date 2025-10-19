// Redmine API response types

export interface RedmineUser {
  id: number;
  name: string;
  mail?: string;
}

export interface RedmineProject {
  id: number;
  name: string;
  identifier: string;
  description?: string;
}

export interface RedmineStatus {
  id: number;
  name: string;
}

export interface RedminePriority {
  id: number;
  name: string;
}

export interface RedmineTracker {
  id: number;
  name: string;
}

export interface RedmineCategory {
  id: number;
  name: string;
}

export interface RedmineVersion {
  id: number;
  name: string;
}

export interface RedmineCustomField {
  id: number;
  name: string;
  value: string | string[];
}

export interface RedmineJournal {
  id: number;
  user: RedmineUser;
  notes: string;
  created_on: string;
  private_notes: boolean;
}

export interface RedmineAttachment {
  id: number;
  filename: string;
  filesize: number;
  content_type: string;
  description: string;
  content_url: string;
  author: RedmineUser;
  created_on: string;
}

export interface RedmineIssue {
  id: number;
  project: RedmineProject;
  tracker: RedmineTracker;
  status: RedmineStatus;
  priority: RedminePriority;
  author: RedmineUser;
  assigned_to?: RedmineUser;
  category?: RedmineCategory;
  fixed_version?: RedmineVersion;
  subject: string;
  description: string;
  start_date?: string;
  due_date?: string;
  done_ratio: number;
  is_private: boolean;
  estimated_hours?: number;
  spent_hours?: number;
  custom_fields?: RedmineCustomField[];
  created_on: string;
  updated_on: string;
  closed_on?: string;
  journals?: RedmineJournal[];
  attachments?: RedmineAttachment[];
}

export interface RedmineIssuesResponse {
  issues: RedmineIssue[];
  total_count: number;
  offset: number;
  limit: number;
}

export interface RedmineIssueResponse {
  issue: RedmineIssue;
}

export interface RedmineErrorResponse {
  errors: string[];
}

// Search parameters
export interface SearchTicketsParams {
  project_id?: number;
  status_id?: number;
  assigned_to_id?: number;
  limit?: number;
  offset?: number;
}

export interface GetTicketDetailParams {
  ticket_id: number;
}

// Projects
export interface RedmineProjectSummary {
  id: number;
  name: string;
  identifier?: string;
  description?: string;
}

export interface RedmineProjectsResponse {
  projects: RedmineProjectSummary[];
  total_count?: number;
  offset?: number;
  limit?: number;
}