#!/usr/bin/env python3
"""
check_network_connectivity.py

Multi-cloud network connectivity checker for:
  - AWS EC2
  - AWS RDS
  - Azure Virtual Machine
  - GCP Compute Engine
  - GCP Cloud Run
  - GCP Cloud SQL

Usage:
  python check_network_connectivity.py --provider aws --resource-type ec2 --resource-id i-xxxxxxxxxxxxxxxxx
  python check_network_connectivity.py --provider aws --resource-type rds --resource-id mydbinstance
  python check_network_connectivity.py --provider azure --resource-type vm \
      --resource-id /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/<vm>
  python check_network_connectivity.py --provider gcp --resource-type compute \
      --resource-id projects/<proj>/zones/<zone>/instances/<name>
  python check_network_connectivity.py --provider gcp --resource-type cloudrun \
      --resource-id projects/<proj>/locations/<region>/services/<name>
  python check_network_connectivity.py --provider gcp --resource-type cloudsql \
      --resource-id projects/<proj>/instances/<name>
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Common types
# ─────────────────────────────────────────────────────────────────────────────

REACHABLE = "reachable"
NOT_REACHABLE = "not_reachable"
UNKNOWN = "unknown"


def _build_result(
    provider: str,
    resource_type: str,
    resource_id: str,
    internet_reachability: str,
    private_reachability: str,
    reasons: List[str],
    observed: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "provider": provider,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "internet_reachability": internet_reachability,
        "private_reachability": private_reachability,
        "reasons": reasons,
        "observed": observed,
    }


# ─────────────────────────────────────────────────────────────────────────────
# AWS helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_boto3_client(service: str, region: Optional[str] = None):
    """Return a boto3 client, importing boto3 lazily."""
    try:
        import boto3  # type: ignore
    except ImportError as exc:
        raise ImportError("boto3 is required for AWS checks. Install with: pip install boto3") from exc
    kwargs: Dict[str, Any] = {}
    if region:
        kwargs["region_name"] = region
    return boto3.client(service, **kwargs)


def _sg_rules_summary(sg_list: List[Dict]) -> Tuple[List[str], List[str]]:
    """
    Returns (ingress_cidrs, egress_cidrs) – lists of allowed CIDR strings
    extracted from the provided security group dictionaries.
    """
    ingress_cidrs: List[str] = []
    egress_cidrs: List[str] = []
    for sg in sg_list:
        for perm in sg.get("IpPermissions", []):
            for r in perm.get("IpRanges", []):
                cidr = r.get("CidrIp", "")
                if cidr:
                    ingress_cidrs.append(cidr)
            for r in perm.get("Ipv6Ranges", []):
                cidr = r.get("CidrIpv6", "")
                if cidr:
                    ingress_cidrs.append(cidr)
        for perm in sg.get("IpPermissionsEgress", []):
            for r in perm.get("IpRanges", []):
                cidr = r.get("CidrIp", "")
                if cidr:
                    egress_cidrs.append(cidr)
            for r in perm.get("Ipv6Ranges", []):
                cidr = r.get("CidrIpv6", "")
                if cidr:
                    egress_cidrs.append(cidr)
    return ingress_cidrs, egress_cidrs


def _is_public_subnet(ec2_client, subnet_id: str) -> bool:
    """
    A subnet is considered public when its associated route table has a route
    to an Internet Gateway (destination 0.0.0.0/0 or ::/0 via igw-*).
    """
    try:
        resp = ec2_client.describe_route_tables(
            Filters=[{"Name": "association.subnet-id", "Values": [subnet_id]}]
        )
        route_tables = resp.get("RouteTables", [])
        if not route_tables:
            # Fall back to the main route table of the VPC
            subnet_resp = ec2_client.describe_subnets(SubnetIds=[subnet_id])
            vpc_id = subnet_resp["Subnets"][0]["VpcId"]
            resp = ec2_client.describe_route_tables(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "association.main", "Values": ["true"]},
                ]
            )
            route_tables = resp.get("RouteTables", [])
        for rt in route_tables:
            for route in rt.get("Routes", []):
                gw = route.get("GatewayId", "")
                dest = route.get("DestinationCidrBlock", route.get("DestinationIpv6CidrBlock", ""))
                if gw.startswith("igw-") and dest in ("0.0.0.0/0", "::/0"):
                    return True
    except Exception:
        pass
    return False


def _has_nat_route(ec2_client, subnet_id: str) -> bool:
    """Check whether the subnet's route table contains a NAT Gateway route."""
    try:
        resp = ec2_client.describe_route_tables(
            Filters=[{"Name": "association.subnet-id", "Values": [subnet_id]}]
        )
        route_tables = resp.get("RouteTables", [])
        if not route_tables:
            subnet_resp = ec2_client.describe_subnets(SubnetIds=[subnet_id])
            vpc_id = subnet_resp["Subnets"][0]["VpcId"]
            resp = ec2_client.describe_route_tables(
                Filters=[
                    {"Name": "vpc-id", "Values": [vpc_id]},
                    {"Name": "association.main", "Values": ["true"]},
                ]
            )
            route_tables = resp.get("RouteTables", [])
        for rt in route_tables:
            for route in rt.get("Routes", []):
                nat = route.get("NatGatewayId", "")
                dest = route.get("DestinationCidrBlock", route.get("DestinationIpv6CidrBlock", ""))
                if nat and dest in ("0.0.0.0/0", "::/0"):
                    return True
    except Exception:
        pass
    return False


# ─────────────────────────────────────────────────────────────────────────────
# AWS EC2
# ─────────────────────────────────────────────────────────────────────────────

def check_aws_ec2(resource_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """Check network reachability for an AWS EC2 instance."""
    ec2 = _get_boto3_client("ec2", region)

    resp = ec2.describe_instances(InstanceIds=[resource_id])
    reservations = resp.get("Reservations", [])
    if not reservations:
        raise ValueError(f"EC2 instance not found: {resource_id}")

    instance = reservations[0]["Instances"][0]
    instance_state = instance.get("State", {}).get("Name", "unknown")
    subnet_id = instance.get("SubnetId", "")
    private_ip = instance.get("PrivateIpAddress", "")
    public_ip = instance.get("PublicIpAddress", "")

    # Security groups attached to the instance
    sg_ids = [sg["GroupId"] for sg in instance.get("SecurityGroups", [])]
    sg_resp = ec2.describe_security_groups(GroupIds=sg_ids) if sg_ids else {"SecurityGroups": []}
    sgs = sg_resp.get("SecurityGroups", [])
    ingress_cidrs, egress_cidrs = _sg_rules_summary(sgs)

    # Subnet / routing
    public_subnet = _is_public_subnet(ec2, subnet_id) if subnet_id else False
    nat_route = _has_nat_route(ec2, subnet_id) if subnet_id else False
    public_ip_assigned = bool(public_ip)

    reasons: List[str] = []
    observed: Dict[str, Any] = {
        "instance_state": instance_state,
        "subnet_id": subnet_id,
        "public_subnet": public_subnet,
        "nat_route": nat_route,
        "private_ip": private_ip,
        "public_ip": public_ip or None,
        "public_ip_assigned": public_ip_assigned,
        "security_groups": [
            {
                "group_id": sg["GroupId"],
                "group_name": sg.get("GroupName", ""),
                "ingress_cidrs": [
                    cidr
                    for perm in sg.get("IpPermissions", [])
                    for r in perm.get("IpRanges", [])
                    for cidr in [r.get("CidrIp", "")]
                    if cidr
                ]
                + [
                    cidr
                    for perm in sg.get("IpPermissions", [])
                    for r in perm.get("Ipv6Ranges", [])
                    for cidr in [r.get("CidrIpv6", "")]
                    if cidr
                ],
                "egress_cidrs": [
                    cidr
                    for perm in sg.get("IpPermissionsEgress", [])
                    for r in perm.get("IpRanges", [])
                    for cidr in [r.get("CidrIp", "")]
                    if cidr
                ]
                + [
                    cidr
                    for perm in sg.get("IpPermissionsEgress", [])
                    for r in perm.get("Ipv6Ranges", [])
                    for cidr in [r.get("CidrIpv6", "")]
                    if cidr
                ],
            }
            for sg in sgs
        ],
    }

    # ── Reasons ──────────────────────────────────────────────────────────────
    reasons.append(f"instance_state={instance_state}")
    reasons.append(f"public_subnet={str(public_subnet).lower()}")
    reasons.append(f"nat_route={str(nat_route).lower()}")
    reasons.append(f"public_ip_assigned={str(public_ip_assigned).lower()}")
    if ingress_cidrs:
        reasons.append(f"sg_ingress_allows={','.join(sorted(set(ingress_cidrs)))}")
    if egress_cidrs:
        reasons.append(f"sg_egress_allows={','.join(sorted(set(egress_cidrs)))}")

    # ── Reachability judgement ────────────────────────────────────────────────
    running = instance_state == "running"

    # Internet reachability: instance must be running, in a public subnet
    # (or have a public IP directly reachable), and have a public IP assigned.
    if running and public_ip_assigned and public_subnet:
        internet_reachability = REACHABLE
    elif not running:
        internet_reachability = NOT_REACHABLE
    else:
        internet_reachability = NOT_REACHABLE

    # Private reachability: instance running and reachable within VPC
    if running and private_ip:
        private_reachability = REACHABLE
    elif not running:
        private_reachability = NOT_REACHABLE
    else:
        private_reachability = UNKNOWN

    return _build_result(
        provider="aws",
        resource_type="ec2",
        resource_id=resource_id,
        internet_reachability=internet_reachability,
        private_reachability=private_reachability,
        reasons=reasons,
        observed=observed,
    )


# ─────────────────────────────────────────────────────────────────────────────
# AWS RDS
# ─────────────────────────────────────────────────────────────────────────────

def check_aws_rds(resource_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """Check network reachability for an AWS RDS DB instance."""
    rds = _get_boto3_client("rds", region)
    ec2 = _get_boto3_client("ec2", region)

    resp = rds.describe_db_instances(DBInstanceIdentifier=resource_id)
    instances = resp.get("DBInstances", [])
    if not instances:
        raise ValueError(f"RDS instance not found: {resource_id}")

    db = instances[0]
    db_state = db.get("DBInstanceStatus", "unknown")
    publicly_accessible = db.get("PubliclyAccessible", False)
    vpc_id = db.get("DBSubnetGroup", {}).get("VpcId", "")
    db_subnet_group_name = db.get("DBSubnetGroup", {}).get("DBSubnetGroupName", "")
    endpoint = db.get("Endpoint", {})
    endpoint_address = endpoint.get("Address", "")
    endpoint_port = endpoint.get("Port", 0)

    # Security groups
    sg_ids = [sg["VpcSecurityGroupId"] for sg in db.get("VpcSecurityGroups", []) if sg.get("Status") == "active"]
    sg_resp = ec2.describe_security_groups(GroupIds=sg_ids) if sg_ids else {"SecurityGroups": []}
    sgs = sg_resp.get("SecurityGroups", [])
    ingress_cidrs, egress_cidrs = _sg_rules_summary(sgs)

    # Subnet IDs in the DB subnet group
    subnet_ids = [s["SubnetIdentifier"] for s in db.get("DBSubnetGroup", {}).get("Subnets", [])]

    reasons: List[str] = []
    observed: Dict[str, Any] = {
        "db_state": db_state,
        "publicly_accessible": publicly_accessible,
        "vpc_id": vpc_id,
        "db_subnet_group": db_subnet_group_name,
        "subnet_ids": subnet_ids,
        "endpoint": endpoint_address,
        "port": endpoint_port,
        "security_groups": [
            {
                "group_id": sg["GroupId"],
                "group_name": sg.get("GroupName", ""),
                "ingress_cidrs": [
                    cidr
                    for perm in sg.get("IpPermissions", [])
                    for r in perm.get("IpRanges", [])
                    for cidr in [r.get("CidrIp", "")]
                    if cidr
                ]
                + [
                    cidr
                    for perm in sg.get("IpPermissions", [])
                    for r in perm.get("Ipv6Ranges", [])
                    for cidr in [r.get("CidrIpv6", "")]
                    if cidr
                ],
                "egress_cidrs": [
                    cidr
                    for perm in sg.get("IpPermissionsEgress", [])
                    for r in perm.get("IpRanges", [])
                    for cidr in [r.get("CidrIp", "")]
                    if cidr
                ]
                + [
                    cidr
                    for perm in sg.get("IpPermissionsEgress", [])
                    for r in perm.get("Ipv6Ranges", [])
                    for cidr in [r.get("CidrIpv6", "")]
                    if cidr
                ],
            }
            for sg in sgs
        ],
    }

    reasons.append(f"db_state={db_state}")
    reasons.append(f"publicly_accessible={str(publicly_accessible).lower()}")
    if ingress_cidrs:
        reasons.append(f"sg_ingress_allows={','.join(sorted(set(ingress_cidrs)))}")
    if egress_cidrs:
        reasons.append(f"sg_egress_allows={','.join(sorted(set(egress_cidrs)))}")

    available = db_state == "available"

    # Internet reachability: available and PubliclyAccessible
    if available and publicly_accessible:
        internet_reachability = REACHABLE
    elif not available:
        internet_reachability = NOT_REACHABLE
    else:
        internet_reachability = NOT_REACHABLE

    # Private reachability: available within VPC
    if available and vpc_id:
        private_reachability = REACHABLE
    elif not available:
        private_reachability = NOT_REACHABLE
    else:
        private_reachability = UNKNOWN

    return _build_result(
        provider="aws",
        resource_type="rds",
        resource_id=resource_id,
        internet_reachability=internet_reachability,
        private_reachability=private_reachability,
        reasons=reasons,
        observed=observed,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Azure VM
# ─────────────────────────────────────────────────────────────────────────────

def _parse_azure_resource_id(resource_id: str) -> Dict[str, str]:
    """
    Parse an Azure Resource Manager resource ID into its components.
    Expected format (case-insensitive):
      /subscriptions/<sub>/resourceGroups/<rg>/providers/<ns>/<type>/<name>
    """
    parts = resource_id.strip("/").split("/")
    result: Dict[str, str] = {}
    it = iter(parts)
    for key in it:
        try:
            value = next(it)
            result[key.lower()] = value
        except StopIteration:
            break
    return result


def check_azure_vm(resource_id: str) -> Dict[str, Any]:
    """Check network reachability for an Azure Virtual Machine."""
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore
        from azure.mgmt.compute import ComputeManagementClient  # type: ignore
        from azure.mgmt.network import NetworkManagementClient  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "azure-mgmt-compute, azure-mgmt-network, and azure-identity are required for Azure checks. "
            "Install with: pip install azure-mgmt-compute azure-mgmt-network azure-identity"
        ) from exc

    parsed = _parse_azure_resource_id(resource_id)
    subscription_id = parsed.get("subscriptions", "")
    resource_group = parsed.get("resourcegroups", "")
    vm_name_parsed = parsed.get("virtualmachines", "")

    # Allow plain "name" or full resource ID
    if not subscription_id:
        raise ValueError(
            "resource_id must be a full Azure resource ID: "
            "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Compute/virtualMachines/<name>"
        )

    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)

    # Get VM with instance view for power state
    vm = compute_client.virtual_machines.get(resource_group, vm_name_parsed, expand="instanceView")

    # Power state
    statuses = vm.instance_view.statuses if vm.instance_view else []
    power_state = "unknown"
    for status in statuses:
        if status.code and status.code.startswith("PowerState/"):
            power_state = status.code.split("/", 1)[1]
            break

    private_ips: List[str] = []
    public_ips: List[str] = []
    nsg_rules_info: List[Dict] = []
    subnet_ids: List[str] = []
    has_udr = False

    # Iterate NICs
    for nic_ref in vm.network_profile.network_interfaces or []:
        nic_id = nic_ref.id
        nic_parts = _parse_azure_resource_id(nic_id)
        nic_rg = nic_parts.get("resourcegroups", resource_group)
        nic_name = nic_parts.get("networkinterfaces", "")

        nic = network_client.network_interfaces.get(nic_rg, nic_name)

        for ip_config in nic.ip_configurations or []:
            # Private IP
            if ip_config.private_ip_address:
                private_ips.append(ip_config.private_ip_address)

            # Public IP
            if ip_config.public_ip_address and ip_config.public_ip_address.id:
                pip_parts = _parse_azure_resource_id(ip_config.public_ip_address.id)
                pip_rg = pip_parts.get("resourcegroups", resource_group)
                pip_name = pip_parts.get("publicipaddresses", "")
                try:
                    pip = network_client.public_ip_addresses.get(pip_rg, pip_name)
                    if pip.ip_address:
                        public_ips.append(pip.ip_address)
                except Exception:
                    pass

            # Subnet and UDR
            if ip_config.subnet and ip_config.subnet.id:
                subnet_ids.append(ip_config.subnet.id)
                sub_parts = _parse_azure_resource_id(ip_config.subnet.id)
                sub_rg = sub_parts.get("resourcegroups", resource_group)
                vnet_name = sub_parts.get("virtualnetworks", "")
                subnet_name = sub_parts.get("subnets", "")
                try:
                    subnet_obj = network_client.subnets.get(sub_rg, vnet_name, subnet_name)
                    if subnet_obj.route_table:
                        has_udr = True
                except Exception:
                    pass

        # NSG on NIC
        if nic.network_security_group and nic.network_security_group.id:
            nsg_parts = _parse_azure_resource_id(nic.network_security_group.id)
            nsg_rg = nsg_parts.get("resourcegroups", resource_group)
            nsg_name = nsg_parts.get("networksecuritygroups", "")
            try:
                nsg = network_client.network_security_groups.get(nsg_rg, nsg_name)
                nsg_rules = []
                for rule in nsg.security_rules or []:
                    if rule.access and rule.access.lower() == "allow":
                        nsg_rules.append(
                            {
                                "name": rule.name,
                                "direction": rule.direction,
                                "priority": rule.priority,
                                "protocol": rule.protocol,
                                "source_address_prefix": rule.source_address_prefix or "",
                                "destination_address_prefix": rule.destination_address_prefix or "",
                                "destination_port_range": rule.destination_port_range or "",
                            }
                        )
                nsg_rules_info.append({"nsg_name": nsg_name, "allow_rules": nsg_rules})
            except Exception:
                pass

    reasons: List[str] = []
    observed: Dict[str, Any] = {
        "power_state": power_state,
        "private_ips": private_ips,
        "public_ips": public_ips,
        "subnet_ids": subnet_ids,
        "has_udr": has_udr,
        "nsg_rules": nsg_rules_info,
    }

    reasons.append(f"power_state={power_state}")
    reasons.append(f"public_ip_assigned={str(bool(public_ips)).lower()}")
    reasons.append(f"has_udr={str(has_udr).lower()}")
    if nsg_rules_info:
        reasons.append("nsg_rules_present=true")

    running = power_state.lower() == "running"
    has_public_ip = bool(public_ips)

    internet_reachability = REACHABLE if running and has_public_ip else NOT_REACHABLE if not running else NOT_REACHABLE
    private_reachability = REACHABLE if running and private_ips else NOT_REACHABLE if not running else UNKNOWN

    return _build_result(
        provider="azure",
        resource_type="vm",
        resource_id=resource_id,
        internet_reachability=internet_reachability,
        private_reachability=private_reachability,
        reasons=reasons,
        observed=observed,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GCP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_gcp_credentials():
    """Return GCP credentials using Application Default Credentials."""
    try:
        import google.auth  # type: ignore
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return credentials, project
    except ImportError as exc:
        raise ImportError(
            "google-auth is required for GCP checks. "
            "Install with: pip install google-auth google-auth-httplib2 google-api-python-client"
        ) from exc


def _build_gcp_service(service_name: str, version: str):
    """Build a GCP API service client."""
    try:
        from googleapiclient import discovery  # type: ignore
        import google.auth  # type: ignore
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return discovery.build(service_name, version, credentials=credentials, cache_discovery=False)
    except ImportError as exc:
        raise ImportError(
            "google-api-python-client is required for GCP checks. "
            "Install with: pip install google-auth google-auth-httplib2 google-api-python-client"
        ) from exc


def _parse_gcp_resource_id(resource_id: str) -> Dict[str, str]:
    """
    Parse a GCP resource ID of the form:
      projects/<proj>/zones/<zone>/instances/<name>
      projects/<proj>/locations/<region>/services/<name>
      projects/<proj>/instances/<name>  (Cloud SQL)
    Returns a dict with keys from the path components.
    """
    parts = resource_id.strip("/").split("/")
    result: Dict[str, str] = {}
    it = iter(parts)
    for key in it:
        try:
            value = next(it)
            result[key] = value
        except StopIteration:
            break
    return result


def _gcp_get_firewall_rules_for_instance(
    service, project: str, network_name: str, instance_tags: List[str], service_account: Optional[str]
) -> List[Dict]:
    """
    Return firewall rules (ingress only) that apply to the given instance based on:
    - target tags matching instance network tags
    - target service accounts matching the instance service account
    - rules with no target tags / no target service accounts (apply to all)
    """
    result = service.firewalls().list(project=project).execute()
    rules = result.get("items", [])

    # Normalize network name (GCP returns full URL)
    def _network_matches(fw_network: str) -> bool:
        return fw_network.endswith("/" + network_name) or fw_network == network_name

    applicable: List[Dict] = []
    for rule in rules:
        if rule.get("direction", "INGRESS") != "INGRESS":
            continue
        if not _network_matches(rule.get("network", "")):
            continue

        target_tags = rule.get("targetTags", [])
        target_sas = rule.get("targetServiceAccounts", [])

        if not target_tags and not target_sas:
            # Applies to all instances in the network
            applicable.append(rule)
        elif instance_tags and any(t in instance_tags for t in target_tags):
            applicable.append(rule)
        elif service_account and service_account in target_sas:
            applicable.append(rule)

    return applicable


def _gcp_firewall_ingress_cidrs(fw_rules: List[Dict]) -> List[str]:
    """Extract all source CIDR ranges from the given firewall rules."""
    cidrs: List[str] = []
    for rule in fw_rules:
        cidrs.extend(rule.get("sourceRanges", []))
    return cidrs


# ─────────────────────────────────────────────────────────────────────────────
# GCP Compute Engine
# ─────────────────────────────────────────────────────────────────────────────

def check_gcp_compute(resource_id: str) -> Dict[str, Any]:
    """
    Check network reachability for a GCP Compute Engine instance.
    resource_id: projects/<proj>/zones/<zone>/instances/<name>
    """
    parsed = _parse_gcp_resource_id(resource_id)
    project = parsed.get("projects", "")
    zone = parsed.get("zones", "")
    instance_name = parsed.get("instances", "")

    service = _build_gcp_service("compute", "v1")

    instance = service.instances().get(project=project, zone=zone, instance=instance_name).execute()

    instance_state = instance.get("status", "UNKNOWN")
    network_tags = instance.get("tags", {}).get("items", [])

    # Network interfaces
    network_interfaces = instance.get("networkInterfaces", [])
    private_ips: List[str] = []
    external_ips: List[str] = []
    network_name = ""
    subnetwork = ""

    for nic in network_interfaces:
        if nic.get("networkIP"):
            private_ips.append(nic["networkIP"])
        for ac in nic.get("accessConfigs", []):
            if ac.get("natIP"):
                external_ips.append(ac["natIP"])
        if not network_name and nic.get("network"):
            # Extract network short name from full URL
            network_name = nic["network"].split("/")[-1]
        if not subnetwork and nic.get("subnetwork"):
            subnetwork = nic["subnetwork"].split("/")[-1]

    # Service account
    sas = instance.get("serviceAccounts", [])
    service_account = sas[0].get("email", "") if sas else None

    # Firewall rules applicable to this instance
    fw_rules = _gcp_get_firewall_rules_for_instance(
        service, project, network_name, network_tags, service_account
    )
    ingress_cidrs = _gcp_firewall_ingress_cidrs(fw_rules)

    fw_summary = [
        {
            "name": r.get("name", ""),
            "priority": r.get("priority", 1000),
            "source_ranges": r.get("sourceRanges", []),
            "allowed": r.get("allowed", []),
            "target_tags": r.get("targetTags", []),
        }
        for r in fw_rules
    ]

    reasons: List[str] = []
    observed: Dict[str, Any] = {
        "instance_state": instance_state,
        "network": network_name,
        "subnetwork": subnetwork,
        "private_ips": private_ips,
        "external_ips": external_ips,
        "network_tags": network_tags,
        "firewall_rules": fw_summary,
    }

    running = instance_state == "RUNNING"
    has_external_ip = bool(external_ips)

    reasons.append(f"instance_state={instance_state}")
    reasons.append(f"external_ip_assigned={str(has_external_ip).lower()}")
    reasons.append(f"network_tags={','.join(network_tags) if network_tags else 'none'}")
    if ingress_cidrs:
        reasons.append(f"fw_ingress_allows={','.join(sorted(set(ingress_cidrs)))}")

    internet_reachability = REACHABLE if running and has_external_ip else NOT_REACHABLE if not running else NOT_REACHABLE
    private_reachability = REACHABLE if running and private_ips else NOT_REACHABLE if not running else UNKNOWN

    return _build_result(
        provider="gcp",
        resource_type="compute",
        resource_id=resource_id,
        internet_reachability=internet_reachability,
        private_reachability=private_reachability,
        reasons=reasons,
        observed=observed,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GCP Cloud Run
# ─────────────────────────────────────────────────────────────────────────────

def check_gcp_cloudrun(resource_id: str) -> Dict[str, Any]:
    """
    Check network reachability for a GCP Cloud Run service.
    resource_id: projects/<proj>/locations/<region>/services/<name>
    """
    parsed = _parse_gcp_resource_id(resource_id)
    project = parsed.get("projects", "")
    location = parsed.get("locations", "")
    service_name = parsed.get("services", "")

    service = _build_gcp_service("run", "v1")

    # Cloud Run v1 uses namespaces (project) and locations
    cr_service = (
        service.namespaces()
        .services()
        .get(name=f"namespaces/{project}/services/{service_name}")
        .execute()
    )

    metadata = cr_service.get("metadata", {})
    annotations = metadata.get("annotations", {})
    spec = cr_service.get("spec", {})

    # Ingress setting
    ingress = annotations.get(
        "run.googleapis.com/ingress",
        annotations.get("serving.knative.dev/visibility", "all"),
    )

    # Authentication: check IAM policy for allUsers binding
    iam_service = _build_gcp_service("run", "v1")
    allow_unauthenticated = False
    try:
        policy_resp = (
            iam_service.projects()
            .locations()
            .services()
            .getIamPolicy(
                resource=f"projects/{project}/locations/{location}/services/{service_name}"
            )
            .execute()
        )
        bindings = policy_resp.get("bindings", [])
        for binding in bindings:
            if binding.get("role") == "roles/run.invoker" and "allUsers" in binding.get("members", []):
                allow_unauthenticated = True
                break
    except Exception:
        allow_unauthenticated = False

    # Service URL
    status = cr_service.get("status", {})
    url = status.get("url", "")

    reasons: List[str] = []
    observed: Dict[str, Any] = {
        "ingress": ingress,
        "allow_unauthenticated": allow_unauthenticated,
        "url": url,
        "location": location,
    }

    reasons.append(f"ingress={ingress}")
    reasons.append(f"allow_unauthenticated={str(allow_unauthenticated).lower()}")

    # Internet reachability: ingress must allow external traffic
    internet_accessible_ingress = ingress in ("all", "external")
    if internet_accessible_ingress:
        internet_reachability = REACHABLE
    else:
        internet_reachability = NOT_REACHABLE

    # Private reachability: internal ingress or VPC connector
    internal_ingress = ingress in ("internal", "internal-and-cloud-load-balancing")
    private_reachability = REACHABLE if internal_ingress or internet_accessible_ingress else NOT_REACHABLE

    return _build_result(
        provider="gcp",
        resource_type="cloudrun",
        resource_id=resource_id,
        internet_reachability=internet_reachability,
        private_reachability=private_reachability,
        reasons=reasons,
        observed=observed,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GCP Cloud SQL
# ─────────────────────────────────────────────────────────────────────────────

def check_gcp_cloudsql(resource_id: str) -> Dict[str, Any]:
    """
    Check network reachability for a GCP Cloud SQL instance.
    resource_id: projects/<proj>/instances/<name>
    """
    parsed = _parse_gcp_resource_id(resource_id)
    project = parsed.get("projects", "")
    instance_name = parsed.get("instances", "")

    service = _build_gcp_service("sqladmin", "v1beta4")

    sql_instance = service.instances().get(project=project, instance=instance_name).execute()

    db_state = sql_instance.get("state", "UNKNOWN")
    settings = sql_instance.get("settings", {})
    ip_config = settings.get("ipConfiguration", {})

    # IP addresses
    ip_addresses = sql_instance.get("ipAddresses", [])
    private_ip = ""
    public_ip = ""
    for addr in ip_addresses:
        if addr.get("type") == "PRIVATE":
            private_ip = addr.get("ipAddress", "")
        elif addr.get("type") == "PRIMARY":
            public_ip = addr.get("ipAddress", "")

    has_public_ip = ip_config.get("ipv4Enabled", False)
    private_network = ip_config.get("privateNetwork", "")
    has_private_ip = bool(private_network)

    # Authorized networks (only applicable when public IP is enabled)
    authorized_networks: List[str] = []
    if has_public_ip:
        for net in ip_config.get("authorizedNetworks", []):
            cidr = net.get("value", "")
            if cidr:
                authorized_networks.append(cidr)

    reasons: List[str] = []
    observed: Dict[str, Any] = {
        "db_state": db_state,
        "has_public_ip": has_public_ip,
        "has_private_ip": has_private_ip,
        "public_ip": public_ip or None,
        "private_ip": private_ip or None,
        "private_network": private_network or None,
        "authorized_networks": authorized_networks,
    }

    reasons.append(f"db_state={db_state}")
    reasons.append(f"has_public_ip={str(has_public_ip).lower()}")
    reasons.append(f"has_private_ip={str(has_private_ip).lower()}")
    if authorized_networks:
        reasons.append(f"authorized_networks={','.join(authorized_networks)}")
    if private_network:
        reasons.append(f"private_network={private_network.split('/')[-1]}")

    runnable = db_state == "RUNNABLE"

    # Internet reachability: RUNNABLE and public IP enabled
    internet_reachability = REACHABLE if runnable and has_public_ip else NOT_REACHABLE if not runnable else NOT_REACHABLE

    # Private reachability: RUNNABLE and private IP configured
    private_reachability = REACHABLE if runnable and has_private_ip else NOT_REACHABLE if not runnable else NOT_REACHABLE

    return _build_result(
        provider="gcp",
        resource_type="cloudsql",
        resource_id=resource_id,
        internet_reachability=internet_reachability,
        private_reachability=private_reachability,
        reasons=reasons,
        observed=observed,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

SUPPORTED = {
    ("aws", "ec2"): check_aws_ec2,
    ("aws", "rds"): check_aws_rds,
    ("azure", "vm"): check_azure_vm,
    ("gcp", "compute"): check_gcp_compute,
    ("gcp", "cloudrun"): check_gcp_cloudrun,
    ("gcp", "cloudsql"): check_gcp_cloudsql,
}


def check(provider: str, resource_type: str, resource_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Main entry point.  Dispatches to the appropriate provider/resource-type
    checker and returns a result dictionary.
    """
    key = (provider.lower(), resource_type.lower())
    if key not in SUPPORTED:
        raise ValueError(
            f"Unsupported provider/resource_type combination: {provider}/{resource_type}. "
            f"Supported: {', '.join(f'{p}/{r}' for p, r in SUPPORTED)}"
        )
    func = SUPPORTED[key]
    if region and key in {("aws", "ec2"), ("aws", "rds")}:
        return func(resource_id, region=region)
    return func(resource_id)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check network connectivity / reachability of cloud resources.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--provider",
        required=True,
        choices=["aws", "azure", "gcp"],
        help="Cloud provider (aws | azure | gcp)",
    )
    parser.add_argument(
        "--resource-type",
        required=True,
        choices=["ec2", "rds", "vm", "compute", "cloudrun", "cloudsql"],
        help="Resource type",
    )
    parser.add_argument(
        "--resource-id",
        required=True,
        help="Resource identifier (instance ID, full resource path, etc.)",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="AWS region (optional, falls back to AWS_DEFAULT_REGION env var or profile setting)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Write JSON output to this file instead of stdout",
    )

    args = parser.parse_args()

    try:
        result = check(
            provider=args.provider,
            resource_type=args.resource_type,
            resource_id=args.resource_id,
            region=args.region,
        )
        output = json.dumps(result, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Result written to {args.output}", file=sys.stderr)
        else:
            print(output)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
