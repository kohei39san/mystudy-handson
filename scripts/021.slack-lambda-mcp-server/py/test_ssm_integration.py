#!/usr/bin/env python3
"""
SSM パラメータストア統合のテストスクリプト
"""

import boto3
import json
from botocore.exceptions import ClientError
from local_test import get_ssm_parameter, load_config_from_ssm

def test_get_ssm_parameter():
    """get_ssm_parameter 関数のテスト"""
    print("SSM パラメータ取得のテスト...")
    
    # テスト用のパラメータ名
    test_param_name = '/slack-mcp-server/test/test-parameter'
    test_param_value = 'test-value'
    
    # SSM クライアント
    ssm_client = boto3.client('ssm')
    
    try:
        # テスト用のパラメータを作成
        ssm_client.put_parameter(
            Name=test_param_name,
            Value=test_param_value,
            Type='String',
            Overwrite=True
        )
        print(f"テスト用パラメータを作成しました: {test_param_name}")
        
        # パラメータを取得
        retrieved_value = get_ssm_parameter(test_param_name)
        print(f"取得した値: {retrieved_value}")
        
        # 値を検証
        assert retrieved_value == test_param_value, f"期待値: {test_param_value}, 実際の値: {retrieved_value}"
        print("パラメータ取得テスト成功")
        
        # テスト用のパラメータを削除
        ssm_client.delete_parameter(Name=test_param_name)
        print(f"テスト用パラメータを削除しました: {test_param_name}")
        
    except ClientError as e:
        print(f"AWS API エラー: {e}")
    except AssertionError as e:
        print(f"テスト失敗: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")

def test_load_config_from_ssm():
    """load_config_from_ssm 関数のテスト"""
    print("\nSSM からの設定読み込みテスト...")
    
    # テスト用のパラメータ
    test_params = {
        '/slack-mcp-server/test/userId': 'U87654321',
        '/slack-mcp-server/test/channelId': 'C87654321',
        '/slack-mcp-server/test/responseTs': '9876543210.654321',
        '/slack-mcp-server/test/text': 'これはテストメッセージです',
        '/slack-mcp-server/openrouter/api-key-param': '/test/openrouter/api-key',
        '/slack-mcp-server/openrouter/model': 'test-model',
        '/slack-mcp-server/dynamodb/table': 'test-table'
    }
    
    # SSM クライアント
    ssm_client = boto3.client('ssm')
    
    try:
        # テスト用のパラメータを作成
        for param_name, param_value in test_params.items():
            ssm_client.put_parameter(
                Name=param_name,
                Value=param_value,
                Type='String',
                Overwrite=True
            )
        print("テスト用パラメータを作成しました")
        
        # 設定を読み込み
        config = load_config_from_ssm()
        print(f"読み込んだ設定: {json.dumps(config, indent=2)}")
        
        # 値を検証
        assert config['userId'] == test_params['/slack-mcp-server/test/userId'], "userId が一致しません"
        assert config['channelId'] == test_params['/slack-mcp-server/test/channelId'], "channelId が一致しません"
        assert config['responseTs'] == test_params['/slack-mcp-server/test/responseTs'], "responseTs が一致しません"
        assert config['text'] == test_params['/slack-mcp-server/test/text'], "text が一致しません"
        assert config['OPENROUTER_API_KEY_PARAM'] == test_params['/slack-mcp-server/openrouter/api-key-param'], "OPENROUTER_API_KEY_PARAM が一致しません"
        assert config['OPENROUTER_MODEL'] == test_params['/slack-mcp-server/openrouter/model'], "OPENROUTER_MODEL が一致しません"
        assert config['DYNAMODB_TABLE'] == test_params['/slack-mcp-server/dynamodb/table'], "DYNAMODB_TABLE が一致しません"
        print("設定読み込みテスト成功")
        
        # テスト用のパラメータを削除
        for param_name in test_params.keys():
            ssm_client.delete_parameter(Name=param_name)
        print("テスト用パラメータを削除しました")
        
    except ClientError as e:
        print(f"AWS API エラー: {e}")
    except AssertionError as e:
        print(f"テスト失敗: {e}")
    except Exception as e:
        print(f"予期しないエラー: {e}")

def main():
    """メイン関数"""
    print("SSM パラメータストア統合テストを開始します")
    
    # 各テストを実行
    test_get_ssm_parameter()
    test_load_config_from_ssm()
    
    print("\nテスト完了")

if __name__ == "__main__":
    main()