resource "opensearch_index" "blog_index" {
  name = "blog-index"

  index_knn = true
  mappings  = file("${path.module}/src/index.json")

  depends_on = [
    aws_opensearch_domain.vector_store
  ]

  number_of_replicas = "1"
  number_of_shards   = "1"
}
