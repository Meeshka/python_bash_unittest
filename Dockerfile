# Use the latest Ubuntu base image
FROM ubuntu:latest

# Update package lists and install any dependencies (optional)
RUN apt-get update && apt-get install -y \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Set the default command to run when the container starts
CMD ["bash"]
