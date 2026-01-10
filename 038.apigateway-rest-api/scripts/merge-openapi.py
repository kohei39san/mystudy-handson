#!/usr/bin/env python3
"""
OpenAPI仕様書マージスクリプト

分割されたOpenAPI仕様書ファイルを1つのファイルにマージします。
- base.yml: 基本情報とサーバー設定
- components/schemas.yml: スキーマ定義
- paths/*.yml: エンドポイント定義

また、CloudFormationのプレースホルダーを置換する機能も提供します。
"""

import os
import sys
import yaml
import argparse
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    YAMLファイルを読み込む
    
    Args:
        file_path: YAMLファイルのパス
        
    Returns:
        読み込んだYAMLデータ
        
    Raises:
        FileNotFoundError: ファイルが見つからない場合
        yaml.YAMLError: YAML解析エラーの場合
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"ファイルが見つかりません: {file_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"YAML解析エラー in {file_path}: {e}")
        raise


def merge_dict_recursive(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    辞書を再帰的にマージする
    
    Args:
        base: ベースとなる辞書
        update: マージする辞書
        
    Returns:
        マージされた辞書
    """
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dict_recursive(result[key], value)
        else:
            result[key] = value
    
    return result


def replace_placeholders(content: str, replacements: Dict[str, str]) -> str:
    """
    文字列内のプレースホルダーを置換する
    
    Args:
        content: 置換対象の文字列
        replacements: 置換マップ（プレースホルダー名 -> 置換値）
        
    Returns:
        置換後の文字列
    """
    for placeholder, value in replacements.items():
        pattern = r'\{\{' + re.escape(placeholder) + r'\}\}'
        content = re.sub(pattern, value, content)
    
    return content


def merge_openapi_files(
    openapi_dir: Path, 
    output_file: Path, 
    replacements: Optional[Dict[str, str]] = None
) -> None:
    """
    OpenAPI仕様書ファイルをマージする
    
    Args:
        openapi_dir: OpenAPIファイルが格納されているディレクトリ
        output_file: 出力ファイルのパス
        replacements: プレースホルダー置換マップ
    """
    logger.info("OpenAPI仕様書のマージを開始します")
    
    # ベースファイルを読み込み
    base_file = openapi_dir / "base.yml"
    if not base_file.exists():
        raise FileNotFoundError(f"ベースファイルが見つかりません: {base_file}")
    
    logger.info(f"ベースファイルを読み込み: {base_file}")
    merged_spec = load_yaml_file(base_file)
    
    # コンポーネントファイルをマージ
    components_dir = openapi_dir / "components"
    if components_dir.exists():
        logger.info("コンポーネントファイルをマージ中...")
        for component_file in sorted(components_dir.glob("*.yml")):
            logger.info(f"  - {component_file.name}")
            component_data = load_yaml_file(component_file)
            merged_spec = merge_dict_recursive(merged_spec, component_data)
    
    # パスファイルをマージ
    paths_dir = openapi_dir / "paths"
    if paths_dir.exists():
        logger.info("パスファイルをマージ中...")
        for path_file in sorted(paths_dir.glob("*.yml")):
            logger.info(f"  - {path_file.name}")
            path_data = load_yaml_file(path_file)
            merged_spec = merge_dict_recursive(merged_spec, path_data)
    
    # マージされた仕様書をYAML文字列に変換
    yaml_content = yaml.dump(
        merged_spec,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        indent=2
    )
    
    # プレースホルダーを置換
    if replacements:
        logger.info("プレースホルダーを置換中...")
        for placeholder, value in replacements.items():
            logger.info(f"  - {placeholder} -> {value}")
        yaml_content = replace_placeholders(yaml_content, replacements)
    
    # 出力ファイルに書き込み
    logger.info(f"マージされた仕様書を出力: {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    logger.info("OpenAPI仕様書のマージが完了しました")


def load_replacements_from_env() -> Dict[str, str]:
    """
    環境変数からプレースホルダー置換マップを作成する
    
    Returns:
        置換マップ
    """
    replacements = {}
    
    # 環境変数から値を取得
    env_mappings = {
        'AWS_REGION': 'AWS_REGION',
        'BACKEND_LAMBDA_ARN': 'BACKEND_LAMBDA_ARN',
        'API_GATEWAY_ROLE_ARN': 'API_GATEWAY_ROLE_ARN'
    }
    
    for placeholder, env_var in env_mappings.items():
        value = os.environ.get(env_var)
        if value:
            replacements[placeholder] = value
            logger.info(f"環境変数から取得: {placeholder} = {value}")
    
    return replacements


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="OpenAPI仕様書マージスクリプト",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--openapi-dir",
        type=Path,
        default=Path("openapi"),
        help="OpenAPIファイルが格納されているディレクトリ (デフォルト: openapi)"
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("openapi.yml"),
        help="出力ファイルのパス (デフォルト: openapi.yml)"
    )
    
    parser.add_argument(
        "--replace-placeholders",
        action="store_true",
        help="環境変数からプレースホルダーを置換する"
    )
    
    args = parser.parse_args()
    
    try:
        # プレースホルダー置換マップを準備
        replacements = None
        if args.replace_placeholders:
            replacements = load_replacements_from_env()
        
        merge_openapi_files(args.openapi_dir, args.output, replacements)
        logger.info("処理が正常に完了しました")
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
