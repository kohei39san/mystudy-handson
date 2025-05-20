const { App, AwsLambdaReceiver } = require('@slack/bolt');
const AWS = require('aws-sdk');

// Initialize AWS services
const ssm = new AWS.SSM();
const lambda = new AWS.Lambda();
const dynamoDB = new AWS.DynamoDB.DocumentClient();

// Initialize the AwsLambdaReceiver
const awsLambdaReceiver = new AwsLambdaReceiver({
  signingSecret: process.env.SLACK_SIGNING_SECRET,
});

// Load parameters from SSM Parameter Store
async function getParameter(name) {
  const params = {
    Name: name,
    WithDecryption: true
  };
  
  const response = await ssm.getParameter(params).promise();
  return response.Parameter.Value;
}

// Initialize the app with the AWS Lambda receiver
let app;
let initialized = false;

async function initializeApp() {
  if (initialized) return;
  
  try {
    const slackBotToken = await getParameter('/slack-mcp-bot/SLACK_BOT_TOKEN');
    const slackSigningSecret = await getParameter('/slack-mcp-bot/SLACK_SIGNING_SECRET');
    
    app = new App({
      token: slackBotToken,
      signingSecret: slackSigningSecret,
      receiver: awsLambdaReceiver,
      processBeforeResponse: true
    });
    
    // Set up event listeners after app is initialized
    setupEventListeners();
    
    initialized = true;
    console.log('App initialized successfully');
  } catch (error) {
    console.error('Error initializing app:', error);
    throw error;
  }
}

function setupEventListeners() {
  // Handle direct messages
  app.message(async ({ message, say, client }) => {
    // Ignore messages from bots
    if (message.subtype === 'bot_message') return;
    
    // Only process direct messages or messages that mention the bot
    if (message.channel_type !== 'im' && !message.text.includes(`<@${process.env.BOT_USER_ID}>`)) return;
    
    try {
      // Acknowledge receipt of the message
      await say({
        text: "I'm processing your request...",
        thread_ts: message.ts
      });
      
      // Store the message in DynamoDB
      const timestamp = new Date().toISOString();
      const conversationId = message.channel + '-' + (message.thread_ts || message.ts);
      
      await dynamoDB.put({
        TableName: process.env.DYNAMODB_TABLE,
        Item: {
          conversationId: conversationId,
          messageId: message.ts,
          userId: message.user,
          channelId: message.channel,
          text: message.text,
          timestamp: timestamp,
          type: 'user_message',
          ttl: Math.floor(Date.now() / 1000) + (60 * 60 * 24 * 30) // 30 days TTL
        }
      }).promise();
      
      // Get conversation history from DynamoDB
      const historyParams = {
        TableName: process.env.DYNAMODB_TABLE,
        KeyConditionExpression: 'conversationId = :conversationId',
        ExpressionAttributeValues: {
          ':conversationId': conversationId
        },
        Limit: 10,
        ScanIndexForward: false // Get most recent messages first
      };
      
      const historyResult = await dynamoDB.query(historyParams).promise();
      const conversationHistory = historyResult.Items.reverse();
      
      // Invoke the MCP Server Lambda
      const payload = {
        message: message.text,
        userId: message.user,
        channelId: message.channel,
        threadTs: message.thread_ts || message.ts,
        conversationHistory: conversationHistory
      };
      
      const mcpResponse = await lambda.invoke({
        FunctionName: process.env.MCP_SERVER_LAMBDA,
        InvocationType: 'RequestResponse',
        Payload: JSON.stringify(payload)
      }).promise();
      
      const mcpResult = JSON.parse(mcpResponse.Payload);
      
      if (mcpResult.error) {
        await say({
          text: `Error: ${mcpResult.error}`,
          thread_ts: message.ts
        });
        return;
      }
      
      // Send the response back to Slack
      await say({
        text: mcpResult.response,
        thread_ts: message.ts
      });
      
      // Store the bot's response in DynamoDB
      await dynamoDB.put({
        TableName: process.env.DYNAMODB_TABLE,
        Item: {
          conversationId: conversationId,
          messageId: Date.now().toString(),
          userId: process.env.BOT_USER_ID,
          channelId: message.channel,
          text: mcpResult.response,
          timestamp: new Date().toISOString(),
          type: 'bot_response',
          ttl: Math.floor(Date.now() / 1000) + (60 * 60 * 24 * 30) // 30 days TTL
        }
      }).promise();
      
    } catch (error) {
      console.error('Error processing message:', error);
      
      // Send error message back to Slack
      await say({
        text: `Sorry, I encountered an error: ${error.message}`,
        thread_ts: message.ts
      });
    }
  });
  
  // Handle app_mention events
  app.event('app_mention', async ({ event, say }) => {
    try {
      // Process similar to direct messages
      await say({
        text: "I'm processing your request...",
        thread_ts: event.ts
      });
      
      // Store the message in DynamoDB
      const timestamp = new Date().toISOString();
      const conversationId = event.channel + '-' + (event.thread_ts || event.ts);
      
      await dynamoDB.put({
        TableName: process.env.DYNAMODB_TABLE,
        Item: {
          conversationId: conversationId,
          messageId: event.ts,
          userId: event.user,
          channelId: event.channel,
          text: event.text,
          timestamp: timestamp,
          type: 'user_mention',
          ttl: Math.floor(Date.now() / 1000) + (60 * 60 * 24 * 30) // 30 days TTL
        }
      }).promise();
      
      // Get conversation history from DynamoDB
      const historyParams = {
        TableName: process.env.DYNAMODB_TABLE,
        KeyConditionExpression: 'conversationId = :conversationId',
        ExpressionAttributeValues: {
          ':conversationId': conversationId
        },
        Limit: 10,
        ScanIndexForward: false // Get most recent messages first
      };
      
      const historyResult = await dynamoDB.query(historyParams).promise();
      const conversationHistory = historyResult.Items.reverse();
      
      // Invoke the MCP Server Lambda
      const payload = {
        message: event.text,
        userId: event.user,
        channelId: event.channel,
        threadTs: event.thread_ts || event.ts,
        conversationHistory: conversationHistory
      };
      
      const mcpResponse = await lambda.invoke({
        FunctionName: process.env.MCP_SERVER_LAMBDA,
        InvocationType: 'RequestResponse',
        Payload: JSON.stringify(payload)
      }).promise();
      
      const mcpResult = JSON.parse(mcpResponse.Payload);
      
      if (mcpResult.error) {
        await say({
          text: `Error: ${mcpResult.error}`,
          thread_ts: event.ts
        });
        return;
      }
      
      // Send the response back to Slack
      await say({
        text: mcpResult.response,
        thread_ts: event.ts
      });
      
      // Store the bot's response in DynamoDB
      await dynamoDB.put({
        TableName: process.env.DYNAMODB_TABLE,
        Item: {
          conversationId: conversationId,
          messageId: Date.now().toString(),
          userId: process.env.BOT_USER_ID,
          channelId: event.channel,
          text: mcpResult.response,
          timestamp: new Date().toISOString(),
          type: 'bot_response',
          ttl: Math.floor(Date.now() / 1000) + (60 * 60 * 24 * 30) // 30 days TTL
        }
      }).promise();
      
    } catch (error) {
      console.error('Error processing app_mention:', error);
      
      // Send error message back to Slack
      await say({
        text: `Sorry, I encountered an error: ${error.message}`,
        thread_ts: event.ts
      });
    }
  });
}

// Lambda handler
exports.handler = async (event, context) => {
  // Initialize the app if it hasn't been initialized yet
  if (!initialized) {
    await initializeApp();
  }
  
  // Handle the Lambda event
  const handler = await awsLambdaReceiver.start();
  return handler(event, context);
};