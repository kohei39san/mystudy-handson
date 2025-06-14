terraform {
  required_version = ">= 1.0.0"

  required_providers {
    opensearch = {
      source  = "opensearch-project/opensearch"
      version = "~> 2.0"
    }
  }
}

resource "opensearch_index" "bedrock_index" {
  name = "bedrock-index"

  index_knn = true
  mappings  = file("${path.module}/../../../src/023.bedrock-rag-agent-in-slack/index.json")

  number_of_replicas = "1"
  number_of_shards   = "1"
  force_destroy      = true
}