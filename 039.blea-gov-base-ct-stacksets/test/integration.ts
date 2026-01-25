#!/usr/bin/env node
import 'dotenv/config';
import { CloudFormationClient, DescribeStackSetCommand, ListStackInstancesCommand } from '@aws-sdk/client-cloudformation';

/**
 * 統合テスト: StackSet のデプロイ確認
 * 
 * 実行前提:
 * - npx cdk deploy で StackSet マネージャースタックがデプロイ済み
 * - AWS 認証情報が設定済み
 */

const STACK_SET_NAME = 'BLEA-Governance-Base-ControlTower';
const REGION = process.env.AWS_REGION || 'ap-northeast-1';

interface TestResult {
  success: boolean;
  message: string;
  details?: any;
}

class StackSetTester {
  private client: CloudFormationClient;

  constructor(region: string) {
    this.client = new CloudFormationClient({ region });
  }

  /**
   * StackSet が存在するかチェック
   */
  async checkStackSetExists(): Promise<TestResult> {
    try {
      const command = new DescribeStackSetCommand({
        StackSetName: STACK_SET_NAME,
      });
      const response = await this.client.send(command);

      if (response.StackSet) {
        return {
          success: true,
          message: `✅ StackSet "${STACK_SET_NAME}" が存在します`,
          details: {
            status: response.StackSet.Status,
            description: response.StackSet.Description,
          },
        };
      } else {
        return {
          success: false,
          message: `❌ StackSet "${STACK_SET_NAME}" が見つかりません`,
        };
      }
    } catch (error: any) {
      return {
        success: false,
        message: `❌ StackSet の取得に失敗: ${error.message}`,
      };
    }
  }

  /**
   * StackSet のステータスチェック
   */
  async checkStackSetStatus(): Promise<TestResult> {
    try {
      const command = new DescribeStackSetCommand({
        StackSetName: STACK_SET_NAME,
      });
      const response = await this.client.send(command);

      const status = response.StackSet?.Status;
      if (status === 'ACTIVE') {
        return {
          success: true,
          message: `✅ StackSet のステータスは ACTIVE です`,
          details: { status },
        };
      } else {
        return {
          success: false,
          message: `⚠️ StackSet のステータスは ${status} です（期待: ACTIVE）`,
          details: { status },
        };
      }
    } catch (error: any) {
      return {
        success: false,
        message: `❌ StackSet ステータスの確認に失敗: ${error.message}`,
      };
    }
  }

  /**
   * StackInstances の一覧を取得
   */
  async checkStackInstances(): Promise<TestResult> {
    try {
      const command = new ListStackInstancesCommand({
        StackSetName: STACK_SET_NAME,
      });
      const response = await this.client.send(command);

      const instances = response.Summaries || [];
      if (instances.length === 0) {
        return {
          success: false,
          message: `⚠️ StackInstance が見つかりません`,
          details: { count: 0 },
        };
      }

      // ステータスごとにカウント
      const statusCount = instances.reduce((acc, instance) => {
        const status = instance.Status || 'UNKNOWN';
        acc[status] = (acc[status] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      const allCurrent = instances.every((i) => i.Status === 'CURRENT');

      return {
        success: allCurrent,
        message: allCurrent
          ? `✅ 全ての StackInstance (${instances.length}個) が CURRENT です`
          : `⚠️ 一部の StackInstance が CURRENT ではありません`,
        details: {
          totalCount: instances.length,
          statusBreakdown: statusCount,
          instances: instances.map((i) => ({
            account: i.Account,
            region: i.Region,
            status: i.Status,
          })),
        },
      };
    } catch (error: any) {
      return {
        success: false,
        message: `❌ StackInstances の確認に失敗: ${error.message}`,
      };
    }
  }

  /**
   * 全てのテストを実行
   */
  async runAllTests(): Promise<void> {
    console.log('🔍 StackSet 統合テストを開始します...\n');
    console.log(`リージョン: ${REGION}`);
    console.log(`StackSet 名: ${STACK_SET_NAME}\n`);

    const tests = [
      { name: 'StackSet の存在確認', fn: () => this.checkStackSetExists() },
      { name: 'StackSet ステータス確認', fn: () => this.checkStackSetStatus() },
      { name: 'StackInstances 確認', fn: () => this.checkStackInstances() },
    ];

    const results: TestResult[] = [];

    for (const test of tests) {
      console.log(`\n📋 ${test.name}:`);
      const result = await test.fn();
      results.push(result);

      console.log(`   ${result.message}`);
      if (result.details) {
        console.log(`   詳細:`, JSON.stringify(result.details, null, 2));
      }
    }

    // サマリー
    console.log('\n' + '='.repeat(60));
    console.log('📊 テスト結果サマリー:');
    console.log('='.repeat(60));

    const passedCount = results.filter((r) => r.success).length;
    const totalCount = results.length;

    console.log(`✅ 成功: ${passedCount}/${totalCount}`);
    console.log(`❌ 失敗: ${totalCount - passedCount}/${totalCount}`);

    if (passedCount === totalCount) {
      console.log('\n🎉 全てのテストが成功しました！');
      process.exit(0);
    } else {
      console.log('\n⚠️ 一部のテストが失敗しました。');
      process.exit(1);
    }
  }
}

// メイン実行
const tester = new StackSetTester(REGION);
tester.runAllTests().catch((error) => {
  console.error('❌ テストの実行中にエラーが発生しました:', error);
  process.exit(1);
});
