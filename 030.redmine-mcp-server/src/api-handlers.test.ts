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
const mockFetch = jest.fn();
jest.mock('node-fetch', () => mockFetch);

// Mock the MCP SDK to avoid ESM issues
jest.mock('@modelcontextprotocol/sdk/server/index.js', () => ({
  Server: jest.fn().mockImplementation(() => ({
    setRequestHandler: jest.fn(),
    connect: jest.fn()
  }))
}));

jest.mock('@modelcontextprotocol/sdk/server/stdio.js', () => ({
  StdioServerTransport: jest.fn()
}));

jest.mock('@modelcontextprotocol/sdk/types.js', () => ({
  CallToolRequestSchema: 'CallToolRequestSchema',
  ListToolsRequestSchema: 'ListToolsRequestSchema'
}));

describe('Redmine API Handlers', () => {
  let RedmineMCPServer: any;

  beforeAll(async () => {
    // Import after mocking
    const module = await import('./index.js');
    RedmineMCPServer = module.RedmineMCPServer;
  });

  let server: any;

  beforeEach(() => {
    process.env.REDMINE_BASE_URL = 'https://mock-redmine.com';
    process.env.REDMINE_API_KEY_PARAMETER = '/redmine/api-key';
    
    mockFetch.mockClear();
    server = new RedmineMCPServer();
  });

  describe('handleSearchTickets', () => {
    it('should make GET request to /issues.json', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          issues: [{
            id: 1,
            subject: 'Test Issue',
            status: { name: 'New' },
            priority: { name: 'Normal' },
            project: { name: 'Test Project' },
            created_on: '2023-01-01T00:00:00Z',
            updated_on: '2023-01-01T00:00:00Z'
          }],
          total_count: 1,
          offset: 0,
          limit: 25
        })
      };

      mockFetch.mockResolvedValue(mockResponse);

      const result = await server.handleSearchTickets({ limit: 10 });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/issues.json'),
        expect.objectContaining({ method: 'GET' })
      );
      
      const responseData = JSON.parse(result.content[0].text);
      expect(responseData.tickets).toHaveLength(1);
      expect(responseData.tickets[0].id).toBe(1);
    });
  });

  describe('handleCreateIssue', () => {
    it('should make POST request with issue data', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          issue: { id: 123, subject: 'New Issue' }
        })
      };

      mockFetch.mockResolvedValue(mockResponse);

      const input = {
        project_id: 1,
        tracker_id: 2,
        subject: 'New Issue'
      };

      const result = await server.handleCreateIssue(input);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/issues.json'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('"subject":"New Issue"')
        })
      );

      const responseData = JSON.parse(result.content[0].text);
      expect(responseData.message).toContain('created successfully');
    });
  });

  describe('handleUpdateIssue', () => {
    it('should make PUT request with update data', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({})
      };

      mockFetch.mockResolvedValue(mockResponse);

      const input = {
        issue_id: 123,
        subject: 'Updated Subject'
      };

      const result = await server.handleUpdateIssue(input);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/issues/123.json'),
        expect.objectContaining({
          method: 'PUT',
          body: expect.stringContaining('"subject":"Updated Subject"')
        })
      );

      const responseData = JSON.parse(result.content[0].text);
      expect(responseData.message).toContain('updated successfully');
    });
  });

  describe('handleDeleteIssue', () => {
    it('should make DELETE request', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({})
      };

      mockFetch.mockResolvedValue(mockResponse);

      const input = { issue_id: 123 };

      const result = await server.handleDeleteIssue(input);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/issues/123.json'),
        expect.objectContaining({ method: 'DELETE' })
      );

      const responseData = JSON.parse(result.content[0].text);
      expect(responseData.message).toContain('deleted successfully');
    });
  });

  describe('handleListProjects', () => {
    it('should make GET request to /projects.json', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          projects: [{
            id: 1,
            name: 'Test Project',
            identifier: 'test-project'
          }]
        })
      };

      mockFetch.mockResolvedValue(mockResponse);

      const result = await server.handleListProjects({});

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/projects.json'),
        expect.objectContaining({ method: 'GET' })
      );

      const responseData = JSON.parse(result.content[0].text);
      expect(responseData.projects).toHaveLength(1);
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors', async () => {
      const mockResponse = {
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: jest.fn().mockResolvedValue('{"errors":["Not found"]}')
      };

      mockFetch.mockResolvedValue(mockResponse);

      await expect(server.handleGetTicketDetail({ ticket_id: 999 }))
        .rejects.toThrow('HTTP 404: Not Found - Not found');
    });
  });
});