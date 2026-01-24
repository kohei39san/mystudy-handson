import * as cdk from 'aws-cdk-lib';
import { BLEAGovBaseCtStackSetStack } from '../lib/stack/blea-gov-base-ct-stackset-manager-stack';
import { stackSetParameter } from '../parameter';

const app = new cdk.App();

/**
 * StackSet マネージャースタック
 * 
 * 使用方法：
 * 1. parameter.ts で通知モードと対象アカウント・リージョンを設定
 * 
 * 2. このスタックをデプロイ（管理アカウントで実行）
 *    npx cdk deploy Dev-BLEAGovBaseCtStackSetManager
 * 
 * テンプレートは CDK Stage の synth() を使用して自動生成されます。
 * 事前に 024 ディレクトリで cdk synth を実行する必要はありません。
 * 
 * 通知の制御方法：
 * - parameter.ts で notificationMode を設定
 *   - 'centralized': 管理アカウントのみが通知を受け取る
 *   - 'regional': 各リージョンで異なる通知先を指定
 *   - 'none': 通知を完全に無効化
 */
new BLEAGovBaseCtStackSetStack(app, 'Dev-BLEAGovBaseCtStackSetManager', {
  description: 'StackSet Manager for BLEA Governance Base (tag:blea-gov-base-ct-stacksets)',
  env: {
    account: stackSetParameter.env.account || process.env.CDK_DEFAULT_ACCOUNT,
    region: stackSetParameter.env.region || process.env.CDK_DEFAULT_REGION,
  },
  tags: {
    Repository: 'aws-samples/baseline-environment-on-aws',
    Environment: stackSetParameter.envName,
    Type: 'StackSetManager',
  },

  stackSetParameter: stackSetParameter,
});

app.synth();
