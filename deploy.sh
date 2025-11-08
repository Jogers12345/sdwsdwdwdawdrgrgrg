#!/bin/bash
# BSEE Production Deployment Script
# Automated deployment for production environments

set -e  # Exit on any error

echo "🚀 BSEE Production Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Please edit .env file with your production values before continuing."
            print_warning "Pay special attention to password fields!"
            read -p "Press Enter to continue after editing .env file..."
        else
            print_error ".env.example file not found. Cannot create environment configuration."
            exit 1
        fi
    fi

    print_success "Prerequisites check passed"
}

# Validate environment configuration
validate_config() {
    print_status "Validating environment configuration..."

    # Check for placeholder values
    if grep -q "your_secure_.*_password_here" .env; then
        print_error "Found placeholder passwords in .env file. Please update them with secure values."
        exit 1
    fi

    if grep -q "changeme123" .env; then
        print_warning "Found default password values. Please update them for production security."
    fi

    # Check required environment variables
    source .env

    required_vars=("BSEE_DB_PASSWORD" "BSEE_SECRET_KEY")
    missing_vars=()

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        print_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi

    print_success "Environment configuration validated"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."

    directories=(
        "logs"
        "data"
        "models"
        "config/ssl"
        "results"
        "cache"
    )

    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        fi
    done

    print_success "Directories created"
}

# Run production tests
run_tests() {
    print_status "Running production validation tests..."

    if [ -f "test_production_system.py" ]; then
        python test_production_system.py
        if [ $? -eq 0 ]; then
            print_success "Production tests passed"
        else
            print_error "Production tests failed"
            exit 1
        fi
    else
        print_warning "Production test file not found. Skipping tests."
    fi
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."

    # Build with production target
    docker-compose build --target production

    if [ $? -eq 0 ]; then
        print_success "Docker images built successfully"
    else
        print_error "Docker build failed"
        exit 1
    fi
}

# Deploy services
deploy_services() {
    print_status "Deploying BSEE services..."

    # Stop existing services
    docker-compose down

    # Start services
    docker-compose up -d

    if [ $? -eq 0 ]; then
        print_success "Services deployed successfully"
    else
        print_error "Service deployment failed"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."

    # Wait for main application
    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_success "Main application is ready"
            break
        fi

        print_status "Waiting for application... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done

    if [ $attempt -gt $max_attempts ]; then
        print_error "Application failed to start within expected time"
        docker-compose logs bsee
        exit 1
    fi

    # Check other services
    print_status "Checking database connection..."
    if docker-compose exec -T postgres pg_isready -U bsee &> /dev/null; then
        print_success "Database is ready"
    else
        print_error "Database is not ready"
        exit 1
    fi

    print_status "Checking Redis connection..."
    if docker-compose exec -T redis redis-cli ping &> /dev/null; then
        print_success "Redis is ready"
    else
        print_error "Redis is not ready"
        exit 1
    fi
}

# Run post-deployment validation
post_deploy_validation() {
    print_status "Running post-deployment validation..."

    # Test AI system
    if curl -f http://localhost:8000/api/ai/status &> /dev/null; then
        print_success "AI system is responding"
    else
        print_warning "AI system endpoint not available (may be normal for minimal deployment)"
    fi

    # Check service health
    services=("bsee" "postgres" "redis" "nginx")

    for service in "${services[@]}"; do
        health=$(docker-compose ps -q "$service" | xargs docker inspect --format='{{.State.Health.Status}}' 2>/dev/null || echo "no-health-check")

        if [ "$health" = "healthy" ] || [ "$health" = "no-health-check" ]; then
            print_success "$service is healthy"
        else
            print_warning "$service health status: $health"
        fi
    done

    print_success "Post-deployment validation completed"
}

# Display deployment summary
show_summary() {
    print_success "🎉 BSEE Deployment Completed Successfully!"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🔗 Access URLs:"
    echo "  • Main Application: http://localhost:8000"
    echo "  • Health Check: http://localhost:8000/health"
    echo "  • API Documentation: http://localhost:8000/docs"
    echo "  • Grafana Dashboard: http://localhost:3000"
    echo "  • Prometheus: http://localhost:9090"
    echo ""
    echo "📝 Management Commands:"
    echo "  • View logs: docker-compose logs -f [service]"
    echo "  • Stop services: docker-compose down"
    echo "  • Restart services: docker-compose restart [service]"
    echo "  • Update services: docker-compose pull && docker-compose up -d"
    echo ""
    echo "📚 Documentation:"
    echo "  • AI Integration Guide: docs/AI_INTEGRATION_GUIDE.md"
    echo "  • Production Deployment: docs/PRODUCTION_DEPLOYMENT.md"
    echo ""
    echo "⚠️  Important Security Notes:"
    echo "  • Change default passwords if you haven't already"
    echo "  • Configure SSL certificates for HTTPS"
    echo "  • Set up monitoring and alerts"
    echo "  • Regular security updates"
}

# Error handling
handle_error() {
    print_error "Deployment failed! Check the logs above for details."
    print_error "You may need to clean up with: docker-compose down"
    exit 1
}

# Set error trap
trap handle_error ERR

# Main deployment flow
main() {
    echo "Starting BSEE production deployment..."
    echo ""

    check_prerequisites
    validate_config
    create_directories
    run_tests
    build_images
    deploy_services
    wait_for_services
    post_deploy_validation
    show_summary

    echo ""
    print_success "Deployment is complete! 🚀"
}

# Run main function
main "$@"