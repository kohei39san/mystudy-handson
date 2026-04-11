import boto3
import os
from datetime import datetime, timezone

QUOTAS = [
    {
        'service_code': 'vpc',
        'quota_code': 'L-F678F1CE',
        'quota_name': 'VPCs per Region',
        'resource_type': 'vpcs',
    },
    {
        'service_code': 'ec2',
        'quota_code': 'L-0263D0A3',
        'quota_name': 'EC2-VPC Elastic IPs',
        'resource_type': 'eips',
    },
    {
        'service_code': 'rds',
        'quota_code': 'L-7B6409FD',
        'quota_name': 'DB instances',
        'resource_type': 'rds-instances',
    },
]


def get_resource_count(resource_type, ec2_client, rds_client):
    if resource_type == 'vpcs':
        total = 0
        paginator = ec2_client.get_paginator('describe_vpcs')
        for page in paginator.paginate():
            total += len(page['Vpcs'])
        return total
    if resource_type == 'eips':
        return len(ec2_client.describe_addresses()['Addresses'])
    if resource_type == 'rds-instances':
        instances = []
        paginator = rds_client.get_paginator('describe_db_instances')
        for page in paginator.paginate():
            instances.extend(page['DBInstances'])
        return len(instances)
    return 0


def handler(event, context):
    namespace = os.environ['METRIC_NAMESPACE']
    ec2 = boto3.client('ec2')
    rds = boto3.client('rds')
    sq = boto3.client('service-quotas')
    cw = boto3.client('cloudwatch')
    results = []
    timestamp = datetime.now(timezone.utc)

    for q in QUOTAS:
        try:
            resp = sq.get_service_quota(
                ServiceCode=q['service_code'],
                QuotaCode=q['quota_code'],
            )
            limit = resp['Quota']['Value']
            usage = get_resource_count(q['resource_type'], ec2, rds)
            pct = round((usage / limit) * 100, 2) if limit > 0 else 0

            cw.put_metric_data(
                Namespace=namespace,
                MetricData=[
                    {
                        'MetricName': 'UsagePercentage',
                        'Dimensions': [
                            {'Name': 'ServiceCode', 'Value': q['service_code']},
                            {'Name': 'QuotaCode', 'Value': q['quota_code']},
                            {'Name': 'QuotaName', 'Value': q['quota_name']},
                        ],
                        'Value': pct,
                        'Unit': 'Percent',
                        'Timestamp': timestamp,
                    }
                ],
            )
            results.append(
                {'quota': q['quota_name'], 'usage': usage, 'limit': limit, 'percentage': pct}
            )
            print(f"{q['quota_name']}: {usage}/{int(limit)} ({pct}%)")

        except Exception as e:
            print(f"Error processing {q['quota_name']}: {e}")

    return {'statusCode': 200, 'results': results}
