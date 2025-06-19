import { Environment } from 'aws-cdk-lib';
import { SSMClient, GetParameterCommand, GetParameterCommandInput } from '@aws-sdk/client-ssm';

export interface AppParameter {
  env?: Environment;
  envName: string;
  securityNotifyEmail: string;
  securitySlackWorkspaceId?: string; // required if deploy via CLI
  securitySlackChannelId?: string; // required if deploy via CLI
  s3ExpirationDays?: number; // days until objects expire
  s3ExpiredObjectDeleteDays?: number; // days until expired objects are deleted
}

export interface PipelineParameter {
  env: Environment;
  envName: string;

  // AWS CodeStar Connections parameters for CDK Pipelines.
  // Only used in bin/blea-gov-base-ct-via-cdk-pipelines.ts
  sourceRepository: string;
  sourceBranch: string;
  sourceConnectionArn: string;
}

/**
 * Get parameter from SSM Parameter Store
 * @param paramName The name of the parameter in SSM Parameter Store
 * @param defaultValue Default value to return if parameter is not found
 * @returns The parameter value or default value if not found
 */
export async function getSSMParameter(paramName: string, defaultValue?: string): Promise<string> {
  try {
    const client = new SSMClient({});
    const input: GetParameterCommandInput = {
      Name: paramName,
      WithDecryption: true,
    };
    const command = new GetParameterCommand(input);
    const response = await client.send(command);
    return response.Parameter?.Value || defaultValue || '';
  } catch (error) {
    console.warn(`Failed to get parameter ${paramName} from SSM Parameter Store: ${error}`);
    if (defaultValue !== undefined) {
      console.warn(`Using default value: ${defaultValue}`);
      return defaultValue;
    }
    throw error;
  }
}

// Example for Development
export const devParameter: AppParameter = {
  envName: await getSSMParameter('/blea/dev/envName', 'Development'),
  securityNotifyEmail: await getSSMParameter('/blea/dev/securityNotifyEmail', 'notify-security@example.com'),
  securitySlackWorkspaceId: await getSSMParameter('/blea/dev/securitySlackWorkspaceId', 'TXXXXXXXXXX'),
  securitySlackChannelId: await getSSMParameter('/blea/dev/securitySlackChannelId', 'CXXXXXXXXXX'),
  s3ExpirationDays: Number(await getSSMParameter('/blea/dev/s3ExpirationDays', '366')),
  s3ExpiredObjectDeleteDays: Number(await getSSMParameter('/blea/dev/s3ExpiredObjectDeleteDays', '30')),
  // env: { account: '123456789012', region: 'ap-northeast-1' },
};

// Example for Staging
export const stagingParameter: AppParameter = {
  envName: 'Staging',
  securityNotifyEmail: 'notify-security@example.com',
  env: { account: '123456789012', region: 'ap-northeast-1' },
};

// Example for Pipeline Deployment
export const devPipelineParameter: PipelineParameter = {
  env: { account: '123456789012', region: 'ap-northeast-1' },
  envName: 'DevPipeline',
  sourceRepository: 'aws-samples/baseline-environment-on-aws',
  sourceBranch: 'main',
  sourceConnectionArn: 'arn:aws:codestar-connections:ap-northeast-1:xxxxxxxxxxxx:connection/example',
};
