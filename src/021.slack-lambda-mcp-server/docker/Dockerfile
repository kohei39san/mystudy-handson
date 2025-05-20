FROM public.ecr.aws/lambda/python:3.11

# Install system dependencies
RUN yum update -y && \
    yum install -y \
    gcc \
    g++ \
    make \
    cmake \
    unzip \
    wget \
    git \
    tar \
    gzip \
    && yum clean all

# Set working directory
WORKDIR /var/task

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server files
COPY mcp_servers/ ./mcp_servers/

# Copy Lambda function code
COPY lambda_function.py .

# Set environment variables
ENV PYTHONPATH=/var/task
ENV OPENROUTER_API_KEY=""
ENV AWS_DOCS_MCP_SERVER_PORT=8080
ENV BEDROCK_KB_MCP_SERVER_PORT=8081

# Command to run the Lambda function
CMD ["lambda_function.handler"]