import { Stage, StageProps, DefaultStackSynthesizer } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { BLEAGovBaseCtStack } from '../../../024.test-custom-blea-gov-base-ct/lib/stack/blea-gov-base-ct-stack';

export interface BLEAGovBaseCtTemplateStageProps extends StageProps {
  securityNotifyEmail: string;
  securitySlackWorkspaceId?: string;
  securitySlackChannelId?: string;
  s3ExpirationDays?: number;
  s3ExpiredObjectDeleteDays?: number;
}

/**
 * テンプレート生成用の Stage
 * 
 * この Stage は実際にデプロイされず、synth() でテンプレートを取得するためだけに使用されます。
 */
export class BLEAGovBaseCtTemplateStage extends Stage {
  constructor(scope: Construct, id: string, props: BLEAGovBaseCtTemplateStageProps) {
    super(scope, id, props);

    new BLEAGovBaseCtStack(this, 'BLEAGovBaseCt', {
      description: 'BLEA Governance Base for multi-accounts (uksb-1tupboc58) (tag:blea-gov-base-ct)',
      securityNotifyEmail: props.securityNotifyEmail,
      securitySlackWorkspaceId: props.securitySlackWorkspaceId,
      securitySlackChannelId: props.securitySlackChannelId,
      s3ExpirationDays: props.s3ExpirationDays,
      s3ExpiredObjectDeleteDays: props.s3ExpiredObjectDeleteDays,
      synthesizer: new DefaultStackSynthesizer({ generateBootstrapVersionRule: false }),
    });
  }
}
