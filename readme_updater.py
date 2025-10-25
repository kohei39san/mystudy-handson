#!/usr/bin/env python3
"""
README.md Update and Infrastructure Diagram Creation Tool

This script processes the 3 oldest directories matching pattern [0-9][0-9][0-9].*
and updates their README.md files with accurate infrastructure descriptions.
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Try to import yaml, but make it optional
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    print("Warning: PyYAML not available. CloudFormation YAML parsing will be limited.")

class DirectoryAnalyzer:
    """Analyzes directories and identifies infrastructure files."""
    
    def __init__(self, workspace_path: str = '/workspace'):
        self.workspace_path = workspace_path
        self.pattern = re.compile(r'^[0-9]{3}\..*$')
    
    def find_matching_directories(self) -> List[Dict[str, Any]]:
        """Find all directories matching the pattern [0-9][0-9][0-9].*"""
        matching_dirs = []
        
        try:
            for item in os.listdir(self.workspace_path):
                item_path = os.path.join(self.workspace_path, item)
                if os.path.isdir(item_path) and self.pattern.match(item):
                    stat_info = os.stat(item_path)
                    mtime = stat_info.st_mtime
                    matching_dirs.append({
                        'name': item,
                        'path': item_path,
                        'mtime': mtime,
                        'mtime_readable': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
        except OSError as e:
            print(f"Error reading workspace directory: {e}")
            return []
        
        return matching_dirs
    
    def select_oldest_directories(self, directories: List[Dict[str, Any]], count: int = 3) -> List[Dict[str, Any]]:
        """Select the oldest directories by modification time."""
        sorted_dirs = sorted(directories, key=lambda x: x['mtime'])
        return sorted_dirs[:count]
    
    def analyze_directory_structure(self, directory_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the structure of a directory to identify infrastructure files."""
        dir_path = directory_info['path']
        analysis = {
            'name': directory_info['name'],
            'path': dir_path,
            'mtime_readable': directory_info['mtime_readable'],
            'has_readme': False,
            'terraform_files': [],
            'cloudformation_files': [],
            'has_existing_diagram': False,
            'src_directory': None,
            'readme_path': None
        }
        
        try:
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                
                if item.lower() == 'readme.md':
                    analysis['has_readme'] = True
                    analysis['readme_path'] = item_path
                elif item.endswith('.tf'):
                    analysis['terraform_files'].append(item_path)
                elif item.endswith(('.yaml', '.yml', '.json')) and not item.startswith('.'):
                    analysis['cloudformation_files'].append(item_path)
                elif item == 'src' and os.path.isdir(item_path):
                    analysis['src_directory'] = item_path
                    src_files = os.listdir(item_path)
                    if 'architecture.drawio' in src_files:
                        analysis['has_existing_diagram'] = True
        
        except OSError as e:
            print(f"Error analyzing directory {dir_path}: {e}")
        
        return analysis

class TerraformParser:
    """Parses Terraform files to extract AWS resources."""
    
    def __init__(self):
        self.aws_resources = {}
    
    def parse_terraform_files(self, tf_files: List[str]) -> Dict[str, Any]:
        """Parse Terraform files and extract AWS resources."""
        resources = {
            'vpc': [],
            'subnets': [],
            'security_groups': [],
            'ec2_instances': [],
            'rds_instances': [],
            'lambda_functions': [],
            'iam_roles': [],
            's3_buckets': [],
            'load_balancers': [],
            'other_resources': []
        }
        
        for tf_file in tf_files:
            try:
                with open(tf_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    resources.update(self._extract_resources_from_content(content, tf_file))
            except Exception as e:
                print(f"Error parsing {tf_file}: {e}")
        
        return resources
    
    def _extract_resources_from_content(self, content: str, filename: str) -> Dict[str, Any]:
        """Extract AWS resources from Terraform content."""
        resources = {
            'vpc': [],
            'subnets': [],
            'security_groups': [],
            'ec2_instances': [],
            'rds_instances': [],
            'lambda_functions': [],
            'iam_roles': [],
            's3_buckets': [],
            'load_balancers': [],
            'other_resources': []
        }
        
        # Simple regex patterns to identify AWS resources
        patterns = {
            'vpc': r'resource\s+"aws_vpc"\s+"([^"]+)"',
            'subnets': r'resource\s+"aws_subnet"\s+"([^"]+)"',
            'security_groups': r'resource\s+"aws_security_group"\s+"([^"]+)"',
            'ec2_instances': r'resource\s+"aws_instance"\s+"([^"]+)"',
            'rds_instances': r'resource\s+"aws_db_instance"\s+"([^"]+)"',
            'lambda_functions': r'resource\s+"aws_lambda_function"\s+"([^"]+)"',
            'iam_roles': r'resource\s+"aws_iam_role"\s+"([^"]+)"',
            's3_buckets': r'resource\s+"aws_s3_bucket"\s+"([^"]+)"',
            'load_balancers': r'resource\s+"aws_lb"\s+"([^"]+)"'
        }
        
        for resource_type, pattern in patterns.items():
            matches = re.findall(pattern, content)
            for match in matches:
                resources[resource_type].append({
                    'name': match,
                    'file': filename,
                    'type': resource_type
                })
        
        return resources

class DiagramGenerator:
    """Generates DrawIO diagrams based on infrastructure analysis."""
    
    def __init__(self, template_path: str = '/workspace/src/aws-template.drawio'):
        self.template_path = template_path
        self.template_content = self._load_template()
    
    def _load_template(self) -> str:
        """Load the AWS template DrawIO file."""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading template: {e}")
            return ""
    
    def generate_diagram(self, resources: Dict[str, Any], output_path: str) -> bool:
        """Generate a new DrawIO diagram based on resources."""
        try:
            # Create a basic diagram structure
            diagram_content = self._create_diagram_from_resources(resources)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(diagram_content)
            
            print(f"Generated diagram: {output_path}")
            return True
        except Exception as e:
            print(f"Error generating diagram: {e}")
            return False
    
    def _create_diagram_from_resources(self, resources: Dict[str, Any]) -> str:
        """Create DrawIO XML content based on resources."""
        # Basic DrawIO structure with AWS resources
        diagram_header = '''<mxfile host="65bd71144e">
    <diagram name="アーキテクチャ図" id="architecture">
        <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
            <root>
                <mxCell id="0"/>
                <mxCell id="1" parent="0"/>'''
        
        diagram_footer = '''            </root>
        </mxGraphModel>
    </diagram>
</mxfile>'''
        
        # Generate cells for each resource type
        cells = []
        y_position = 100
        
        # VPC container
        if resources.get('vpc'):
            cells.append(self._create_vpc_cell(y_position))
            y_position += 200
        
        # EC2 instances
        if resources.get('ec2_instances'):
            for i, instance in enumerate(resources['ec2_instances']):
                cells.append(self._create_ec2_cell(instance, 100 + i * 150, y_position))
        
        # Add other resources as needed
        
        return diagram_header + '\n'.join(cells) + diagram_footer
    
    def _create_vpc_cell(self, y_pos: int) -> str:
        """Create a VPC cell in DrawIO format."""
        return f'''                <mxCell id="vpc-1" value="VPC" style="points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontSize=12;fontStyle=0;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fillColor=none;verticalAlign=top;align=left;spacingLeft=30;fontColor=#AAB7B8;dashed=0;" vertex="1" parent="1">
                    <mxGeometry x="50" y="{y_pos}" width="400" height="300" as="geometry"/>
                </mxCell>'''
    
    def _create_ec2_cell(self, instance: Dict[str, Any], x_pos: int, y_pos: int) -> str:
        """Create an EC2 instance cell in DrawIO format."""
        return f'''                <mxCell id="ec2-{instance['name']}" value="{instance['name']}" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;fillColor=#ED7100;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.compute;" vertex="1" parent="1">
                    <mxGeometry x="{x_pos}" y="{y_pos}" width="78" height="78" as="geometry"/>
                </mxCell>'''

class ReadmeUpdater:
    """Updates README.md files with infrastructure descriptions."""
    
    def __init__(self):
        pass
    
    def update_readme(self, analysis: Dict[str, Any], resources: Dict[str, Any]) -> bool:
        """Update or create README.md file with infrastructure description."""
        try:
            readme_content = self._generate_readme_content(analysis, resources)
            
            # Create backup if README exists
            if analysis['has_readme']:
                backup_path = f"{analysis['readme_path']}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(analysis['readme_path'], backup_path)
                print(f"Created backup: {backup_path}")
            
            # Write new README
            readme_path = analysis['readme_path'] or os.path.join(analysis['path'], 'README.md')
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"Updated README: {readme_path}")
            return True
        except Exception as e:
            print(f"Error updating README: {e}")
            return False
    
    def _generate_readme_content(self, analysis: Dict[str, Any], resources: Dict[str, Any]) -> str:
        """Generate README content based on infrastructure analysis."""
        title = self._generate_title(analysis['name'])
        description = self._generate_description(resources)
        resource_details = self._generate_resource_details(resources)
        
        content = f"""# {title}

このTerraform構成は、以下のAWSリソースを作成します：

![アーキテクチャ図](src/architecture.svg)

## 概要

{description}

## リソース構成

{resource_details}

## 使用方法

1. 必要な変数を設定してください
2. `terraform init` を実行してください
3. `terraform plan` で構成を確認してください
4. `terraform apply` でリソースを作成してください

## 注意事項

- このリソースを使用する際は、適切なIAM権限が必要です
- 作成されるリソースには料金が発生する場合があります
- 使用後は `terraform destroy` でリソースを削除してください
"""
        return content
    
    def _generate_title(self, directory_name: str) -> str:
        """Generate a title based on directory name."""
        # Extract meaningful parts from directory name
        parts = directory_name.split('.')
        if len(parts) > 1:
            return f"{parts[1].replace('-', ' ').replace(',', '、').title()} 構成"
        return f"{directory_name} 構成"
    
    def _generate_description(self, resources: Dict[str, Any]) -> str:
        """Generate description based on resources."""
        descriptions = []
        
        if resources.get('vpc'):
            descriptions.append("VPCネットワーク環境")
        if resources.get('ec2_instances'):
            descriptions.append(f"EC2インスタンス ({len(resources['ec2_instances'])}台)")
        if resources.get('rds_instances'):
            descriptions.append("RDSデータベース")
        if resources.get('lambda_functions'):
            descriptions.append("Lambda関数")
        if resources.get('s3_buckets'):
            descriptions.append("S3ストレージ")
        
        if descriptions:
            return "、".join(descriptions) + "を含むAWSインフラストラクチャです。"
        return "AWSリソースを管理するTerraform構成です。"
    
    def _generate_resource_details(self, resources: Dict[str, Any]) -> str:
        """Generate detailed resource descriptions."""
        details = []
        
        if resources.get('vpc'):
            details.append("### ネットワークリソース")
            for vpc in resources['vpc']:
                details.append(f"- **VPC**: {vpc['name']}")
        
        if resources.get('subnets'):
            for subnet in resources['subnets']:
                details.append(f"- **サブネット**: {subnet['name']}")
        
        if resources.get('security_groups'):
            for sg in resources['security_groups']:
                details.append(f"- **セキュリティグループ**: {sg['name']}")
        
        if resources.get('ec2_instances'):
            details.append("\n### コンピューティングリソース")
            for instance in resources['ec2_instances']:
                details.append(f"- **EC2インスタンス**: {instance['name']}")
        
        if resources.get('rds_instances'):
            details.append("\n### データベースリソース")
            for rds in resources['rds_instances']:
                details.append(f"- **RDSインスタンス**: {rds['name']}")
        
        if resources.get('lambda_functions'):
            details.append("\n### サーバーレスリソース")
            for func in resources['lambda_functions']:
                details.append(f"- **Lambda関数**: {func['name']}")
        
        return '\n'.join(details) if details else "リソースの詳細情報を取得できませんでした。"

class MainProcessor:
    """Main processor that orchestrates the entire README update process."""
    
    def __init__(self):
        self.analyzer = DirectoryAnalyzer()
        self.tf_parser = TerraformParser()
        self.diagram_generator = DiagramGenerator()
        self.readme_updater = ReadmeUpdater()
    
    def run(self):
        """Execute the main README update process."""
        print("=== README Update and Infrastructure Diagram Creation ===\n")
        
        # Step 1: Find and select directories
        print("1. Finding directories matching pattern [0-9][0-9][0-9].*...")
        all_directories = self.analyzer.find_matching_directories()
        print(f"   Found {len(all_directories)} matching directories")
        
        oldest_directories = self.analyzer.select_oldest_directories(all_directories, 3)
        print(f"   Selected 3 oldest directories for processing:")
        for i, dir_info in enumerate(oldest_directories, 1):
            print(f"   {i}. {dir_info['name']} - {dir_info['mtime_readable']}")
        print()
        
        # Step 2: Process each selected directory
        for i, dir_info in enumerate(oldest_directories, 1):
            print(f"Processing directory {i}/3: {dir_info['name']}")
            print("-" * 50)
            
            # Analyze directory structure
            analysis = self.analyzer.analyze_directory_structure(dir_info)
            print(f"   Directory analysis:")
            print(f"   - Has README: {analysis['has_readme']}")
            print(f"   - Terraform files: {len(analysis['terraform_files'])}")
            print(f"   - CloudFormation files: {len(analysis['cloudformation_files'])}")
            print(f"   - Has existing diagram: {analysis['has_existing_diagram']}")
            
            # Parse infrastructure files
            resources = {}
            if analysis['terraform_files']:
                print(f"   Parsing Terraform files...")
                resources = self.tf_parser.parse_terraform_files(analysis['terraform_files'])
                self._print_resource_summary(resources)
            
            # Generate diagram
            if analysis['src_directory']:
                diagram_path = os.path.join(analysis['src_directory'], 'architecture.drawio')
            else:
                # Create src directory if it doesn't exist
                src_dir = os.path.join(analysis['path'], 'src')
                os.makedirs(src_dir, exist_ok=True)
                diagram_path = os.path.join(src_dir, 'architecture.drawio')
            
            print(f"   Generating diagram: {diagram_path}")
            diagram_success = self.diagram_generator.generate_diagram(resources, diagram_path)
            
            # Update README
            print(f"   Updating README...")
            readme_success = self.readme_updater.update_readme(analysis, resources)
            
            if diagram_success and readme_success:
                print(f"   ✓ Successfully processed {dir_info['name']}")
            else:
                print(f"   ✗ Failed to process {dir_info['name']}")
            
            print()
        
        print("=== Processing Complete ===")
        print(f"Processed {len(oldest_directories)} directories")
        print("Note: SVG files will be generated automatically from DrawIO files by the system")
    
    def _print_resource_summary(self, resources: Dict[str, Any]):
        """Print a summary of discovered resources."""
        total_resources = sum(len(resource_list) for resource_list in resources.values() if resource_list)
        if total_resources > 0:
            print(f"   Found {total_resources} AWS resources:")
            for resource_type, resource_list in resources.items():
                if resource_list:
                    print(f"     - {resource_type}: {len(resource_list)}")
        else:
            print(f"   No AWS resources found")

def main():
    """Main entry point."""
    processor = MainProcessor()
    processor.run()

if __name__ == "__main__":
    main()