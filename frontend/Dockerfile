# ============================================================================
# Frontend Dockerfile
# ============================================================================
# Builds the React frontend application container.
# Uses Node.js 17 Alpine for a lightweight base image.
# ============================================================================

FROM node:17-alpine
WORKDIR /front

# Build arguments passed from docker-compose.yml
ARG FRONT_CMD        # Command to run (e.g., "npm start" or "npm run build")
ARG API_HOSTNAME     # Backend API hostname for frontend configuration
ARG FRONT_PORT       # Port number for the React app

# Environment variables for React app
ENV REACT_APP_API_HOSTNAME=$API_HOSTNAME  # Available in React code via process.env
ENV PORT=$FRONT_PORT                      # Port for React dev server

# Copy all frontend files and install dependencies
COPY . .
RUN npm install

# Note: The CMD directives below are overridden by docker-compose.yml command
# These are kept for reference but won't execute in compose setup
CMD npm install -g serve  # Install serve for production builds
CMD $FRONT_CMD            # Run the frontend command
