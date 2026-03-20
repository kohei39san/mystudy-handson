FROM bitnami/kubectl:latest

# Switch to root to install packages
USER root

# Install socat for HTTPS proxy functionality
RUN install_packages socat

# Ensure UID 1001 has a named user entry to avoid "I have no name!" prompt.
RUN mkdir -p /home/kubectl \
	&& chown 1001:0 /home/kubectl \
	&& echo 'kubectl:x:1001:0:kubectl user:/home/kubectl:/bin/bash' >> /etc/passwd

# Start interactive exec sessions in kubectl user's home directory.
WORKDIR /home/kubectl

# Switch back to non-root user
USER 1001

# Default command (will be overridden by docker-compose)
CMD ["kubectl", "version", "--client"]
