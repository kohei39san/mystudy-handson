import { Stack, StackProps, CfnOutput } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import {
  CfnStackSet,
  CfnStackInstances,
  CfnStackSetProps,
} from 'aws-cdk-lib/aws-cloudformation';

export interface StackSetManagerProps {
  stackSetName: string;
  description?: string;
  templateBody: string;  // CloudFormation テンプレート JSON 文字列
  capabilities?: string[];
  parameters?: {
    [key: string]: string;
  };
  targetAccounts: string[];
  targetRegions: string[];
  autoDeploymentEnabled?: boolean;  // Control Tower OUベースの自動デプロイ
  permissionModel?: 'SELF_MANAGED' | 'SERVICE_MANAGED';
}

export class StackSetManager extends Construct {
  public readonly stackSet: CfnStackSet;

  constructor(scope: Construct, id: string, props: StackSetManagerProps) {
    super(scope, id);

    // CloudFormation テンプレートは既に文字列として渡される
    const templateBody = props.templateBody;

    // StackSet を作成
    this.stackSet = new CfnStackSet(this, 'StackSet', {
      stackSetName: props.stackSetName,
      description: props.description,
      templateBody: templateBody,
      capabilities: props.capabilities || ['CAPABILITY_NAMED_IAM'],
      parameters: this.convertParameters(props.parameters),
      permissionModel: props.permissionModel || 'SELF_MANAGED',
      autoDeployment: props.autoDeploymentEnabled
        ? {
            enabled: true,
            retain: true,
          }
        : undefined,
    });

    // StackSet インスタンスをデプロイ
    new CfnStackInstances(this, 'StackInstances', {
      stackSetName: this.stackSet.stackSetName,
      accounts: props.targetAccounts,
      regions: props.targetRegions,
      deploymentPreferences: {
        maxConcurrentPercentage: 100,
        failureTolerancePercentage: 0,
      },
    });

    new CfnOutput(this, 'StackSetId', {
      value: this.stackSet.ref,
      description: 'StackSet ID',
    });
  }

  /**
   * CloudFormation テンプレート JSON を読み込む
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
