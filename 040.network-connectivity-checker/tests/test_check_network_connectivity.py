"""
Unit tests for check_network_connectivity.py

All external API calls (boto3, Azure SDK, GCP API) are mocked so that these
tests run without real cloud credentials.
"""

import json
import sys
import os
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# The conftest.py already adds the scripts directory to sys.path.
import check_network_connectivity as cnc


# ─────────────────────────────────────────────────────────────────────────────
# Helper factories
# ─────────────────────────────────────────────────────────────────────────────

def _make_ec2_instance(
    state="running",
    subnet_id="subnet-aaa",
    private_ip="10.0.1.10",
    public_ip="203.0.113.10",
    sg_ids=None,
):
    if sg_ids is None:
        sg_ids = [{"GroupId": "sg-111", "GroupName": "test-sg"}]
    return {
        "State": {"Name": state},
        "SubnetId": subnet_id,
        "PrivateIpAddress": private_ip,
        "PublicIpAddress": public_ip,
        "SecurityGroups": sg_ids,
    }


def _make_sg(group_id="sg-111", ingress_cidrs=None, egress_cidrs=None):
    ingress_cidrs = ingress_cidrs or ["0.0.0.0/0"]
    egress_cidrs = egress_cidrs or ["0.0.0.0/0"]
    return {
        "GroupId": group_id,
        "GroupName": "test-sg",
        "IpPermissions": [
            {
                "IpProtocol": "tcp",
                "FromPort": 443,
                "ToPort": 443,
                "IpRanges": [{"CidrIp": cidr} for cidr in ingress_cidrs],
                "Ipv6Ranges": [],
            }
        ],
        "IpPermissionsEgress": [
            {
                "IpProtocol": "-1",
                "FromPort": None,
                "ToPort": None,
                "IpRanges": [{"CidrIp": cidr} for cidr in egress_cidrs],
                "Ipv6Ranges": [],
            }
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Utility / helper tests
# ─────────────────────────────────────────────────────────────────────────────

class TestBuildResult:
    """Tests for _build_result helper."""

    def test_keys_present(self):
        result = cnc._build_result(
            provider="aws",
            resource_type="ec2",
            resource_id="i-123",
            internet_reachability=cnc.REACHABLE,
            private_reachability=cnc.REACHABLE,
            reasons=["instance_state=running"],
            observed={"instance_state": "running"},
        )
        assert result["provider"] == "aws"
        assert result["resource_type"] == "ec2"
        assert result["resource_id"] == "i-123"
        assert result["internet_reachability"] == cnc.REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE
        assert "instance_state=running" in result["reasons"]
        assert result["observed"]["instance_state"] == "running"


class TestSgRulesSummary:
    """Tests for _sg_rules_summary helper."""

    def test_empty(self):
        ing, eg = cnc._sg_rules_summary([])
        assert ing == []
        assert eg == []

    def test_ingress_and_egress(self):
        sg = _make_sg(ingress_cidrs=["10.0.0.0/16"], egress_cidrs=["0.0.0.0/0"])
        ing, eg = cnc._sg_rules_summary([sg])
        assert "10.0.0.0/16" in ing
        assert "0.0.0.0/0" in eg

    def test_ipv6_included(self):
        sg = {
            "GroupId": "sg-v6",
            "IpPermissions": [{"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443, "IpRanges": [], "Ipv6Ranges": [{"CidrIpv6": "::/0"}]}],
            "IpPermissionsEgress": [{"IpProtocol": "-1", "FromPort": None, "ToPort": None, "IpRanges": [], "Ipv6Ranges": [{"CidrIpv6": "::/0"}]}],
        }
        ing, eg = cnc._sg_rules_summary([sg])
        assert "::/0" in ing
        assert "::/0" in eg


class TestSgRulesWithPorts:
    """Tests for _sg_rules_with_ports helper."""

    def test_extracts_ports_and_protocol_for_ipv4(self):
        sg = _make_sg(ingress_cidrs=["10.0.0.0/16"], egress_cidrs=["0.0.0.0/0"])
        ingress_rules, egress_rules = cnc._sg_rules_with_ports([sg])

        assert ingress_rules[0]["cidr"] == "10.0.0.0/16"
        assert ingress_rules[0]["protocol"] == "tcp"
        assert ingress_rules[0]["from_port"] == 443
        assert ingress_rules[0]["to_port"] == 443

        assert egress_rules[0]["cidr"] == "0.0.0.0/0"
        assert egress_rules[0]["protocol"] == "-1"
        assert egress_rules[0]["from_port"] is None
        assert egress_rules[0]["to_port"] is None

    def test_extracts_ports_and_protocol_for_ipv6(self):
        sg = {
            "GroupId": "sg-v6",
            "GroupName": "sg-v6",
            "IpPermissions": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 8443,
                    "ToPort": 8443,
                    "IpRanges": [],
                    "Ipv6Ranges": [{"CidrIpv6": "::/0"}],
                }
            ],
            "IpPermissionsEgress": [],
        }

        ingress_rules, egress_rules = cnc._sg_rules_with_ports([sg])
        assert len(egress_rules) == 0
        assert ingress_rules[0]["cidr"] == "::/0"
        assert ingress_rules[0]["protocol"] == "tcp"
        assert ingress_rules[0]["from_port"] == 8443
        assert ingress_rules[0]["to_port"] == 8443


class TestParseAzureResourceId:
    def test_full_id(self):
        rid = "/subscriptions/sub123/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/myvm"
        parsed = cnc._parse_azure_resource_id(rid)
        assert parsed["subscriptions"] == "sub123"
        assert parsed["resourcegroups"] == "rg1"
        assert parsed["virtualmachines"] == "myvm"


class TestParseGcpResourceId:
    def test_compute(self):
        rid = "projects/my-proj/zones/us-central1-a/instances/my-vm"
        parsed = cnc._parse_gcp_resource_id(rid)
        assert parsed["projects"] == "my-proj"
        assert parsed["zones"] == "us-central1-a"
        assert parsed["instances"] == "my-vm"

    def test_cloudrun(self):
        rid = "projects/my-proj/locations/us-central1/services/my-svc"
        parsed = cnc._parse_gcp_resource_id(rid)
        assert parsed["projects"] == "my-proj"
        assert parsed["locations"] == "us-central1"
        assert parsed["services"] == "my-svc"

    def test_cloudsql(self):
        rid = "projects/my-proj/instances/my-db"
        parsed = cnc._parse_gcp_resource_id(rid)
        assert parsed["projects"] == "my-proj"
        assert parsed["instances"] == "my-db"


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher tests
# ─────────────────────────────────────────────────────────────────────────────

class TestDispatcher:
    def test_unsupported_combination_raises(self):
        with pytest.raises(ValueError, match="Unsupported provider"):
            cnc.check("aws", "cloudrun", "some-id")

    def test_supported_combinations_exist(self):
        assert ("aws", "ec2") in cnc.SUPPORTED
        assert ("aws", "rds") in cnc.SUPPORTED
        assert ("azure", "vm") in cnc.SUPPORTED
        assert ("gcp", "compute") in cnc.SUPPORTED
        assert ("gcp", "cloudrun") in cnc.SUPPORTED
        assert ("gcp", "cloudsql") in cnc.SUPPORTED


# ─────────────────────────────────────────────────────────────────────────────
# AWS EC2 tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAwsEc2:
    """Tests for check_aws_ec2."""

    def _mock_ec2_client(self, instance, sg, public_subnet=True, nat_route=False):
        """Build a mock boto3 EC2 client."""
        client = MagicMock()
        client.describe_instances.return_value = {
            "Reservations": [{"Instances": [instance]}]
        }
        client.describe_security_groups.return_value = {"SecurityGroups": [sg]}

        route = {"GatewayId": "igw-xxx", "DestinationCidrBlock": "0.0.0.0/0"}
        nat_r = {"NatGatewayId": "nat-xxx", "DestinationCidrBlock": "0.0.0.0/0"}
        rt_routes = []
        if public_subnet:
            rt_routes.append(route)
        if nat_route:
            rt_routes.append(nat_r)

        client.describe_route_tables.return_value = {
            "RouteTables": [{"Routes": rt_routes}]
        }
        return client

    @patch("check_network_connectivity._get_boto3_client")
    def test_running_public_instance_is_reachable(self, mock_client):
        instance = _make_ec2_instance()
        sg = _make_sg()
        client = self._mock_ec2_client(instance, sg, public_subnet=True)
        mock_client.return_value = client

        result = cnc.check_aws_ec2("i-123")

        assert result["internet_reachability"] == cnc.REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE
        assert "instance_state=running" in result["reasons"]
        assert "public_subnet=true" in result["reasons"]
        assert "public_ip_assigned=true" in result["reasons"]
        assert result["observed"]["public_ip"] == "203.0.113.10"
        assert result["observed"]["private_ip"] == "10.0.1.10"
        assert result["observed"]["public_ip_assigned"] is True

    @patch("check_network_connectivity._get_boto3_client")
    def test_stopped_instance_is_not_reachable(self, mock_client):
        instance = _make_ec2_instance(state="stopped")
        sg = _make_sg()
        client = self._mock_ec2_client(instance, sg, public_subnet=True)
        mock_client.return_value = client

        result = cnc.check_aws_ec2("i-456")

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.NOT_REACHABLE
        assert "instance_state=stopped" in result["reasons"]

    @patch("check_network_connectivity._get_boto3_client")
    def test_private_subnet_no_public_ip_not_internet_reachable(self, mock_client):
        instance = _make_ec2_instance(public_ip="")
        sg = _make_sg()
        client = self._mock_ec2_client(instance, sg, public_subnet=False, nat_route=True)
        mock_client.return_value = client

        result = cnc.check_aws_ec2("i-789")

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE
        assert "public_ip_assigned=false" in result["reasons"]
        assert result["observed"]["public_ip_assigned"] is False

    @patch("check_network_connectivity._get_boto3_client")
    def test_sg_ingress_cidrs_in_reasons(self, mock_client):
        instance = _make_ec2_instance()
        sg = _make_sg(ingress_cidrs=["10.0.0.0/8", "192.168.0.0/16"])
        client = self._mock_ec2_client(instance, sg, public_subnet=True)
        mock_client.return_value = client

        result = cnc.check_aws_ec2("i-sg")

        ingress_reason = next(
            (r for r in result["reasons"] if r.startswith("sg_ingress_allows=")), None
        )
        assert ingress_reason is not None
        assert "10.0.0.0/8" in ingress_reason
        assert "192.168.0.0/16" in ingress_reason

    @patch("check_network_connectivity._get_boto3_client")
    def test_not_found_raises(self, mock_client):
        client = MagicMock()
        client.describe_instances.return_value = {"Reservations": []}
        mock_client.return_value = client

        with pytest.raises(ValueError, match="EC2 instance not found"):
            cnc.check_aws_ec2("i-notfound")

    @patch("check_network_connectivity._get_boto3_client")
    def test_output_structure(self, mock_client):
        instance = _make_ec2_instance()
        sg = _make_sg()
        client = self._mock_ec2_client(instance, sg)
        mock_client.return_value = client

        result = cnc.check_aws_ec2("i-struct")

        for key in ("provider", "resource_type", "resource_id", "internet_reachability",
                    "private_reachability", "reasons", "observed"):
            assert key in result
        assert result["provider"] == "aws"
        assert result["resource_type"] == "ec2"
        observed_sg = result["observed"]["security_groups"][0]
        assert "ingress_rules" in observed_sg
        assert "egress_rules" in observed_sg
        assert "ingress_cidrs" not in observed_sg
        assert "egress_cidrs" not in observed_sg
        assert observed_sg["ingress_rules"][0]["protocol"] == "tcp"
        assert observed_sg["ingress_rules"][0]["from_port"] == 443
        assert observed_sg["ingress_rules"][0]["to_port"] == 443


# ─────────────────────────────────────────────────────────────────────────────
# AWS RDS tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAwsRds:
    """Tests for check_aws_rds."""

    def _make_rds_instance(
        self,
        status="available",
        publicly_accessible=True,
        vpc_id="vpc-111",
        sg_ids=None,
    ):
        if sg_ids is None:
            sg_ids = [{"VpcSecurityGroupId": "sg-rds", "Status": "active"}]
        return {
            "DBInstanceStatus": status,
            "PubliclyAccessible": publicly_accessible,
            "DBSubnetGroup": {
                "VpcId": vpc_id,
                "DBSubnetGroupName": "my-subnet-group",
                "Subnets": [
                    {"SubnetIdentifier": "subnet-a"},
                    {"SubnetIdentifier": "subnet-b"},
                ],
            },
            "VpcSecurityGroups": sg_ids,
            "Endpoint": {"Address": "mydb.cluster.us-east-1.rds.amazonaws.com", "Port": 5432},
        }

    @patch("check_network_connectivity._get_boto3_client")
    def test_available_public_rds_is_internet_reachable(self, mock_client):
        db = self._make_rds_instance(publicly_accessible=True)
        sg = _make_sg("sg-rds")

        rds_client = MagicMock()
        ec2_client = MagicMock()
        rds_client.describe_db_instances.return_value = {"DBInstances": [db]}
        ec2_client.describe_security_groups.return_value = {"SecurityGroups": [sg]}

        mock_client.side_effect = lambda svc, region=None: (
            rds_client if svc == "rds" else ec2_client
        )

        result = cnc.check_aws_rds("mydb")

        assert result["internet_reachability"] == cnc.REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE
        assert "db_state=available" in result["reasons"]
        assert "publicly_accessible=true" in result["reasons"]

    @patch("check_network_connectivity._get_boto3_client")
    def test_private_rds_not_internet_reachable(self, mock_client):
        db = self._make_rds_instance(publicly_accessible=False)
        sg = _make_sg("sg-rds")

        rds_client = MagicMock()
        ec2_client = MagicMock()
        rds_client.describe_db_instances.return_value = {"DBInstances": [db]}
        ec2_client.describe_security_groups.return_value = {"SecurityGroups": [sg]}

        mock_client.side_effect = lambda svc, region=None: (
            rds_client if svc == "rds" else ec2_client
        )

        result = cnc.check_aws_rds("mydb")

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE

    @patch("check_network_connectivity._get_boto3_client")
    def test_unavailable_rds_not_reachable(self, mock_client):
        db = self._make_rds_instance(status="stopped")
        sg = _make_sg("sg-rds")

        rds_client = MagicMock()
        ec2_client = MagicMock()
        rds_client.describe_db_instances.return_value = {"DBInstances": [db]}
        ec2_client.describe_security_groups.return_value = {"SecurityGroups": [sg]}

        mock_client.side_effect = lambda svc, region=None: (
            rds_client if svc == "rds" else ec2_client
        )

        result = cnc.check_aws_rds("mydb")

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.NOT_REACHABLE

    @patch("check_network_connectivity._get_boto3_client")
    def test_not_found_raises(self, mock_client):
        rds_client = MagicMock()
        rds_client.describe_db_instances.return_value = {"DBInstances": []}
        mock_client.return_value = rds_client

        with pytest.raises(ValueError, match="RDS instance not found"):
            cnc.check_aws_rds("notfound")

    @patch("check_network_connectivity._get_boto3_client")
    def test_output_structure(self, mock_client):
        db = self._make_rds_instance()
        sg = _make_sg("sg-rds")

        rds_client = MagicMock()
        ec2_client = MagicMock()
        rds_client.describe_db_instances.return_value = {"DBInstances": [db]}
        ec2_client.describe_security_groups.return_value = {"SecurityGroups": [sg]}

        mock_client.side_effect = lambda svc, region=None: (
            rds_client if svc == "rds" else ec2_client
        )

        result = cnc.check_aws_rds("mydb")

        assert result["provider"] == "aws"
        assert result["resource_type"] == "rds"
        assert result["observed"]["db_state"] == "available"
        assert result["observed"]["publicly_accessible"] is True
        observed_sg = result["observed"]["security_groups"][0]
        assert "ingress_rules" in observed_sg
        assert "egress_rules" in observed_sg
        assert "ingress_cidrs" not in observed_sg
        assert "egress_cidrs" not in observed_sg
        assert observed_sg["ingress_rules"][0]["protocol"] == "tcp"
        assert observed_sg["ingress_rules"][0]["from_port"] == 443
        assert observed_sg["ingress_rules"][0]["to_port"] == 443


# ─────────────────────────────────────────────────────────────────────────────
# Azure VM tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAzureVm:
    """Tests for check_azure_vm."""

    RESOURCE_ID = (
        "/subscriptions/sub-123/resourceGroups/rg1"
        "/providers/Microsoft.Compute/virtualMachines/myvm"
    )

    def _make_vm(self, power_state="running", nic_ids=None):
        vm = MagicMock()
        status = MagicMock()
        status.code = f"PowerState/{power_state}"
        vm.instance_view.statuses = [status]

        nic_ref = MagicMock()
        nic_ref.id = (
            "/subscriptions/sub-123/resourceGroups/rg1"
            "/providers/Microsoft.Network/networkInterfaces/nic1"
        )
        vm.network_profile.network_interfaces = [nic_ref]
        return vm

    def _make_nic(self, private_ip="10.0.0.4", public_ip_id=None, nsg_id=None, subnet_id=None):
        nic = MagicMock()
        ip_config = MagicMock()
        ip_config.private_ip_address = private_ip

        if public_ip_id:
            pip_ref = MagicMock()
            pip_ref.id = public_ip_id
            ip_config.public_ip_address = pip_ref
        else:
            ip_config.public_ip_address = None

        if subnet_id:
            subnet_ref = MagicMock()
            subnet_ref.id = subnet_id
            ip_config.subnet = subnet_ref
        else:
            ip_config.subnet = None

        nic.ip_configurations = [ip_config]

        if nsg_id:
            nsg_ref = MagicMock()
            nsg_ref.id = nsg_id
            nic.network_security_group = nsg_ref
        else:
            nic.network_security_group = None

        return nic

    def _make_nsg(self):
        nsg = MagicMock()
        rule = MagicMock()
        rule.name = "AllowHTTPS"
        rule.access = "Allow"
        rule.direction = "Inbound"
        rule.priority = 100
        rule.protocol = "Tcp"
        rule.source_address_prefix = "0.0.0.0/0"
        rule.destination_address_prefix = "*"
        rule.destination_port_range = "443"
        nsg.security_rules = [rule]
        return nsg

    def test_running_vm_with_public_ip_is_reachable(self):
        vm = self._make_vm(power_state="running")
        nic = self._make_nic(
            private_ip="10.0.0.4",
            public_ip_id=(
                "/subscriptions/sub-123/resourceGroups/rg1"
                "/providers/Microsoft.Network/publicIPAddresses/pip1"
            ),
        )
        pip = MagicMock()
        pip.ip_address = "1.2.3.4"
        nsg = self._make_nsg()

        mock_compute_cls = MagicMock()
        mock_network_cls = MagicMock()
        mock_cred = MagicMock()

        compute_client = MagicMock()
        compute_client.virtual_machines.get.return_value = vm
        mock_compute_cls.return_value = compute_client

        network_client = MagicMock()
        network_client.network_interfaces.get.return_value = nic
        network_client.public_ip_addresses.get.return_value = pip
        network_client.network_security_groups.get.return_value = nsg
        mock_network_cls.return_value = network_client

        with patch.dict("sys.modules", {
            "azure.identity": MagicMock(DefaultAzureCredential=mock_cred),
            "azure.mgmt.compute": MagicMock(ComputeManagementClient=mock_compute_cls),
            "azure.mgmt.network": MagicMock(NetworkManagementClient=mock_network_cls),
        }):
            result = cnc.check_azure_vm(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE
        assert "power_state=running" in result["reasons"]

    def test_stopped_vm_not_reachable(self):
        vm = self._make_vm(power_state="deallocated")
        nic = self._make_nic(private_ip="10.0.0.4")

        mock_compute_cls = MagicMock()
        mock_network_cls = MagicMock()
        mock_cred = MagicMock()

        compute_client = MagicMock()
        compute_client.virtual_machines.get.return_value = vm
        mock_compute_cls.return_value = compute_client

        network_client = MagicMock()
        network_client.network_interfaces.get.return_value = nic
        mock_network_cls.return_value = network_client

        with patch.dict("sys.modules", {
            "azure.identity": MagicMock(DefaultAzureCredential=mock_cred),
            "azure.mgmt.compute": MagicMock(ComputeManagementClient=mock_compute_cls),
            "azure.mgmt.network": MagicMock(NetworkManagementClient=mock_network_cls),
        }):
            result = cnc.check_azure_vm(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.NOT_REACHABLE

    def test_subnet_nsg_is_collected(self):
        vm = self._make_vm(power_state="running")
        nic = self._make_nic(
            private_ip="10.0.0.4",
            subnet_id=(
                "/subscriptions/sub-123/resourceGroups/rg1"
                "/providers/Microsoft.Network/virtualNetworks/vnet1/subnets/subnet1"
            ),
        )

        subnet_obj = MagicMock()
        subnet_obj.route_table = None
        subnet_nsg_ref = MagicMock()
        subnet_nsg_ref.id = (
            "/subscriptions/sub-123/resourceGroups/rg1"
            "/providers/Microsoft.Network/networkSecurityGroups/subnet-nsg"
        )
        subnet_obj.network_security_group = subnet_nsg_ref

        subnet_nsg = self._make_nsg()

        mock_compute_cls = MagicMock()
        mock_network_cls = MagicMock()
        mock_cred = MagicMock()

        compute_client = MagicMock()
        compute_client.virtual_machines.get.return_value = vm
        mock_compute_cls.return_value = compute_client

        network_client = MagicMock()
        network_client.network_interfaces.get.return_value = nic
        network_client.subnets.get.return_value = subnet_obj
        network_client.network_security_groups.get.return_value = subnet_nsg
        mock_network_cls.return_value = network_client

        with patch.dict("sys.modules", {
            "azure.identity": MagicMock(DefaultAzureCredential=mock_cred),
            "azure.mgmt.compute": MagicMock(ComputeManagementClient=mock_compute_cls),
            "azure.mgmt.network": MagicMock(NetworkManagementClient=mock_network_cls),
        }):
            result = cnc.check_azure_vm(self.RESOURCE_ID)

        assert result["observed"]["subnet_nsg_rules"]
        assert result["observed"]["subnet_nsg_rules"][0]["nsg_name"] == "subnet-nsg"
        assert "nsg_rules_present_subnet=true" in result["reasons"]
        assert "nsg_rules_present_nic=false" in result["reasons"]

    def test_invalid_resource_id_raises(self):
        with pytest.raises(ValueError, match="resource_id must be a full Azure resource ID"):
            cnc.check_azure_vm("just-a-vm-name")


# ─────────────────────────────────────────────────────────────────────────────
# GCP Compute Engine tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGcpCompute:
    """Tests for check_gcp_compute."""

    RESOURCE_ID = "projects/my-proj/zones/us-central1-a/instances/my-vm"

    def _make_instance(self, status="RUNNING", external_ip="34.0.0.1", tags=None):
        nic = {
            "networkIP": "10.128.0.2",
            "network": "https://www.googleapis.com/compute/v1/projects/my-proj/global/networks/default",
            "subnetwork": "https://www.googleapis.com/compute/v1/projects/my-proj/regions/us-central1/subnetworks/default",
            "accessConfigs": [],
        }
        if external_ip:
            nic["accessConfigs"] = [{"natIP": external_ip}]
        return {
            "status": status,
            "tags": {"items": tags or []},
            "networkInterfaces": [nic],
            "serviceAccounts": [{"email": "sa@my-proj.iam.gserviceaccount.com"}],
        }

    def _make_fw_rule(self, name="default-allow-https", source_ranges=None, target_tags=None):
        return {
            "name": name,
            "direction": "INGRESS",
            "network": "https://www.googleapis.com/compute/v1/projects/my-proj/global/networks/default",
            "priority": 1000,
            "sourceRanges": source_ranges or ["0.0.0.0/0"],
            "allowed": [{"IPProtocol": "tcp", "ports": ["443"]}],
            "targetTags": target_tags or [],
        }

    @patch("check_network_connectivity._build_gcp_service")
    def test_running_instance_with_external_ip_is_reachable(self, mock_build):
        instance_data = self._make_instance()
        fw_rule = self._make_fw_rule()

        service = MagicMock()
        service.instances.return_value.get.return_value.execute.return_value = instance_data
        service.firewalls.return_value.list.return_value.execute.return_value = {"items": [fw_rule]}
        mock_build.return_value = service

        result = cnc.check_gcp_compute(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE
        assert "instance_state=RUNNING" in result["reasons"]
        assert "external_ip_assigned=true" in result["reasons"]

    @patch("check_network_connectivity._build_gcp_service")
    def test_stopped_instance_not_reachable(self, mock_build):
        instance_data = self._make_instance(status="TERMINATED", external_ip=None)

        service = MagicMock()
        service.instances.return_value.get.return_value.execute.return_value = instance_data
        service.firewalls.return_value.list.return_value.execute.return_value = {"items": []}
        mock_build.return_value = service

        result = cnc.check_gcp_compute(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.NOT_REACHABLE

    @patch("check_network_connectivity._build_gcp_service")
    def test_network_tags_in_reasons(self, mock_build):
        instance_data = self._make_instance(tags=["http-server", "https-server"])
        fw_rule = self._make_fw_rule(target_tags=["https-server"])

        service = MagicMock()
        service.instances.return_value.get.return_value.execute.return_value = instance_data
        service.firewalls.return_value.list.return_value.execute.return_value = {"items": [fw_rule]}
        mock_build.return_value = service

        result = cnc.check_gcp_compute(self.RESOURCE_ID)

        tags_reason = next(
            (r for r in result["reasons"] if r.startswith("network_tags=")), None
        )
        assert tags_reason is not None
        assert "http-server" in tags_reason
        assert "https-server" in tags_reason
        assert result["observed"]["network_tags"] == ["http-server", "https-server"]

    @patch("check_network_connectivity._build_gcp_service")
    def test_firewall_tag_filtering(self, mock_build):
        """Firewall rules that don't match instance tags should not be applied."""
        instance_data = self._make_instance(tags=["web"])
        fw_rule_matching = self._make_fw_rule(name="allow-web", target_tags=["web"])
        fw_rule_non_matching = self._make_fw_rule(name="allow-db", target_tags=["db"])

        service = MagicMock()
        service.instances.return_value.get.return_value.execute.return_value = instance_data
        service.firewalls.return_value.list.return_value.execute.return_value = {
            "items": [fw_rule_matching, fw_rule_non_matching]
        }
        mock_build.return_value = service

        result = cnc.check_gcp_compute(self.RESOURCE_ID)

        fw_names = [fw["name"] for fw in result["observed"]["firewall_rules"]]
        assert "allow-web" in fw_names
        assert "allow-db" not in fw_names

    @patch("check_network_connectivity._build_gcp_service")
    def test_instance_without_external_ip_not_internet_reachable(self, mock_build):
        instance_data = self._make_instance(external_ip=None)

        service = MagicMock()
        service.instances.return_value.get.return_value.execute.return_value = instance_data
        service.firewalls.return_value.list.return_value.execute.return_value = {"items": []}
        mock_build.return_value = service

        result = cnc.check_gcp_compute(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE
        assert "external_ip_assigned=false" in result["reasons"]


# ─────────────────────────────────────────────────────────────────────────────
# GCP Cloud Run tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGcpCloudRun:
    """Tests for check_gcp_cloudrun."""

    RESOURCE_ID = "projects/my-proj/locations/us-central1/services/my-svc"

    def _make_cr_service(self, ingress="all"):
        return {
            "metadata": {
                "name": "my-svc",
                "annotations": {"run.googleapis.com/ingress": ingress},
            },
            "spec": {},
            "status": {"url": "https://my-svc-xxx-uc.a.run.app"},
        }

    def _make_iam_policy(self, allow_unauthenticated=True):
        bindings = []
        if allow_unauthenticated:
            bindings.append({"role": "roles/run.invoker", "members": ["allUsers"]})
        return {"bindings": bindings}

    def _make_lb_lookup(self, names=None, details=None, errors=None, permission_denied=False):
        if names is None:
            names = ["fw-default"]
        if details is None:
            details = [{"name": "fw-default", "scheme": "EXTERNAL_MANAGED"}]
        if errors is None:
            errors = []
        return {
            "matched_neg_names": ["neg-my-svc"],
            "matched_backend_names": ["be-my-svc"],
            "matched_lb_names": names,
            "matched_lb_details": details,
            "errors": errors,
            "permission_denied": permission_denied,
        }

    @patch("check_network_connectivity._discover_gcp_cloudrun_load_balancers")
    @patch("check_network_connectivity._build_gcp_service")
    def test_public_ingress_is_internet_reachable(self, mock_build, mock_discover):
        cr_data = self._make_cr_service(ingress="all")
        iam_policy = self._make_iam_policy(allow_unauthenticated=True)
        mock_discover.return_value = self._make_lb_lookup()

        run_service = MagicMock()
        run_service.projects.return_value.locations.return_value.services.return_value.get.return_value.execute.return_value = cr_data
        run_service.projects.return_value.locations.return_value.services.return_value.getIamPolicy.return_value.execute.return_value = iam_policy
        compute_service = MagicMock()
        mock_build.side_effect = [run_service, compute_service]

        result = cnc.check_gcp_cloudrun(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE
        assert "ingress=all" in result["reasons"]
        assert "invoker_principal_count=1" in result["reasons"]

    @patch("check_network_connectivity._discover_gcp_cloudrun_load_balancers")
    @patch("check_network_connectivity._build_gcp_service")
    def test_internal_ingress_not_internet_reachable(self, mock_build, mock_discover):
        cr_data = self._make_cr_service(ingress="internal")
        iam_policy = {"bindings": [{"role": "roles/run.invoker", "members": ["serviceAccount:svc@x"]}]}
        mock_discover.return_value = self._make_lb_lookup(
            names=["fw-external"],
            details=[{"name": "fw-external", "scheme": "EXTERNAL_MANAGED"}],
        )

        run_service = MagicMock()
        run_service.projects.return_value.locations.return_value.services.return_value.get.return_value.execute.return_value = cr_data
        run_service.projects.return_value.locations.return_value.services.return_value.getIamPolicy.return_value.execute.return_value = iam_policy
        compute_service = MagicMock()
        mock_build.side_effect = [run_service, compute_service]

        result = cnc.check_gcp_cloudrun(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.NOT_REACHABLE
        assert "ingress_internal_lb_scheme_mismatch" in result["reasons"]

    @patch("check_network_connectivity._discover_gcp_cloudrun_load_balancers")
    @patch("check_network_connectivity._build_gcp_service")
    def test_external_ingress_is_internet_reachable(self, mock_build, mock_discover):
        cr_data = self._make_cr_service(ingress="external")
        iam_policy = {"bindings": [{"role": "roles/run.invoker", "members": ["serviceAccount:svc@x"]}]}
        mock_discover.return_value = self._make_lb_lookup()

        run_service = MagicMock()
        run_service.projects.return_value.locations.return_value.services.return_value.get.return_value.execute.return_value = cr_data
        run_service.projects.return_value.locations.return_value.services.return_value.getIamPolicy.return_value.execute.return_value = iam_policy
        compute_service = MagicMock()
        mock_build.side_effect = [run_service, compute_service]

        result = cnc.check_gcp_cloudrun(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE

    @patch("check_network_connectivity._discover_gcp_cloudrun_load_balancers")
    @patch("check_network_connectivity._build_gcp_service")
    def test_invoker_missing_not_reachable(self, mock_build, mock_discover):
        cr_data = self._make_cr_service(ingress="all")
        iam_policy = {"bindings": []}
        mock_discover.return_value = self._make_lb_lookup()

        run_service = MagicMock()
        run_service.projects.return_value.locations.return_value.services.return_value.get.return_value.execute.return_value = cr_data
        run_service.projects.return_value.locations.return_value.services.return_value.getIamPolicy.return_value.execute.return_value = iam_policy
        compute_service = MagicMock()
        mock_build.side_effect = [run_service, compute_service]

        result = cnc.check_gcp_cloudrun(self.RESOURCE_ID)

        assert result["private_reachability"] == cnc.NOT_REACHABLE
        assert "invoker_missing" in result["reasons"]

    @patch("check_network_connectivity._discover_gcp_cloudrun_load_balancers")
    @patch("check_network_connectivity._build_gcp_service")
    def test_lb_permission_denied_results_unknown(self, mock_build, mock_discover):
        cr_data = self._make_cr_service(ingress="all")
        iam_policy = {"bindings": [{"role": "roles/run.invoker", "members": ["serviceAccount:svc@x"]}]}
        mock_discover.return_value = self._make_lb_lookup(
            names=[],
            details=[],
            errors=["permission_denied:backendServices"],
            permission_denied=True,
        )

        run_service = MagicMock()
        run_service.projects.return_value.locations.return_value.services.return_value.get.return_value.execute.return_value = cr_data
        run_service.projects.return_value.locations.return_value.services.return_value.getIamPolicy.return_value.execute.return_value = iam_policy
        compute_service = MagicMock()
        mock_build.side_effect = [run_service, compute_service]

        result = cnc.check_gcp_cloudrun(self.RESOURCE_ID)

        assert result["private_reachability"] == cnc.UNKNOWN
        assert "permission_denied" in result["reasons"]

    @patch("check_network_connectivity._discover_gcp_cloudrun_load_balancers")
    @patch("check_network_connectivity._build_gcp_service")
    def test_multiple_lbs_one_valid_reachable(self, mock_build, mock_discover):
        cr_data = self._make_cr_service(ingress="internal")
        iam_policy = {"bindings": [{"role": "roles/run.invoker", "members": ["serviceAccount:svc@x"]}]}
        mock_discover.return_value = self._make_lb_lookup(
            names=["fw-external", "fw-internal"],
            details=[
                {"name": "fw-external", "scheme": "EXTERNAL_MANAGED"},
                {"name": "fw-internal", "scheme": "INTERNAL_MANAGED"},
            ],
        )

        run_service = MagicMock()
        run_service.projects.return_value.locations.return_value.services.return_value.get.return_value.execute.return_value = cr_data
        run_service.projects.return_value.locations.return_value.services.return_value.getIamPolicy.return_value.execute.return_value = iam_policy
        compute_service = MagicMock()
        mock_build.side_effect = [run_service, compute_service]

        result = cnc.check_gcp_cloudrun(self.RESOURCE_ID)

        assert result["private_reachability"] == cnc.REACHABLE
        assert sorted(result["observed"]["matched_lb_names"]) == ["fw-external", "fw-internal"]


# ─────────────────────────────────────────────────────────────────────────────
# GCP Cloud SQL tests
# ─────────────────────────────────────────────────────────────────────────────

class TestGcpCloudSql:
    """Tests for check_gcp_cloudsql."""

    RESOURCE_ID = "projects/my-proj/instances/my-db"

    def _make_sql_instance(
        self,
        state="RUNNABLE",
        public_ip_enabled=True,
        private_network=None,
        authorized_networks=None,
        ip_addresses=None,
    ):
        if ip_addresses is None:
            ip_addresses = []
            if public_ip_enabled:
                ip_addresses.append({"type": "PRIMARY", "ipAddress": "34.0.0.10"})
            if private_network:
                ip_addresses.append({"type": "PRIVATE", "ipAddress": "10.0.0.5"})

        ip_config: dict = {"ipv4Enabled": public_ip_enabled}
        if private_network:
            ip_config["privateNetwork"] = private_network
        if authorized_networks is not None:
            ip_config["authorizedNetworks"] = [
                {"value": cidr} for cidr in authorized_networks
            ]

        return {
            "state": state,
            "ipAddresses": ip_addresses,
            "settings": {"ipConfiguration": ip_config},
        }

    @patch("check_network_connectivity._build_gcp_service")
    def test_public_ip_enabled_internet_reachable(self, mock_build):
        sql_data = self._make_sql_instance(
            public_ip_enabled=True,
            authorized_networks=["0.0.0.0/0"],
        )
        service = MagicMock()
        service.instances.return_value.get.return_value.execute.return_value = sql_data
        mock_build.return_value = service

        result = cnc.check_gcp_cloudsql(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.REACHABLE
        assert result["private_reachability"] == cnc.NOT_REACHABLE
        assert "db_state=RUNNABLE" in result["reasons"]
        assert "has_public_ip=true" in result["reasons"]
        assert "authorized_networks=0.0.0.0/0" in result["reasons"]

    @patch("check_network_connectivity._build_gcp_service")
    def test_private_only_not_internet_reachable(self, mock_build):
        sql_data = self._make_sql_instance(
            public_ip_enabled=False,
            private_network="projects/my-proj/global/networks/default",
        )
        service = MagicMock()
        service.instances.return_value.get.return_value.execute.return_value = sql_data
        mock_build.return_value = service

        result = cnc.check_gcp_cloudsql(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.REACHABLE
        assert "has_private_ip=true" in result["reasons"]

    @patch("check_network_connectivity._build_gcp_service")
    def test_stopped_db_not_reachable(self, mock_build):
        sql_data = self._make_sql_instance(state="SUSPENDED", public_ip_enabled=True)
        service = MagicMock()
        service.instances.return_value.get.return_value.execute.return_value = sql_data
        mock_build.return_value = service

        result = cnc.check_gcp_cloudsql(self.RESOURCE_ID)

        assert result["internet_reachability"] == cnc.NOT_REACHABLE
        assert result["private_reachability"] == cnc.NOT_REACHABLE

    @patch("check_network_connectivity._build_gcp_service")
    def test_output_structure(self, mock_build):
        sql_data = self._make_sql_instance(
            public_ip_enabled=True,
            private_network="projects/my-proj/global/networks/default",
        )
        service = MagicMock()
        service.instances.return_value.get.return_value.execute.return_value = sql_data
        mock_build.return_value = service

        result = cnc.check_gcp_cloudsql(self.RESOURCE_ID)

        assert result["provider"] == "gcp"
        assert result["resource_type"] == "cloudsql"
        assert result["resource_id"] == self.RESOURCE_ID
        assert "db_state" in result["observed"]
        assert "has_public_ip" in result["observed"]
        assert "has_private_ip" in result["observed"]
        assert "public_ip" in result["observed"]
        assert "private_ip" in result["observed"]
        assert "authorized_networks" in result["observed"]


# ─────────────────────────────────────────────────────────────────────────────
# JSON serialisability tests
# ─────────────────────────────────────────────────────────────────────────────

class TestJsonSerializable:
    """Verify result dicts can be serialised to JSON without errors."""

    @patch("check_network_connectivity._get_boto3_client")
    def test_ec2_result_is_json_serializable(self, mock_client):
        instance = _make_ec2_instance()
        sg = _make_sg()
        client = MagicMock()
        client.describe_instances.return_value = {"Reservations": [{"Instances": [instance]}]}
        client.describe_security_groups.return_value = {"SecurityGroups": [sg]}
        client.describe_route_tables.return_value = {
            "RouteTables": [{"Routes": [{"GatewayId": "igw-x", "DestinationCidrBlock": "0.0.0.0/0"}]}]
        }
        mock_client.return_value = client

        result = cnc.check_aws_ec2("i-json")
        serialised = json.dumps(result)
        parsed = json.loads(serialised)
        assert parsed["provider"] == "aws"
