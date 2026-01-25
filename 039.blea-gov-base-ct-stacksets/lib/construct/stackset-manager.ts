import { Stack, StackProps, CfnOutput } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { CfnStackSet, CfnStackSetProps } from 'aws-cdk-lib/aws-cloudformation';
import * as cfn from 'aws-cdk-lib/aws-cloudformation';

export interface StackSetManagerProps {
  stackSetName: string;
  description?: string;
  templateBody: string;  // CloudFormation テンプレート JSON 文字列
  capabilities?: string[];
  parameters?: {
    [key: string]: string;
  };
  targetAccounts?: string[];          // アカウントベースのデプロイ用
  targetOus?: string[];               // OUベースのデプロイ用
  targetRegions: string[];
  autoDeploymentEnabled?: boolean;  // Control Tower OUベースの自動デプロイ
  permissionModel?: 'SELF_MANAGED' | 'SERVICE_MANAGED';
  callAs?: 'SELF' | 'DELEGATED_ADMIN';  // SERVICE_MANAGEDでの呼び出し元
  administrationRoleArn?: string;  // SELF_MANAGED用の管理ロールARN
  executionRoleName?: string;  // ターゲットアカウントの実行ロール名
}

export class StackSetManager extends Construct {
  public readonly stackSet: CfnStackSet;

  constructor(scope: Construct, id: string, props: StackSetManagerProps) {
    super(scope, id);

    // CloudFormation テンプレートは既に文字列として渡される
    const templateBody = props.templateBody;

    // deploymentTargets を構築: OUベースまたはアカウントベース
    const deploymentTargets: any = {};
    if (props.targetOus && props.targetOus.length > 0) {
      // OUベースのデプロイメント
      deploymentTargets.organizationalUnitIds = props.targetOus;
    } else if (props.targetAccounts && props.targetAccounts.length > 0) {
      // アカウントベースのデプロイメント
      deploymentTargets.accounts = props.targetAccounts;
    } else {
      throw new Error('targetOus または targetAccounts のいずれかを指定してください。');
    }

    // StackSet を作成
    this.stackSet = new CfnStackSet(this, 'StackSet', {
      stackSetName: props.stackSetName,
      description: props.description,
      templateBody: templateBody,
      capabilities: props.capabilities || ['CAPABILITY_NAMED_IAM'],
      parameters: this.convertParameters(props.parameters),
      permissionModel: props.permissionModel || 'SELF_MANAGED',
      callAs: props.callAs,
      // SELF_MANAGEDの場合のみIAMロールを指定
      administrationRoleArn: props.permissionModel === 'SELF_MANAGED' ? props.administrationRoleArn : undefined,
      executionRoleName: props.permissionModel === 'SELF_MANAGED' ? (props.executionRoleName || 'AWSCloudFormationStackSetExecutionRole') : undefined,
      // SERVICE_MANAGEDの場合はautoDeploymentが必須
      autoDeployment: props.permissionModel === 'SERVICE_MANAGED' 
        ? {
            enabled: true,
            retainStacksOnAccountRemoval: false,
          }
        : (props.autoDeploymentEnabled
          ? {
              enabled: true,
              retainStacksOnAccountRemoval: true,
            }
          : undefined),
      stackInstancesGroup: [
        {
          deploymentTargets: deploymentTargets,
          regions: props.targetRegions,
        },
      ],
    });

    new CfnOutput(this, 'StackSetId', {
      value: this.stackSet.ref,
      description: 'StackSet ID',
    });
  }

  /**
   * パラメータを CloudFormation StackSet の形式 [{parameterKey, parameterValue}] に変換する
   */
  private convertParameters(
    parameters?: Record<string, string>
  ): Array<{ parameterKey: string; parameterValue: string }> | undefined {
    if (!parameters) {
      return undefined;
    }

    return Object.entries(parameters).map(([key, value]) => ({
      parameterKey: key,
      parameterValue: value,
    }));
  }
}
