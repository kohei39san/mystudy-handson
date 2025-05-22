FROM public.ecr.aws/lambda/python:3.9

# システムの依存関係をインストール
RUN yum update -y && \
    yum install -y \
    gcc \
    gcc-c++ \
    make \
    git \
    wget \
    tar \
    gzip \
    && yum clean all

# 作業ディレクトリを設定
WORKDIR /var/task

# Python の依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# AWS Documentation MCP Server をインストール
RUN pip install --no-cache-dir aws-documentation-mcp-server

# Bedrock Knowledge Base MCP Server をインストール
RUN pip install --no-cache-dir bedrock-kb-mcp-server

# Lambda 関数コードをコピー
COPY lambda_function.py .

# Lambda ハンドラーを設定
CMD ["lambda_function.lambda_handler"]