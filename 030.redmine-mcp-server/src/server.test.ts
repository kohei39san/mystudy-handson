import { SearchRedmineTicketsSchema, GetRedmineTicketDetailSchema, ListRedmineProjectsSchema, ListRedmineRolesSchema, GetRedmineRoleDetailSchema, ListRedmineTrackersSchema, ListRedminePrioritiesSchema, ListRedmineIssueStatusesSchema } from './schemas';

// Mock AWS SDK
jest.mock('@aws-sdk/client-ssm', () => ({
  SSMClient: jest.fn().mockImplementation(() => ({
    send: jest.fn().mockResolvedValue({
      Parameter: { Value: 'mock-api-key' }
    })
  })),
  GetParameterCommand: jest.fn()
}));

// Mock node-fetch
jest.mock('node-fetch', () => jest.fn());

describe('Redmine MCP Server Schemas', () => {
  describe('SearchRedmineTicketsSchema', () => {
    it('should validate valid search parameters', () => {
      const validInput = {
        project_id: 1,
        status_id: 2,
        assigned_to_id: 3,
        limit: 50,
        offset: 10
      };

      const result = SearchRedmineTicketsSchema.parse(validInput);
      expect(result).toEqual(validInput);
    });

    it('should use default values for optional parameters', () => {
      const input = {};
      const result = SearchRedmineTicketsSchema.parse(input);
      expect(result.limit).toBeUndefined();
      expect(result.offset).toBeUndefined();
    });

    it('should reject invalid limit values', () => {
      expect(() => {
        SearchRedmineTicketsSchema.parse({ limit: 101 });
      }).toThrow();

      expect(() => {
        SearchRedmineTicketsSchema.parse({ limit: -1 });
      }).toThrow();
    });

    it('should reject invalid offset values', () => {
      expect(() => {
        SearchRedmineTicketsSchema.parse({ offset: -1 });
      }).toThrow();
    });
  });

  describe('GetRedmineTicketDetailSchema', () => {
    it('should validate valid ticket ID', () => {
      const validInput = { ticket_id: 123 };
      const result = GetRedmineTicketDetailSchema.parse(validInput);
      expect(result).toEqual(validInput);
    });

    it('should reject invalid ticket IDs', () => {
      expect(() => {
        GetRedmineTicketDetailSchema.parse({ ticket_id: -1 });
      }).toThrow();

      expect(() => {
        GetRedmineTicketDetailSchema.parse({ ticket_id: 0 });
      }).toThrow();

      expect(() => {
        GetRedmineTicketDetailSchema.parse({});
      }).toThrow();
    });
  });

  describe('ListRedmineProjectsSchema', () => {
    it('should validate valid project list parameters', () => {
      const validInput = {
        limit: 30,
        offset: 5
      };

      const result = ListRedmineProjectsSchema.parse(validInput);
      expect(result).toEqual(validInput);
    });

    it('should use default values', () => {
      const input = {};
      const result = ListRedmineProjectsSchema.parse(input);
      expect(result.limit).toBeUndefined();
      expect(result.offset).toBeUndefined();
    });

    it('should reject invalid parameters', () => {
      expect(() => {
        ListRedmineProjectsSchema.parse({ limit: 101 });
      }).toThrow();

      expect(() => {
        ListRedmineProjectsSchema.parse({ offset: -1 });
      }).toThrow();
    });
  });

  describe('ListRedmineRolesSchema', () => {
    it('should validate empty input', () => {
      const input = {};
      const result = ListRedmineRolesSchema.parse(input);
      expect(result).toEqual({});
    });
  });

  describe('GetRedmineRoleDetailSchema', () => {
    it('should validate valid role ID', () => {
      const validInput = { role_id: 5 };
      const result = GetRedmineRoleDetailSchema.parse(validInput);
      expect(result).toEqual(validInput);
    });

    it('should reject invalid role IDs', () => {
      expect(() => {
        GetRedmineRoleDetailSchema.parse({ role_id: -1 });
      }).toThrow();

      expect(() => {
        GetRedmineRoleDetailSchema.parse({ role_id: 0 });
      }).toThrow();

      expect(() => {
        GetRedmineRoleDetailSchema.parse({});
      }).toThrow();
    });
  });

  describe('ListRedmineTrackersSchema', () => {
    it('should validate empty input', () => {
      const input = {};
      const result = ListRedmineTrackersSchema.parse(input);
      expect(result).toEqual({});
    });
  });

  describe('ListRedminePrioritiesSchema', () => {
    it('should validate empty input', () => {
      const input = {};
      const result = ListRedminePrioritiesSchema.parse(input);
      expect(result).toEqual({});
    });
  });

  describe('ListRedmineIssueStatusesSchema', () => {
    it('should validate empty input', () => {
      const input = {};
      const result = ListRedmineIssueStatusesSchema.parse(input);
      expect(result).toEqual({});
    });
  });
});

describe('AWS SDK Integration', () => {
  const { SSMClient, GetParameterCommand } = require('@aws-sdk/client-ssm');
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should mock SSMClient correctly', () => {
    const client = new SSMClient({ region: 'us-east-1' });
    expect(SSMClient).toHaveBeenCalledWith({ region: 'us-east-1' });
  });

  it('should mock GetParameterCommand correctly', async () => {
    const client = new SSMClient({ region: 'us-east-1' });
    const command = new GetParameterCommand({
      Name: '/test/parameter',
      WithDecryption: true
    });
    
    const result = await client.send(command);
    expect(result.Parameter.Value).toBe('mock-api-key');
  });
});