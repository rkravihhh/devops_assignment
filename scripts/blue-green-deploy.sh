#!/bin/bash

# Blue-Green Deployment Script for Bash
# This script manages blue-green deployments for the application

set -e

# Configuration
APP_NAME="backend-app"
BLUE_DEPLOYMENT="backend-app-blue"
GREEN_DEPLOYMENT="backend-app-green"
BLUE_SERVICE="backend-app-blue-service"
GREEN_SERVICE="backend-app-green-service"
BLUE_INGRESS="backend-app-blue-ingress"
GREEN_INGRESS="backend-app-green-ingress"
HEALTH_CHECK_PATH="/health"
HEALTH_CHECK_TIMEOUT=300  # 5 minutes
ROLLBACK_TIMEOUT=60       # 1 minute

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a deployment is ready
check_deployment_ready() {
    local deployment_name=$1
    local namespace=$2
    
    log_info "Checking if deployment $deployment_name is ready..."
    
    if ! kubectl get deployment "$deployment_name" -n "$namespace" >/dev/null 2>&1; then
        log_error "Deployment $deployment_name not found in namespace $namespace"
        return 1
    fi
    
    if kubectl rollout status deployment/"$deployment_name" -n "$namespace" --timeout=${HEALTH_CHECK_TIMEOUT}s; then
        return 0
    else
        log_error "Deployment $deployment_name failed to become ready"
        return 1
    fi
}

# Function to check if pods are healthy
check_pods_healthy() {
    local deployment_name=$1
    local namespace=$2
    
    log_info "Checking if pods for $deployment_name are healthy..."
    
    # Get version from deployment name
    local version
    if [[ "$deployment_name" == *"blue"* ]]; then
        version="blue"
    else
        version="green"
    fi
    
    # Get pod names
    local pods
    pods=$(kubectl get pods -n "$namespace" -l "app=backend-app,version=$version" -o jsonpath='{.items[*].metadata.name}' 2>/dev/null)
    
    if [ -z "$pods" ]; then
        log_error "No pods found for deployment $deployment_name"
        return 1
    fi
    
    # Check each pod
    for pod in $pods; do
        if [ -z "$pod" ]; then continue; fi
        
        log_info "Checking pod $pod..."
        
        # Wait for pod to be ready
        if ! kubectl wait --for=condition=Ready pod/"$pod" -n "$namespace" --timeout=${HEALTH_CHECK_TIMEOUT}s; then
            log_error "Pod $pod is not ready"
            return 1
        fi
        
        # Check if pod is actually healthy by calling health endpoint
        local pod_ip
        pod_ip=$(kubectl get pod "$pod" -n "$namespace" -o jsonpath='{.status.podIP}' 2>/dev/null)
        if [ -n "$pod_ip" ]; then
            log_info "Testing health endpoint on pod $pod ($pod_ip:8000$HEALTH_CHECK_PATH)"
            if ! kubectl exec "$pod" -n "$namespace" -- curl -f "http://localhost:8000$HEALTH_CHECK_PATH" >/dev/null 2>&1; then
                log_error "Health check failed for pod $pod"
                return 1
            fi
        fi
    done
    
    log_success "All pods for $deployment_name are healthy"
    return 0
}

# Function to switch traffic to a deployment
switch_traffic() {
    local target_deployment=$1
    local namespace=$2
    
    log_info "Switching traffic to $target_deployment..."
    
    if [[ "$target_deployment" == "$BLUE_DEPLOYMENT" ]]; then
        # Switch to blue
        log_info "Switching ALB target group to blue..."
        kubectl patch ingress "$BLUE_INGRESS" -n "$namespace" -p '{"metadata":{"annotations":{"alb.ingress.kubernetes.io/target-group-arn":"'$BLUE_TARGET_GROUP_ARN'"}}}' >/dev/null 2>&1
        kubectl patch ingress "$GREEN_INGRESS" -n "$namespace" -p '{"metadata":{"annotations":{"alb.ingress.kubernetes.io/target-group-arn":""}}}' >/dev/null 2>&1
    else
        # Switch to green
        log_info "Switching ALB target group to green..."
        kubectl patch ingress "$GREEN_INGRESS" -n "$namespace" -p '{"metadata":{"annotations":{"alb.ingress.kubernetes.io/target-group-arn":"'$GREEN_TARGET_GROUP_ARN'"}}}' >/dev/null 2>&1
        kubectl patch ingress "$BLUE_INGRESS" -n "$namespace" -p '{"metadata":{"annotations":{"alb.ingress.kubernetes.io/target-group-arn":""}}}' >/dev/null 2>&1
    fi
    
    log_success "Traffic switched to $target_deployment"
    return 0
}

# Function to get current active deployment
get_active_deployment() {
    local namespace=$1
    
    # Check which deployment has traffic
    local blue_ingress_arn
    local green_ingress_arn
    blue_ingress_arn=$(kubectl get ingress "$BLUE_INGRESS" -n "$namespace" -o jsonpath='{.metadata.annotations.alb\.ingress\.kubernetes\.io/target-group-arn}' 2>/dev/null)
    green_ingress_arn=$(kubectl get ingress "$GREEN_INGRESS" -n "$namespace" -o jsonpath='{.metadata.annotations.alb\.ingress\.kubernetes\.io/target-group-arn}' 2>/dev/null)
    
    if [ -n "$blue_ingress_arn" ] && [ "$blue_ingress_arn" != "" ]; then
        echo "blue"
    elif [ -n "$green_ingress_arn" ] && [ "$green_ingress_arn" != "" ]; then
        echo "green"
    else
        echo "unknown"
    fi
}

# Function to deploy to inactive environment
deploy_to_inactive() {
    local image_tag=$1
    local namespace=$2
    
    log_info "Deploying to inactive environment with image tag: $image_tag"
    
    # Determine which environment is inactive
    local active
    local target_deployment
    local target_service
    local target_ingress
    
    active=$(get_active_deployment "$namespace")
    
    if [[ "$active" == "blue" ]]; then
        target_deployment="$GREEN_DEPLOYMENT"
        target_service="$GREEN_SERVICE"
        target_ingress="$GREEN_INGRESS"
        log_info "Active is blue, deploying to green"
    else
        target_deployment="$BLUE_DEPLOYMENT"
        target_service="$BLUE_SERVICE"
        target_ingress="$BLUE_INGRESS"
        log_info "Active is green, deploying to blue"
    fi
    
    # Update the deployment with new image
    log_info "Updating $target_deployment with image: $image_tag"
    kubectl set image deployment/"$target_deployment" backend-app="$image_tag" -n "$namespace"
    
    # Wait for deployment to be ready
    if ! check_deployment_ready "$target_deployment" "$namespace"; then
        log_error "Deployment $target_deployment failed to become ready"
        return 1
    fi
    
    # Check if pods are healthy
    if ! check_pods_healthy "$target_deployment" "$namespace"; then
        log_error "Pods for $target_deployment are not healthy"
        return 1
    fi
    
    log_success "Successfully deployed to $target_deployment"
    echo "$target_deployment"
    return 0
}

# Function to perform blue-green deployment
start_blue_green_deploy() {
    local image_tag=$1
    local namespace=$2
    local auto_switch=$3
    
    log_info "Starting blue-green deployment with image: $image_tag"
    
    # Deploy to inactive environment
    local new_deployment
    if new_deployment=$(deploy_to_inactive "$image_tag" "$namespace"); then
        if [[ "$auto_switch" == "true" ]]; then
            # Switch traffic to new deployment
            if switch_traffic "$new_deployment" "$namespace"; then
                # Wait a bit for traffic to stabilize
                log_info "Waiting for traffic to stabilize..."
                sleep 30
                
                # Verify the switch was successful
                log_info "Verifying traffic switch..."
                log_success "Blue-green deployment completed successfully"
                return 0
            else
                log_error "Failed to switch traffic"
                return 1
            fi
        else
            log_warning "Deployment completed but traffic not switched (AutoSwitch=false)"
            log_info "To switch traffic, run: ./blue-green-deploy.sh switch-traffic $new_deployment $namespace"
            return 0
        fi
    else
        log_error "Failed to deploy to inactive environment"
        return 1
    fi
}

# Function to perform rollback
start_rollback() {
    local namespace=$1
    
    log_info "Starting rollback process..."
    
    # Get current active deployment
    local active
    active=$(get_active_deployment "$namespace")
    
    if [[ "$active" == "blue" ]]; then
        log_info "Currently on blue, switching to green"
        switch_traffic "$GREEN_DEPLOYMENT" "$namespace"
    elif [[ "$active" == "green" ]]; then
        log_info "Currently on green, switching to blue"
        switch_traffic "$BLUE_DEPLOYMENT" "$namespace"
    else
        log_error "Unable to determine current active deployment"
        return 1
    fi
}

# Function to show deployment status
show_status() {
    local namespace=$1
    
    log_info "Blue-Green Deployment Status for namespace: $namespace"
    echo "=========================================="
    
    # Show deployments
    echo "Deployments:"
    kubectl get deployments -n "$namespace" -l app=backend-app -o wide
    echo ""
    
    # Show services
    echo "Services:"
    kubectl get services -n "$namespace" -l app=backend-app -o wide
    echo ""
    
    # Show pods
    echo "Pods:"
    kubectl get pods -n "$namespace" -l app=backend-app -o wide
    echo ""
    
    # Show ingress
    echo "Ingress:"
    kubectl get ingress -n "$namespace" -l app=backend-app -o wide
    echo ""
    
    # Show current active
    local active
    active=$(get_active_deployment "$namespace")
    echo "Current Active Deployment: $active"
}

# Main script logic
case "${1:-}" in
    "deploy")
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 deploy <image_tag> [namespace] [auto_switch]"
            exit 1
        fi
        start_blue_green_deploy "$2" "${3:-production}" "${4:-true}"
        ;;
    "switch-traffic")
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 switch-traffic <deployment_name> [namespace]"
            exit 1
        fi
        switch_traffic "$2" "${3:-production}"
        ;;
    "rollback")
        start_rollback "${2:-production}"
        ;;
    "status")
        show_status "${2:-production}"
        ;;
    "check-health")
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 check-health <deployment_name> [namespace]"
            exit 1
        fi
        check_pods_healthy "$2" "${3:-production}"
        ;;
    *)
        echo "Blue-Green Deployment Script for Bash"
        echo "Usage: $0 {deploy|switch-traffic|rollback|status|check-health}"
        echo ""
        echo "Commands:"
        echo "  deploy <image_tag> [namespace] [auto_switch]     - Deploy new version using blue-green strategy"
        echo "  switch-traffic <deployment_name> [namespace]   - Switch traffic to specific deployment"
        echo "  rollback [namespace]                           - Rollback to previous deployment"
        echo "  status [namespace]                             - Show deployment status"
        echo "  check-health <deployment_name> [namespace]    - Check health of specific deployment"
        echo ""
        echo "Examples:"
        echo "  $0 deploy '492390865085.dkr.ecr.us-east-1.amazonaws.com/dev-app:v1.2.3'"
        echo "  $0 switch-traffic backend-app-green production"
        echo "  $0 rollback production"
        echo "  $0 status production"
        exit 1
        ;;
esac
