#!/bin/bash

# OpenSearchのエンドポイントを環境変数から取得
OPENSEARCH_ENDPOINT=$1
USERNAME=$2
PASSWORD=$3

if [ -z "$OPENSEARCH_ENDPOINT" ] || [ -z "$USERNAME" ] || [ -z "$PASSWORD" ]; then
    echo "Usage: $0 <opensearch-endpoint> <username> <password>"
    exit 1
fi

# ベクトルインデックスの作成
echo "Creating vector index..."
curl -XPUT -k -u "${USERNAME}:${PASSWORD}" "https://${OPENSEARCH_ENDPOINT}/bedrock-kb" \
-H "Content-Type: application/json" \
-d '{
  "settings": {
    "index": {
      "knn": true,
      "knn.algo_param.ef_search": 512
    }
  },
  "mappings": {
    "properties": {
      "embedding": {
        "type": "knn_vector",
        "dimension": 1536,
        "method": {
          "name": "hnsw",
          "engine": "nmslib",
          "space_type": "l2",
          "parameters": {
            "ef_construction": 512,
            "m": 16
          }
        }
      },
      "text": {
        "type": "text"
      },
      "url": {
        "type": "keyword"
      },
      "title": {
        "type": "text"
      }
    }
  }
}'

# インデックス作成の確認
echo "Verifying index creation..."
curl -XGET -k -u "${USERNAME}:${PASSWORD}" "https://${OPENSEARCH_ENDPOINT/_cat/indices/bedrock-kb?v"

echo "OpenSearch initialization completed."