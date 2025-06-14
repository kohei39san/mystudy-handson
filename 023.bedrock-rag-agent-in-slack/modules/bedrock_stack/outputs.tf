output "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID"
  value       = aws_cloudformation_stack.bedrock_stack.outputs["KnowledgeBaseId"]
}

output "data_source_id" {
  description = "Bedrock Data Source ID"
  value       = aws_cloudformation_stack.bedrock_stack.outputs["DataSourceId"]
}

output "agent_id" {
  description = "Bedrock Agent ID"
  value       = aws_cloudformation_stack.bedrock_stack.outputs["AgentId"]
}

output "agent_alias_id" {
  description = "Bedrock Agent Alias ID"
  value       = aws_cloudformation_stack.bedrock_stack.outputs["AgentAliasId"]
}

output "agent_arn" {
  description = "Bedrock Agent ARN"
  value       = aws_cloudformation_stack.bedrock_stack.outputs["AgentArn"]
}

output "alias_id" {
  description = "Bedrock Alias ID"
  value       = aws_cloudformation_stack.bedrock_stack.outputs["AliasId"]
}