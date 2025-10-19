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