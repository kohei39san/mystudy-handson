#!/usr/bin/env node

// Load environment variables from .env (if present)
import 'dotenv/config';

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';
import fetch from 'node-fetch';
import {
  SearchRedmineTicketsSchema,
  GetRedmineTicketDetailSchema,
  SearchRedmineTicketsInput,
  GetRedmineTicketDetailInput,
  ListRedmineProjectsSchema,
  ListRedmineProjectsInput,
  ListRedmineRolesSchema,
  ListRedmineRolesInput,
  GetRedmineRoleDetailSchema,
  GetRedmineRoleDetailInput,
  ListRedmineTrackersSchema,
  ListRedmineTrackersInput,
  ListRedminePrioritiesSchema,
  ListRedminePrioritiesInput,
  ListRedmineIssueStatusesSchema,
  ListRedmineIssueStatusesInput,
  CreateRedmineIssueSchema,
  CreateRedmineIssueInput,
  UpdateRedmineIssueSchema,
  UpdateRedmineIssueInput,
  DeleteRedmineIssueSchema,
  DeleteRedmineIssueInput,
} from './schemas.js';
import {
  RedmineIssuesResponse,
  RedmineIssueResponse,
  RedmineErrorResponse,
  SearchTicketsParams,
  RedmineProjectsResponse,
  RedmineRolesResponse,
  RedmineRoleResponse,
  RedmineTrackersResponse,
  RedminePrioritiesResponse,
  RedmineIssueStatusesResponse,
} from './types.js';

export class RedmineMCPServer {
  private server: Server;
  private ssmClient: SSMClient;
  private redmineBaseUrl: string;
  private redmineBaseUrlParameter: string;
  private apiKeyParameter: string;
  private apiKey: string | null = null;

  constructor() {
    this.server = new Server(
      {
        name: 'redmine-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Environment variables
  this.redmineBaseUrl = process.env.REDMINE_BASE_URL || '';
  this.redmineBaseUrlParameter = process.env.REDMINE_BASE_URL_PARAMETER || '';
  this.apiKeyParameter = process.env.REDMINE_API_KEY_PARAMETER || '';
    const awsRegion = process.env.AWS_REGION || 'us-east-1';

    if (!this.redmineBaseUrl) {
      // If base URL is not set via env var, it may be provided via SSM parameter name.
      if (!this.redmineBaseUrlParameter) {
        throw new Error('REDMINE_BASE_URL environment variable or REDMINE_BASE_URL_PARAMETER is required');
      }
    }

    if (!this.apiKeyParameter) {
      throw new Error('REDMINE_API_KEY_PARAMETER environment variable is required');
    }

    // Initialize AWS SSM client
    this.ssmClient = new SSMClient({ region: awsRegion });

    this.setupToolHandlers();
  }

  private async getApiKey(): Promise<string> {
    if (this.apiKey) {
      return this.apiKey;
    }

    try {
      const command = new GetParameterCommand({
        Name: this.apiKeyParameter,
        WithDecryption: true,
      });

      const response = await this.ssmClient.send(command);
      
      if (!response.Parameter?.Value) {
        throw new Error('API key not found in Parameter Store');
      }

      this.apiKey = response.Parameter.Value;
      return this.apiKey;
    } catch (error) {
      throw new Error(`Failed to retrieve API key from Parameter Store: ${error}`);
    }
  }

  private async getRedmineBaseUrl(): Promise<string> {
    // If env var provided, prefer it
    if (this.redmineBaseUrl) {
      return this.redmineBaseUrl;
    }

    // Otherwise, fetch from SSM using the configured parameter name
    if (!this.redmineBaseUrlParameter) {
      throw new Error('REDMINE_BASE_URL is not configured and REDMINE_BASE_URL_PARAMETER is not provided');
    }

    try {
      const command = new GetParameterCommand({
        Name: this.redmineBaseUrlParameter,
        WithDecryption: true,
      });

      const response = await this.ssmClient.send(command);
      if (!response.Parameter?.Value) {
        throw new Error('Redmine base URL not found in Parameter Store');
      }

      // Cache the value so future calls don't hit SSM
      this.redmineBaseUrl = response.Parameter.Value;
      return this.redmineBaseUrl;
    } catch (error) {
      throw new Error(`Failed to retrieve Redmine base URL from Parameter Store: ${error}`);
    }
  }

  private async makeRedmineRequest<T>(endpoint: string, params?: Record<string, any>, method: string = 'GET', body?: any): Promise<T> {
    const apiKey = await this.getApiKey();
    const baseUrl = await this.getRedmineBaseUrl();

    const url = new URL(`${baseUrl}${endpoint}`);
    url.searchParams.append('key', apiKey);
    
    if (method === 'GET' && params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, value.toString());
        }
      });
    }

    const requestOptions: any = {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    };

    if (body && (method === 'POST' || method === 'PUT')) {
      requestOptions.body = JSON.stringify(body);
    }

    const response = await fetch(url.toString(), requestOptions);

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorJson = JSON.parse(errorText) as RedmineErrorResponse;
        if (errorJson.errors && errorJson.errors.length > 0) {
          errorMessage += ` - ${errorJson.errors.join(', ')}`;
        }
      } catch {
        // If parsing fails, use the raw error text
        errorMessage += ` - ${errorText}`;
      }
      
      throw new Error(errorMessage);
    }

    if (method === 'DELETE') {
      return {} as T;
    }

    const data = await response.json() as T;
    return data;
  }

  private setupToolHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'search_redmine_tickets',
            description: 'Search for Redmine tickets with optional filters',
            inputSchema: {
              type: 'object',
              properties: {
                project_id: {
                  type: 'number',
                  description: 'Project ID to filter tickets',
                },
                status_id: {
                  type: 'number',
                  description: 'Status ID to filter tickets',
                },
                assigned_to_id: {
                  type: 'number',
                  description: 'Assigned user ID to filter tickets',
                },
                limit: {
                  type: 'number',
                  description: 'Maximum number of tickets to return (default: 25, max: 100)',
                  default: 25,
                },
                offset: {
                  type: 'number',
                  description: 'Number of tickets to skip (default: 0)',
                  default: 0,
                },
              },
            },
          },
          {
            name: 'get_redmine_ticket_detail',
            description: 'Get detailed information about a specific Redmine ticket',
            inputSchema: {
              type: 'object',
              properties: {
                ticket_id: {
                  type: 'number',
                  description: 'The ID of the ticket to retrieve',
                },
              },
              required: ['ticket_id'],
            },
          },
          {
            name: 'list_redmine_projects',
            description: 'List Redmine projects with pagination',
            inputSchema: {
              type: 'object',
              properties: {
                limit: {
                  type: 'number',
                  description: 'Maximum number of projects to return (default: 25, max: 100)',
                  default: 25,
                },
                offset: {
                  type: 'number',
                  description: 'Number of projects to skip (default: 0)',
                  default: 0,
                },
              },
            },
          },
          {
            name: 'list_redmine_roles',
            description: 'List all Redmine roles',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'get_redmine_role_detail',
            description: 'Get detailed information about a specific Redmine role',
            inputSchema: {
              type: 'object',
              properties: {
                role_id: {
                  type: 'number',
                  description: 'The ID of the role to retrieve',
                },
              },
              required: ['role_id'],
            },
          },
          {
            name: 'list_redmine_trackers',
            description: 'List all Redmine trackers',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'list_redmine_priorities',
            description: 'List all Redmine issue priorities',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'list_redmine_issue_statuses',
            description: 'List all Redmine issue statuses',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'create_redmine_issue',
            description: 'Create a new Redmine issue',
            inputSchema: {
              type: 'object',
              properties: {
                project_id: {
                  type: 'number',
                  description: 'Project ID (required)',
                },
                tracker_id: {
                  type: 'number',
                  description: 'Tracker ID (required)',
                },
                subject: {
                  type: 'string',
                  description: 'Issue subject (required)',
                },
                description: {
                  type: 'string',
                  description: 'Issue description (optional)',
                },
                status_id: {
                  type: 'number',
                  description: 'Status ID (optional)',
                },
                priority_id: {
                  type: 'number',
                  description: 'Priority ID (optional)',
                },
                assigned_to_id: {
                  type: 'number',
                  description: 'Assigned user ID (optional)',
                },
              },
              required: ['project_id', 'tracker_id', 'subject'],
            },
          },
          {
            name: 'update_redmine_issue',
            description: 'Update an existing Redmine issue',
            inputSchema: {
              type: 'object',
              properties: {
                issue_id: {
                  type: 'number',
                  description: 'Issue ID to update (required)',
                },
                subject: {
                  type: 'string',
                  description: 'New subject (optional)',
                },
                description: {
                  type: 'string',
                  description: 'New description (optional)',
                },
                status_id: {
                  type: 'number',
                  description: 'New status ID (optional)',
                },
                priority_id: {
                  type: 'number',
                  description: 'New priority ID (optional)',
                },
                assigned_to_id: {
                  type: 'number',
                  description: 'New assigned user ID (optional)',
                },
                notes: {
                  type: 'string',
                  description: 'Update notes (optional)',
                },
              },
              required: ['issue_id'],
            },
          },
          {
            name: 'delete_redmine_issue',
            description: 'Delete a Redmine issue',
            inputSchema: {
              type: 'object',
              properties: {
                issue_id: {
                  type: 'number',
                  description: 'Issue ID to delete (required)',
                },
              },
              required: ['issue_id'],
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'search_redmine_tickets':
            return await this.handleSearchTickets(args as SearchRedmineTicketsInput);
          
          case 'get_redmine_ticket_detail':
            return await this.handleGetTicketDetail(args as GetRedmineTicketDetailInput);

          case 'list_redmine_projects':
            return await this.handleListProjects(args as ListRedmineProjectsInput);

          case 'list_redmine_roles':
            return await this.handleListRoles(args as ListRedmineRolesInput);

          case 'get_redmine_role_detail':
            return await this.handleGetRoleDetail(args as GetRedmineRoleDetailInput);

          case 'list_redmine_trackers':
            return await this.handleListTrackers(args as ListRedmineTrackersInput);

          case 'list_redmine_priorities':
            return await this.handleListPriorities(args as ListRedminePrioritiesInput);

          case 'list_redmine_issue_statuses':
            return await this.handleListIssueStatuses(args as ListRedmineIssueStatusesInput);

          case 'create_redmine_issue':
            return await this.handleCreateIssue(args as CreateRedmineIssueInput);

          case 'update_redmine_issue':
            return await this.handleUpdateIssue(args as UpdateRedmineIssueInput);

          case 'delete_redmine_issue':
            return await this.handleDeleteIssue(args as DeleteRedmineIssueInput);
          
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error instanceof Error ? error.message : String(error)}`,
            },
          ],
        };
      }
    });
  }

  async handleSearchTickets(args: SearchRedmineTicketsInput) {
    // Validate input using Zod
    const validatedArgs = SearchRedmineTicketsSchema.parse(args);

    const params: SearchTicketsParams & { include?: string } = {
      ...validatedArgs,
      include: 'attachments,journals',
    };

    const response = await this.makeRedmineRequest<RedmineIssuesResponse>('/issues.json', params);

    const ticketSummary = response.issues.map(issue => ({
      id: issue.id,
      subject: issue.subject,
      status: issue.status.name,
      priority: issue.priority.name,
      assigned_to: issue.assigned_to?.name || 'Unassigned',
      project: issue.project.name,
      created_on: issue.created_on,
      updated_on: issue.updated_on,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            total_count: response.total_count,
            offset: response.offset,
            limit: response.limit,
            tickets: ticketSummary,
          }, null, 2),
        },
      ],
    };
  }

  async handleGetTicketDetail(args: GetRedmineTicketDetailInput) {
    // Validate input using Zod
    const validatedArgs = GetRedmineTicketDetailSchema.parse(args);

    const params = {
      include: 'children,attachments,relations,changesets,journals,watchers',
    };

    const response = await this.makeRedmineRequest<RedmineIssueResponse>(
      `/issues/${validatedArgs.ticket_id}.json`,
      params
    );

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(response.issue, null, 2),
        },
      ],
    };
  }

  async handleListProjects(args: ListRedmineProjectsInput) {
    // Validate input using Zod
    const validatedArgs = ListRedmineProjectsSchema.parse(args);

    const params = {
      limit: validatedArgs.limit,
      offset: validatedArgs.offset,
    } as Record<string, any>;

    const response = await this.makeRedmineRequest<RedmineProjectsResponse>('/projects.json', params);

    const projects = response.projects.map(p => ({
      id: p.id,
      name: p.name,
      identifier: p.identifier,
      description: p.description || '',
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            total_count: response.total_count ?? projects.length,
            offset: response.offset ?? validatedArgs.offset,
            limit: response.limit ?? validatedArgs.limit,
            projects,
          }, null, 2),
        },
      ],
    };
  }

  async handleListRoles(args: ListRedmineRolesInput) {
    // Validate input using Zod
    const validatedArgs = ListRedmineRolesSchema.parse(args);

    const response = await this.makeRedmineRequest<RedmineRolesResponse>('/roles.json');

    const roles = response.roles.map(r => ({
      id: r.id,
      name: r.name,
      assignable: r.assignable ?? false,
      builtin: r.builtin,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ roles }, null, 2),
        },
      ],
    };
  }

  async handleGetRoleDetail(args: GetRedmineRoleDetailInput) {
    // Validate input using Zod
    const validatedArgs = GetRedmineRoleDetailSchema.parse(args);

    const response = await this.makeRedmineRequest<RedmineRoleResponse>(
      `/roles/${validatedArgs.role_id}.json`
    );

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(response.role, null, 2),
        },
      ],
    };
  }

  async handleListTrackers(args: ListRedmineTrackersInput) {
    // Validate input using Zod
    const validatedArgs = ListRedmineTrackersSchema.parse(args);

    const response = await this.makeRedmineRequest<RedmineTrackersResponse>('/trackers.json');

    const trackers = response.trackers.map(t => ({
      id: t.id,
      name: t.name,
      default_status: t.default_status?.name,
      description: t.description || '',
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ trackers }, null, 2),
        },
      ],
    };
  }

  async handleListPriorities(args: ListRedminePrioritiesInput) {
    // Validate input using Zod
    const validatedArgs = ListRedminePrioritiesSchema.parse(args);

    const response = await this.makeRedmineRequest<RedminePrioritiesResponse>('/enumerations/issue_priorities.json');

    const priorities = response.issue_priorities.map(p => ({
      id: p.id,
      name: p.name,
      is_default: p.is_default ?? false,
      active: p.active ?? true,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ priorities }, null, 2),
        },
      ],
    };
  }

  async handleListIssueStatuses(args: ListRedmineIssueStatusesInput) {
    // Validate input using Zod
    const validatedArgs = ListRedmineIssueStatusesSchema.parse(args);

    const response = await this.makeRedmineRequest<RedmineIssueStatusesResponse>('/issue_statuses.json');

    const statuses = response.issue_statuses.map(s => ({
      id: s.id,
      name: s.name,
      is_closed: s.is_closed ?? false,
      is_default: s.is_default ?? false,
    }));

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ statuses }, null, 2),
        },
      ],
    };
  }

  async handleCreateIssue(args: CreateRedmineIssueInput) {
    // Validate input using Zod
    const validatedArgs = CreateRedmineIssueSchema.parse(args);

    const issueData = {
      issue: {
        project_id: validatedArgs.project_id,
        tracker_id: validatedArgs.tracker_id,
        subject: validatedArgs.subject,
        description: validatedArgs.description,
        status_id: validatedArgs.status_id,
        priority_id: validatedArgs.priority_id,
        assigned_to_id: validatedArgs.assigned_to_id,
      }
    };

    const response = await this.makeRedmineRequest<RedmineIssueResponse>('/issues.json', undefined, 'POST', issueData);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ message: 'Issue created successfully', issue: response.issue }, null, 2),
        },
      ],
    };
  }

  async handleUpdateIssue(args: UpdateRedmineIssueInput) {
    // Validate input using Zod
    const validatedArgs = UpdateRedmineIssueSchema.parse(args);

    const updateData: any = { issue: {} };
    
    if (validatedArgs.subject) updateData.issue.subject = validatedArgs.subject;
    if (validatedArgs.description) updateData.issue.description = validatedArgs.description;
    if (validatedArgs.status_id) updateData.issue.status_id = validatedArgs.status_id;
    if (validatedArgs.priority_id) updateData.issue.priority_id = validatedArgs.priority_id;
    if (validatedArgs.assigned_to_id) updateData.issue.assigned_to_id = validatedArgs.assigned_to_id;
    if (validatedArgs.notes) updateData.issue.notes = validatedArgs.notes;

    await this.makeRedmineRequest(`/issues/${validatedArgs.issue_id}.json`, undefined, 'PUT', updateData);

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ message: `Issue ${validatedArgs.issue_id} updated successfully` }, null, 2),
        },
      ],
    };
  }

  async handleDeleteIssue(args: DeleteRedmineIssueInput) {
    // Validate input using Zod
    const validatedArgs = DeleteRedmineIssueSchema.parse(args);

    await this.makeRedmineRequest(`/issues/${validatedArgs.issue_id}.json`, undefined, 'DELETE');

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({ message: `Issue ${validatedArgs.issue_id} deleted successfully` }, null, 2),
        },
      ],
    };
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Redmine MCP server running on stdio');
  }
}

// Start the server
const server = new RedmineMCPServer();
server.run().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});