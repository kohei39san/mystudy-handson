FROM bitnami/kubectl:latest

# Switch to root to install packages
USER root

# Install socat for HTTPS proxy functionality
RUN install_packages socat

# Switch back to non-root user
USER 1001

# Default command (will be overridden by docker-compose)
CMD ["kubectl", "version", "--client"]
