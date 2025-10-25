import { z } from 'zod';

// Zod schemas for tool input validation

export const SearchRedmineTicketsSchema = z.object({
  project_id: z.number().int().positive().optional(),
  status_id: z.number().int().positive().optional(),
  assigned_to_id: z.number().int().positive().optional(),
  limit: z.number().int().positive().max(100).default(25).optional(),
  offset: z.number().int().min(0).default(0).optional(),
});

export const GetRedmineTicketDetailSchema = z.object({
  ticket_id: z.number().int().positive(),
});

export type SearchRedmineTicketsInput = z.infer<typeof SearchRedmineTicketsSchema>;
export type GetRedmineTicketDetailInput = z.infer<typeof GetRedmineTicketDetailSchema>;

// Schema for listing projects
export const ListRedmineProjectsSchema = z.object({
  limit: z.number().int().positive().max(100).default(25).optional(),
  offset: z.number().int().min(0).default(0).optional(),
});

export type ListRedmineProjectsInput = z.infer<typeof ListRedmineProjectsSchema>;

// Schema for listing roles
export const ListRedmineRolesSchema = z.object({});

export const GetRedmineRoleDetailSchema = z.object({
  role_id: z.number().int().positive(),
});

export type ListRedmineRolesInput = z.infer<typeof ListRedmineRolesSchema>;
export type GetRedmineRoleDetailInput = z.infer<typeof GetRedmineRoleDetailSchema>;

// Schema for listing trackers
export const ListRedmineTrackersSchema = z.object({});

export type ListRedmineTrackersInput = z.infer<typeof ListRedmineTrackersSchema>;

// Schema for listing priorities
export const ListRedminePrioritiesSchema = z.object({});

export type ListRedminePrioritiesInput = z.infer<typeof ListRedminePrioritiesSchema>;

// Schema for listing issue statuses
export const ListRedmineIssueStatusesSchema = z.object({});

export type ListRedmineIssueStatusesInput = z.infer<typeof ListRedmineIssueStatusesSchema>;