plugin "aws" {
  enabled = true
  version = "0.30.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
  deep_check = true
}

# Enable terraform_comment_syntax rule
rule "terraform_comment_syntax" {
  enabled = true
}

# Enable terraform_deprecated_index rule
rule "terraform_deprecated_index" {
  enabled = true
}

# Enable terraform_deprecated_interpolation rule
rule "terraform_deprecated_interpolation" {
  enabled = true
}

# Enable terraform_documented_outputs rule
rule "terraform_documented_outputs" {
  enabled = true
}

# Enable terraform_documented_variables rule
rule "terraform_documented_variables" {
  enabled = true
}

# Enable terraform_module_pinned_source rule
rule "terraform_module_pinned_source" {
  enabled = true
}

# Enable terraform_naming_convention rule
rule "terraform_naming_convention" {
  enabled = true
}

# Enable terraform_required_providers rule
rule "terraform_required_providers" {
  enabled = true
}

# Enable terraform_required_version rule
rule "terraform_required_version" {
  enabled = true
}

# Enable terraform_standard_module_structure rule
rule "terraform_standard_module_structure" {
  enabled = true
}

# Enable terraform_typed_variables rule
rule "terraform_typed_variables" {
  enabled = true
}

# Enable terraform_unused_declarations rule
rule "terraform_unused_declarations" {
  enabled = true
}

# Enable terraform_unused_required_providers rule
rule "terraform_unused_required_providers" {
  enabled = true
}

# Enable terraform_workspace_remote rule
rule "terraform_workspace_remote" {
  enabled = true
}