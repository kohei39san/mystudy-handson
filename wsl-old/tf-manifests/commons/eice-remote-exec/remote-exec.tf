locals {
  send_ssh_public_key_cmd = "aws ec2-instance-connect send-ssh-public-key --instance-id ${var.instance_id} --instance-os-user ${var.ssh_user} --ssh-public-key=file://${var.ssh_public_key}"
  env_cmds                = [for k, v in var.environment : "export ${k}=${v}"]
  remote_scripts          = [for s in var.scripts : "/tmp/${basename(s)}"]
  script_cmds             = [for s in local.remote_scripts : "chmod u+x ${s};${s}"]
  inline                  = length(var.scripts) == 0 ? concat(local.env_cmds, var.inline) : concat(local.env_cmds, local.script_cmds)
}

resource "terraform_data" "send_file" {
  for_each = { for k, v in local.remote_scripts : var.scripts[k] => local.remote_scripts[k] }
  triggers_replace = [
    var.public_ip,
    var.depends_on_cmd,
  ]

  provisioner "local-exec" {
    command = local.send_ssh_public_key_cmd
  }

  connection {
    type        = "ssh"
    user        = var.ssh_user
    host        = var.public_ip
    private_key = file(var.ssh_private_key)
  }

  provisioner "file" {
    source      = each.key
    destination = each.value
  }
}

resource "terraform_data" "remote_exec" {
  triggers_replace = concat([
    var.public_ip,
    var.depends_on_cmd,
  ], [for i in terraform_data.send_file : i.id])

  provisioner "local-exec" {
    command = local.send_ssh_public_key_cmd
  }

  connection {
    type        = "ssh"
    user        = var.ssh_user
    host        = var.public_ip
    private_key = file(var.ssh_private_key)
  }

  provisioner "remote-exec" {
    inline = local.inline
  }
}
