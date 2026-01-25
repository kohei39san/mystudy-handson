import { Environment } from 'aws-cdk-lib';

/**
 * 環境変数から値を取得するヘルパー関数
 */
function getEnvOrDefault(key: string, defaultValue: string): string {
  return process.env[key] || defaultValue;
}

function getEnvOrThrow(key: string): string {
  const value = process.env[key];
  if (!value) {
    throw new Error(`環境変数 ${key} が設定されていません。`);
  }
  return value;
}

/**
 * 環境変数から配列を取得（カンマ区切り）
 */
function getEnvArray(key: string, defaultValue: string[] = []): string[] {
  const value = process.env[key];
  if (!value) {
    return defaultValue;
  }
  return value.split(',').map(v => v.trim());
}

/**
 * StackSets 用の拡張パラメータ
 * 通知の重複を避けるため、以下の3つのモードをサポート
 */
export type NotificationMode = 
  | 'centralized'    // 管理アカウントのみが通知を受け取る
  | 'regional'       // 各リージョンで異なる通知先を指定
  | 'none';           // 通知を無効化

export interface StackSetParameter {
  env: Environment;
  envName: string;
  
  // 通知設定
  notificationMode: NotificationMode;
  securityNotifyEmail?: string;           // centralized/regional モード用
  securitySlackWorkspaceId?: string;
  securitySlackChannelId?: string;
  
  // リージョン別オーバーライド（regional モード用）
  regionalNotifications?: {
    [region: string]: {
      email?: string;
      slackChannelId?: string;
    };
  };
  
  // S3 ライフサイクル設定
  s3ExpirationDays?: number;
  s3ExpiredObjectDeleteDays?: number;
  
  // StackSet対象アカウント・リージョン
  targetAccounts: string[];           // アカウントベースのデプロイ用
  targetOus?: string[];                // OUベースのデプロイ用（SERVICE_MANAGED）
  targetRegions: string[];
  managementAccountId: string;  // 管理アカウントID
  
  // StackSet IAM Roles (SELF_MANAGED mode)
  permissionModel?: 'SELF_MANAGED' | 'SERVICE_MANAGED';
  callAs?: 'SELF' | 'DELEGATED_ADMIN';
  administrationRoleArn?: string;
  executionRoleName?: string;
}

/**
 * マルチリージョン・マルチアカウント用のパラメータ
 * 
 * 環境変数から設定を読み込みます：
 * - STACK_SET_ACCOUNT: 管理アカウントID（必須）
 * - STACK_SET_REGION: 管理アカウントのリージョン（デフォルト: ap-northeast-1）
 * - STACK_SET_ENV_NAME: 環境名（デフォルト: Production）
 * - STACK_SET_NOTIFICATION_MODE: 通知モード（デフォルト: centralized）
 * - STACK_SET_NOTIFY_EMAIL: 通知先メールアドレス
 * - STACK_SET_SLACK_WORKSPACE_ID: Slack Workspace ID
 * - STACK_SET_SLACK_CHANNEL_ID: Slack Channel ID
 * - STACK_SET_TARGET_ACCOUNTS: ゲストアカウントID（カンマ区切り、必須）
 * - STACK_SET_TARGET_REGIONS: デプロイ対象リージョン（カンマ区切り、必須）
 * - STACK_SET_TARGET_OUS: デプロイ対象OU ID（カンマ区切り、SERVICE_MANAGED + OUベース用）
 */
export const stackSetParameter: StackSetParameter = {
  env: { 
    account: getEnvOrThrow('STACK_SET_ACCOUNT'),
    region: getEnvOrDefault('STACK_SET_REGION', 'ap-northeast-1'),
  },
  envName: getEnvOrDefault('STACK_SET_ENV_NAME', 'Production'),
  notificationMode: (getEnvOrDefault('STACK_SET_NOTIFICATION_MODE', 'centralized') as NotificationMode),
  
  // メール・Slack設定
  securityNotifyEmail: getEnvOrDefault('STACK_SET_NOTIFY_EMAIL', 'security-ops@example.com'),
  securitySlackWorkspaceId: process.env.STACK_SET_SLACK_WORKSPACE_ID,
  securitySlackChannelId: process.env.STACK_SET_SLACK_CHANNEL_ID,
  
  // S3ライフサイクル
  s3ExpirationDays: Number(getEnvOrDefault('STACK_SET_S3_EXPIRATION_DAYS', '366')),
  s3ExpiredObjectDeleteDays: Number(getEnvOrDefault('STACK_SET_S3_EXPIRED_DELETE_DAYS', '30')),
  
  // デプロイ対象（OU ベースの場合は targetOus を使用、アカウントベースの場合は targetAccounts を使用）
  targetAccounts: getEnvArray('STACK_SET_TARGET_ACCOUNTS'),
  targetRegions: getEnvArray('STACK_SET_TARGET_REGIONS'),
  managementAccountId: getEnvOrThrow('STACK_SET_ACCOUNT'),
  targetOus: getEnvArray('STACK_SET_TARGET_OUS'),
  
  // StackSet IAM Roles
  permissionModel: (process.env.STACK_SET_PERMISSION_MODEL as 'SELF_MANAGED' | 'SERVICE_MANAGED') || 'SELF_MANAGED',
  callAs: (process.env.STACK_SET_CALL_AS as 'SELF' | 'DELEGATED_ADMIN') || 'SELF',
  administrationRoleArn: process.env.STACK_SET_ADMIN_ROLE_ARN,
  executionRoleName: process.env.STACK_SET_EXECUTION_ROLE_NAME || 'AWSCloudFormationStackSetExecutionRole',
};
