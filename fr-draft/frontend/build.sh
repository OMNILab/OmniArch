#!/bin/bash

# Build script for Smart Meeting Frontend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="smart-meeting-frontend"
TAG=${1:-latest}
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo -e "${GREEN}🚀 Building Smart Meeting Frontend Docker Image${NC}"
echo -e "${YELLOW}Image: ${FULL_IMAGE_NAME}${NC}"

# Build the Docker image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build -t ${FULL_IMAGE_NAME} .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    echo -e "${YELLOW}Image: ${FULL_IMAGE_NAME}${NC}"
    
    # Show image info
    echo -e "${YELLOW}📊 Image details:${NC}"
    docker images ${FULL_IMAGE_NAME}
    
    echo -e "${GREEN}🎉 Build completed successfully!${NC}"
    echo -e "${YELLOW}To run the container:${NC}"
    echo -e "  docker run -p 80:80 ${FULL_IMAGE_NAME}"
    echo -e "${YELLOW}Or use docker-compose:${NC}"
    echo -e "  docker-compose up -d"
else
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi 