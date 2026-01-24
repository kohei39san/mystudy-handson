import { Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { StackSetManager } from '../construct/stackset-manager';
import { StackSetParameter } from '../../parameter';
import { BLEAGovBaseCtTemplateStage } from '../stage/blea-gov-base-ct-template-stage';

export interface BLEAGovBaseCtStackSetStackProps extends StackProps {
  stackSetParameter: StackSetParameter;
}

/**
 * StackSet マネージャースタック
 * 
 * このスタックは管理アカウントにデプロイされ、
 * ゲストアカウントへの BLEA Governance Base の自動デプロイを管理します。
 */
export class BLEAGovBaseCtStackSetStack extends Stack {
  constructor(scope: Construct, id: string, props: BLEAGovBaseCtStackSetStackProps) {
    super(scope, id, props);

    const params = props.stackSetParameter;

    // 通知モードに基づいてパラメータを構築
    const notificationParams = this.buildNotificationParameters(params);

    // テンプレート生成用の Stage を作成
    const templateStage = new BLEAGovBaseCtTemplateStage(this, 'TemplateStage', {
      env: params.env,
      securityNotifyEmail: params.securityNotifyEmail || 'noop@example.com',
      securitySlackWorkspaceId: params.securitySlackWorkspaceId,
      securitySlackChannelId: params.securitySlackChannelId,
      s3ExpirationDays: params.s3ExpirationDays,
      s3ExpiredObjectDeleteDays: params.s3ExpiredObjectDeleteDays,
    });

    // Stage を synth してテンプレートを取得
    const template = templateStage.synth().stacks[0].template;

    // StackSet を作成
    new StackSetManager(this, 'BLEAGovBaseCtStackSetManager', {
      stackSetName: 'BLEA-Governance-Base-ControlTower',
      description: 'BLEA Governance Base for AWS Control Tower multi-accounts and multi-regions',
      
      // Stage から取得したテンプレートを直接渡す
      templateBody: JSON.stringify(template),
      
      capabilities: ['CAPABILITY_NAMED_IAM'],
      
      // StackSet に渡すパラメータ
      parameters: {
        ...notificationParams,
        S3ExpirationDays: params.s3ExpirationDays?.toString() || '366',
        S3ExpiredObjectDeleteDays: params.s3ExpiredObjectDeleteDays?.toString() || '30',
      },
      
      targetAccounts: params.targetAccounts,
      targetRegions: params.targetRegions,
      
      // Service Managed でない場合は SELF_MANAGED を使用
      permissionModel: 'SELF_MANAGED',
    });
  }

  /**
   * 通知モードに基づいて、CloudFormation パラメータを構築
   */
  private buildNotificationParameters(params: StackSetParameter): Record<string, string> {
    const result: Record<string, string> = {};

    switch (params.notificationMode) {
      case 'centralized':
        // 管理アカウントのみが通知を受け取る
        result['NotificationMode'] = 'centralized';
        result['SecurityNotifyEmail'] = params.securityNotifyEmail || '';
        result['SecuritySlackWorkspaceId'] = params.securitySlackWorkspaceId || '';
        result['SecuritySlackChannelId'] = params.securitySlackChannelId || '';
        break;

      case 'regional':
        // リージョン別に異なる通知先を指定
        result['NotificationMode'] = 'regional';
        if (params.regionalNotifications) {
          result['RegionalNotifications'] = JSON.stringify(params.regionalNotifications);
        }
        break;

      case 'none':
        // 通知を無効化
        result['NotificationMode'] = 'none';
        break;

      default:
        // デフォルト: centralized
        result['NotificationMode'] = 'centralized';
        result['SecurityNotifyEmail'] = params.securityNotifyEmail || '';
    }

    return result;
  }
}
