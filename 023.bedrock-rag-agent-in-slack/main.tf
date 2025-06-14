module "main_stack" {
  source = "./modules/main_stack"

  project_name             = var.project_name
  slack_workspace_id       = var.slack_workspace_id
  slack_channel_id         = var.slack_channel_id
  slack_channel_name       = var.slack_channel_name
  opensearch_instance_type = var.opensearch_instance_type
}

module "bedrock_stack" {
  source = "./modules/bedrock_stack"

  main_stack_name             = var.project_name
  bedrock_model_id            = var.bedrock_model_id
  bedrock_opensearch_role_arn = module.main_stack.bedrock_opensearch_role_arn
  embedding_model_id          = var.embedding_model_id
  opensearch_endpoint         = module.main_stack.opensearch_endpoint
  knowledge_base_bucket_arn   = module.main_stack.knowledge_base_bucket_arn
  opensearch_domain_arn       = module.main_stack.opensearch_domain_arn

  depends_on = [
    module.main_stack,
    module.opensearch_index
  ]
}

module "lambda_stack" {
  source = "./modules/lambda_stack"

  main_stack_name           = var.project_name
  github_repository_url     = var.github_repository_url
  github_pat                = var.github_pat
  github_username           = var.github_username
  schedule_expression       = var.schedule_expression
  knowledgebase_bucket_arn  = module.main_stack.knowledge_base_bucket_arn
  knowledgebase_bucket_name = module.main_stack.knowledge_base_bucket_name
  knowledgebase_id          = module.bedrock_stack.knowledge_base_id
  datasource_id             = module.bedrock_stack.data_source_id

  depends_on = [
    module.bedrock_stack
  ]
}

module "opensearch_index" {
  source = "./modules/opensearch_index"

  depends_on = [
    module.main_stack
  ]
}