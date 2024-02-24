locals {
  send_ssh_public_key_cmd = "aws ec2-instance-connect send-ssh-public-key --instance-id ${var.instance_id} --instance-os-user ${var.ssh_user} --ssh-public-key=file://${var.ssh_public_key}"
  env_cmds                = [for k, v in var.environment : "export ${k}=${v}"]
  remote_scripts          = [for s in var.scripts : "/tmp/${basename(s)}"]
  script_cmds             = [for s in local.remote_scripts : "chmod u+x ${s};${s}"]
  inline                  = length(var.scripts) == 0 ? concat(local.env_cmds, var.inline) : concat(local.env_cmds, local.script_cmds)
}

resource "null_resource" "send_file" {
  for_each = { for k, v in local.remote_scripts : var.scripts[k] => local.remote_scripts[k] }
  triggers = {
    public_ip = "${var.public_ip}"
  }

  provisioner "local-exec" {
    command = local.send_ssh_public_key_cmd
  }

  connection {
    type        = "ssh"
    user        = var.ssh_user
    host        = self.triggers.public_ip
    private_key = file(var.ssh_private_key)
  }

  provisioner "file" {
    source      = each.key
    destination = each.value
  }
}

resource "null_resource" "remote_exec" {
  triggers = {
    public_ip     = "${var.public_ip}"
    send_file_ids = join(",", [for i in null_resource.send_file : i.id])
  }

  provisioner "local-exec" {
    command = local.send_ssh_public_key_cmd
  }

  connection {
    type        = "ssh"
    user        = var.ssh_user
    host        = self.triggers.public_ip
    private_key = file(var.ssh_private_key)
  }

  provisioner "remote-exec" {
    inline = local.inline
  }
}
