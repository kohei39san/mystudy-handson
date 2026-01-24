import { Environment } from 'aws-cdk-lib';

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
  targetAccounts: string[];
  targetRegions: string[];
  managementAccountId: string;  // 管理アカウントID
}

export interface StackSetDeploymentParameter {
  env: Environment;
  envName: string;
  organizationId: string;
  sourceRepository?: string;
  sourceBranch?: string;
}

/**
 * マルチリージョン・マルチアカウント用のパラメータ例
 */
export const stackSetParameter: StackSetParameter = {
  env: { account: '123456789012', region: 'ap-northeast-1' }, // 管理アカウント
  envName: 'Production',
  notificationMode: 'centralized',
  
  // 方法1: 管理アカウントのみが通知を受け取る
  securityNotifyEmail: 'security-ops@example.com',
  securitySlackWorkspaceId: 'TXXXXXXXXXX',
  securitySlackChannelId: 'CXXXXXXXXXX',
  
  // 方法2: リージョン別に異なる通知先を指定
  // notificationMode: 'regional',
  // regionalNotifications: {
  //   'ap-northeast-1': {
  //     email: 'security-ap@example.com',
  //     slackChannelId: 'CAPXXXXXXXXX',
  //   },
  //   'us-east-1': {
  //     email: 'security-us@example.com',
  //     slackChannelId: 'CUSXXXXXXXXX',
  //   },
  //   'eu-west-1': {
  //     email: 'security-eu@example.com',
  //     slackChannelId: 'CEUXXXXXXXXX',
  //   },
  // },
  
  // 方法3: 通知を無効化
  // notificationMode: 'none',
  
  s3ExpirationDays: 366,
  s3ExpiredObjectDeleteDays: 30,
  
  targetAccounts: ['210987654321', '321098765432'],  // ゲストアカウント
  targetRegions: ['ap-northeast-1', 'us-east-1', 'eu-west-1'],
  managementAccountId: '123456789012',
};

export const stackSetDeploymentParameter: StackSetDeploymentParameter = {
  env: { account: '123456789012', region: 'ap-northeast-1' },
  envName: 'Production-StackSets',
  organizationId: 'o-xxxxxxxxxx',
  sourceRepository: 'aws-samples/baseline-environment-on-aws',
  sourceBranch: 'main',
};
