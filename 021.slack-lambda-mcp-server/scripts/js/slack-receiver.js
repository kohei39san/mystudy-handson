const { App } = require('@slack/bolt');
const AWS = require('aws-sdk');
const ssm = new AWS.SSM();
const sns = new AWS.SNS();

// 環境変数
const SLACK_BOT_TOKEN_PARAM = process.env.SLACK_BOT_TOKEN_PARAM || '/slack-bot/token';
const SLACK_SIGNING_SECRET_PARAM = process.env.SLACK_SIGNING_SECRET_PARAM || '/slack-bot/signing-secret';
const SLACK_APP_TOKEN_PARAM = process.env.SLACK_APP_TOKEN_PARAM || '/slack-bot/app-token';
const SNS_TOPIC_ARN = process.env.SNS_TOPIC_ARN;

// SSMからパラメータを取得する関数
async function getParameter(paramName) {
  const params = {
    Name: paramName,
    WithDecryption: true
  };
  
  try {
    const response = await ssm.getParameter(params).promise();
    return response.Parameter.Value;
  } catch (error) {
    console.error(`Error retrieving parameter ${paramName}:`, error);
    throw error;
  }
}

// 初期化関数
async function initializeApp() {
  try {
    // SSMからSlackの認証情報を取得
    const [botToken, signingSecret, appToken] = await Promise.all([
      getParameter(SLACK_BOT_TOKEN_PARAM),
      getParameter(SLACK_SIGNING_SECRET_PARAM),
      getParameter(SLACK_APP_TOKEN_PARAM)
    ]);

    // Slackアプリの初期化
    const app = new App({
      token: botToken,
      signingSecret: signingSecret,
      socketMode: true,
      appToken: appToken
    });

    // メンションされたときのイベントハンドラ
    app.event('app_mention', async ({ event, say, client }) => {
      try {
        // ユーザーからのメッセージ
        const text = event.text;
        const userId = event.user;
        const channelId = event.channel;
        const threadTs = event.thread_ts || event.ts;
        
        // 処理中メッセージを送信
        const response = await say({
          text: ":hourglass_flowing_sand: 考え中です...",
          thread_ts: threadTs,
          channel: channelId
        });
        
        // SNSにメッセージを送信
        const message = {
          userId: userId,
          channelId: channelId,
          threadTs: threadTs,
          messageTs: response.ts,
          text: text,
          responseTs: response.ts
        };
        
        await sns.publish({
          TopicArn: SNS_TOPIC_ARN,
          Message: JSON.stringify(message),
          MessageAttributes: {
            'messageType': {
              DataType: 'String',
              StringValue: 'slack_message'
            }
          }
        }).promise();
        
        console.log('Message sent to SNS:', message);
        
      } catch (error) {
        console.error('Error processing app_mention event:', error);
        await say({
          text: `:x: エラーが発生しました: ${error.message}`,
          thread_ts: event.thread_ts || event.ts
        });
      }
    });

    // DMのメッセージイベントハンドラ
    app.message(async ({ message, say }) => {
      // DMチャンネルの場合のみ処理
      if (message.channel_type !== 'im') return;
      
      try {
        // 処理中メッセージを送信
        const response = await say({
          text: ":hourglass_flowing_sand: 考え中です...",
          thread_ts: message.thread_ts || message.ts
        });
        
        // SNSにメッセージを送信
        const messageData = {
          userId: message.user,
          channelId: message.channel,
          threadTs: message.thread_ts || message.ts,
          messageTs: message.ts,
          text: message.text,
          responseTs: response.ts
        };
        
        await sns.publish({
          TopicArn: SNS_TOPIC_ARN,
          Message: JSON.stringify(messageData),
          MessageAttributes: {
            'messageType': {
              DataType: 'String',
              StringValue: 'slack_message'
            }
          }
        }).promise();
        
        console.log('Message sent to SNS:', messageData);
        
      } catch (error) {
        console.error('Error processing DM message:', error);
        await say({
          text: `:x: エラーが発生しました: ${error.message}`,
          thread_ts: message.thread_ts || message.ts
        });
      }
    });

    return app;
  } catch (error) {
    console.error('Failed to initialize app:', error);
    throw error;
  }
}

// Lambda handler
exports.handler = async (event, context) => {
  try {
    const app = await initializeApp();
    await app.start();
    console.log('⚡️ Bolt app is running!');
    
    // Lambda Function URLからのリクエストを処理
    if (event.requestContext) {
      // Function URLからのリクエスト
      return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Slack app is running' })
      };
    }
    
    return { statusCode: 200, body: 'Success' };
  } catch (error) {
    console.error('Error in Lambda handler:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};