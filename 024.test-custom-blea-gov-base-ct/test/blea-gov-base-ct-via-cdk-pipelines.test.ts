import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { devParameter, devPipelineParameter } from '../parameter';
import { BLEAGovBaseCtPipelineStack } from '../lib/stack/blea-gov-base-ct-via-cdk-pipelines-stack';

// Mock the S3 lifecycle rule parameters
jest.mock('../parameter', () => {
  const originalModule = jest.requireActual('../parameter');
  return {
    ...originalModule,
    s3ExpirationDays: 366,
    s3ExpiredObjectDeleteDays: 30,
  };
});

test('Snapshot test for BLEAGovABaseCtPipeline Stack', () => {
  const app = new cdk.App();
  const stack = new BLEAGovBaseCtPipelineStack(app, 'Dev-BLEAGovBaseCtPipeilne', {
    env: devPipelineParameter.env,
    tags: {
      Repository: 'aws-samples/baseline-environment-on-aws',
      Environment: devPipelineParameter.envName,
    },

    targetParameters: [devParameter],
    sourceRepository: devPipelineParameter.sourceRepository,
    sourceBranch: devPipelineParameter.sourceBranch,
    sourceConnectionArn: devPipelineParameter.sourceConnectionArn,
  });

  // test with snapshot
  expect(Template.fromStack(stack)).toMatchSnapshot();
});
