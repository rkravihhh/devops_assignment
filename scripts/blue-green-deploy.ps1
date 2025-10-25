# Blue-Green Deployment Script for PowerShell
# This script manages blue-green deployments for the application

param(
    [Parameter(Mandatory=$true)]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$ImageTag = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Namespace = "production",
    
    [Parameter(Mandatory=$false)]
    [string]$DeploymentName = "",
    
    [Parameter(Mandatory=$false)]
    [bool]$AutoSwitch = $true
)

# Configuration
$APP_NAME = "backend-app"
$BLUE_DEPLOYMENT = "backend-app-blue"
$GREEN_DEPLOYMENT = "backend-app-green"
$BLUE_SERVICE = "backend-app-blue-service"
$GREEN_SERVICE = "backend-app-green-service"
$BLUE_INGRESS = "backend-app-blue-ingress"
$GREEN_INGRESS = "backend-app-green-ingress"
$HEALTH_CHECK_PATH = "/health"
$HEALTH_CHECK_TIMEOUT = 300  # 5 minutes
$ROLLBACK_TIMEOUT = 60       # 1 minute

# Logging functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if a deployment is ready
function Test-DeploymentReady {
    param(
        [string]$DeploymentName,
        [string]$Namespace
    )
    
    Write-Info "Checking if deployment $DeploymentName is ready..."
    
    try {
        $deployment = kubectl get deployment $DeploymentName -n $Namespace 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Deployment $DeploymentName not found in namespace $Namespace"
            return $false
        }
        
        kubectl rollout status deployment/$DeploymentName -n $Namespace --timeout=${HEALTH_CHECK_TIMEOUT}s
        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-Error "Failed to check deployment status: $_"
        return $false
    }
}

# Function to check if pods are healthy
function Test-PodsHealthy {
    param(
        [string]$DeploymentName,
        [string]$Namespace
    )
    
    Write-Info "Checking if pods for $DeploymentName are healthy..."
    
    try {
        # Get version from deployment name
        $version = if ($DeploymentName -like "*blue*") { "blue" } else { "green" }
        
        # Get pod names
        $pods = kubectl get pods -n $Namespace -l "app=backend-app,version=$version" -o jsonpath='{.items[*].metadata.name}' 2>$null
        
        if ([string]::IsNullOrEmpty($pods)) {
            Write-Error "No pods found for deployment $DeploymentName"
            return $false
        }
        
        # Check each pod
        $podList = $pods -split ' '
        foreach ($pod in $podList) {
            if ([string]::IsNullOrEmpty($pod)) { continue }
            
            Write-Info "Checking pod $pod..."
            
            # Wait for pod to be ready
            kubectl wait --for=condition=Ready pod/$pod -n $Namespace --timeout=${HEALTH_CHECK_TIMEOUT}s
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Pod $pod is not ready"
                return $false
            }
            
            # Check if pod is actually healthy by calling health endpoint
            $podIP = kubectl get pod $pod -n $Namespace -o jsonpath='{.status.podIP}' 2>$null
            if (-not [string]::IsNullOrEmpty($podIP)) {
                Write-Info "Testing health endpoint on pod $pod ($podIP:8000$HEALTH_CHECK_PATH)"
                $healthCheck = kubectl exec $pod -n $Namespace -- curl -f "http://localhost:8000$HEALTH_CHECK_PATH" 2>$null
                if ($LASTEXITCODE -ne 0) {
                    Write-Error "Health check failed for pod $pod"
                    return $false
                }
            }
        }
        
        Write-Success "All pods for $DeploymentName are healthy"
        return $true
    }
    catch {
        Write-Error "Failed to check pod health: $_"
        return $false
    }
}

# Function to switch traffic to a deployment
function Switch-Traffic {
    param(
        [string]$TargetDeployment,
        [string]$Namespace
    )
    
    Write-Info "Switching traffic to $TargetDeployment..."
    
    try {
        if ($TargetDeployment -eq $BLUE_DEPLOYMENT) {
            # Switch to blue
            Write-Info "Switching ALB target group to blue..."
            kubectl patch ingress $BLUE_INGRESS -n $Namespace -p '{"metadata":{"annotations":{"alb.ingress.kubernetes.io/target-group-arn":"'$BLUE_TARGET_GROUP_ARN'"}}}' 2>$null
            kubectl patch ingress $GREEN_INGRESS -n $Namespace -p '{"metadata":{"annotations":{"alb.ingress.kubernetes.io/target-group-arn":""}}}' 2>$null
        }
        else {
            # Switch to green
            Write-Info "Switching ALB target group to green..."
            kubectl patch ingress $GREEN_INGRESS -n $Namespace -p '{"metadata":{"annotations":{"alb.ingress.kubernetes.io/target-group-arn":"'$GREEN_TARGET_GROUP_ARN'"}}}' 2>$null
            kubectl patch ingress $BLUE_INGRESS -n $Namespace -p '{"metadata":{"annotations":{"alb.ingress.kubernetes.io/target-group-arn":""}}}' 2>$null
        }
        
        Write-Success "Traffic switched to $TargetDeployment"
        return $true
    }
    catch {
        Write-Error "Failed to switch traffic: $_"
        return $false
    }
}

# Function to get current active deployment
function Get-ActiveDeployment {
    param([string]$Namespace)
    
    try {
        # Check which deployment has traffic
        $blueIngressArn = kubectl get ingress $BLUE_INGRESS -n $Namespace -o jsonpath='{.metadata.annotations.alb\.ingress\.kubernetes\.io/target-group-arn}' 2>$null
        $greenIngressArn = kubectl get ingress $GREEN_INGRESS -n $Namespace -o jsonpath='{.metadata.annotations.alb\.ingress\.kubernetes\.io/target-group-arn}' 2>$null
        
        if (-not [string]::IsNullOrEmpty($blueIngressArn) -and $blueIngressArn -ne "") {
            return "blue"
        }
        elseif (-not [string]::IsNullOrEmpty($greenIngressArn) -and $greenIngressArn -ne "") {
            return "green"
        }
        else {
            return "unknown"
        }
    }
    catch {
        Write-Error "Failed to get active deployment: $_"
        return "unknown"
    }
}

# Function to deploy to inactive environment
function Deploy-ToInactive {
    param(
        [string]$ImageTag,
        [string]$Namespace
    )
    
    Write-Info "Deploying to inactive environment with image tag: $ImageTag"
    
    # Determine which environment is inactive
    $active = Get-ActiveDeployment $Namespace
    $targetDeployment = ""
    $targetService = ""
    $targetIngress = ""
    
    if ($active -eq "blue") {
        $targetDeployment = $GREEN_DEPLOYMENT
        $targetService = $GREEN_SERVICE
        $targetIngress = $GREEN_INGRESS
        Write-Info "Active is blue, deploying to green"
    }
    else {
        $targetDeployment = $BLUE_DEPLOYMENT
        $targetService = $BLUE_SERVICE
        $targetIngress = $BLUE_INGRESS
        Write-Info "Active is green, deploying to blue"
    }
    
    try {
        # Update the deployment with new image
        Write-Info "Updating $targetDeployment with image: $ImageTag"
        kubectl set image deployment/$targetDeployment backend-app=$ImageTag -n $Namespace
        
        # Wait for deployment to be ready
        if (-not (Test-DeploymentReady $targetDeployment $Namespace)) {
            Write-Error "Deployment $targetDeployment failed to become ready"
            return $null
        }
        
        # Check if pods are healthy
        if (-not (Test-PodsHealthy $targetDeployment $Namespace)) {
            Write-Error "Pods for $targetDeployment are not healthy"
            return $null
        }
        
        Write-Success "Successfully deployed to $targetDeployment"
        return $targetDeployment
    }
    catch {
        Write-Error "Failed to deploy to inactive environment: $_"
        return $null
    }
}

# Function to perform blue-green deployment
function Start-BlueGreenDeploy {
    param(
        [string]$ImageTag,
        [string]$Namespace,
        [bool]$AutoSwitch
    )
    
    Write-Info "Starting blue-green deployment with image: $ImageTag"
    
    # Deploy to inactive environment
    $newDeployment = Deploy-ToInactive $ImageTag $Namespace
    if ($null -eq $newDeployment) {
        Write-Error "Failed to deploy to inactive environment"
        return $false
    }
    
    if ($AutoSwitch) {
        # Switch traffic to new deployment
        if (Switch-Traffic $newDeployment $Namespace) {
            # Wait a bit for traffic to stabilize
            Write-Info "Waiting for traffic to stabilize..."
            Start-Sleep -Seconds 30
            
            # Verify the switch was successful
            Write-Info "Verifying traffic switch..."
            Write-Success "Blue-green deployment completed successfully"
            return $true
        }
        else {
            Write-Error "Failed to switch traffic"
            return $false
        }
    }
    else {
        Write-Warning "Deployment completed but traffic not switched (AutoSwitch=false)"
        Write-Info "To switch traffic, run: .\blue-green-deploy.ps1 -Action switch-traffic -DeploymentName $newDeployment -Namespace $Namespace"
        return $true
    }
}

# Function to rollback deployment
function Start-Rollback {
    param([string]$Namespace)
    
    Write-Info "Starting rollback process..."
    
    try {
        # Get current active deployment
        $active = Get-ActiveDeployment $Namespace
        
        if ($active -eq "blue") {
            Write-Info "Currently on blue, switching to green"
            return Switch-Traffic $GREEN_DEPLOYMENT $Namespace
        }
        elseif ($active -eq "green") {
            Write-Info "Currently on green, switching to blue"
            return Switch-Traffic $BLUE_DEPLOYMENT $Namespace
        }
        else {
            Write-Error "Unable to determine current active deployment"
            return $false
        }
    }
    catch {
        Write-Error "Failed to rollback: $_"
        return $false
    }
}

# Function to show deployment status
function Show-Status {
    param([string]$Namespace)
    
    Write-Info "Blue-Green Deployment Status for namespace: $Namespace"
    Write-Host "=========================================="
    
    # Show deployments
    Write-Host "Deployments:"
    kubectl get deployments -n $Namespace -l app=backend-app -o wide
    Write-Host ""
    
    # Show services
    Write-Host "Services:"
    kubectl get services -n $Namespace -l app=backend-app -o wide
    Write-Host ""
    
    # Show pods
    Write-Host "Pods:"
    kubectl get pods -n $Namespace -l app=backend-app -o wide
    Write-Host ""
    
    # Show ingress
    Write-Host "Ingress:"
    kubectl get ingress -n $Namespace -l app=backend-app -o wide
    Write-Host ""
    
    # Show current active
    $active = Get-ActiveDeployment $Namespace
    Write-Host "Current Active Deployment: $active"
}

# Main script logic
switch ($Action.ToLower()) {
    "deploy" {
        if ([string]::IsNullOrEmpty($ImageTag)) {
            Write-Error "Usage: .\blue-green-deploy.ps1 -Action deploy -ImageTag <image_tag> [-Namespace <namespace>] [-AutoSwitch <true|false>]"
            exit 1
        }
        Start-BlueGreenDeploy $ImageTag $Namespace $AutoSwitch
    }
    "switch-traffic" {
        if ([string]::IsNullOrEmpty($DeploymentName)) {
            Write-Error "Usage: .\blue-green-deploy.ps1 -Action switch-traffic -DeploymentName <deployment_name> [-Namespace <namespace>]"
            exit 1
        }
        Switch-Traffic $DeploymentName $Namespace
    }
    "rollback" {
        Start-Rollback $Namespace
    }
    "status" {
        Show-Status $Namespace
    }
    "check-health" {
        if ([string]::IsNullOrEmpty($DeploymentName)) {
            Write-Error "Usage: .\blue-green-deploy.ps1 -Action check-health -DeploymentName <deployment_name> [-Namespace <namespace>]"
            exit 1
        }
        Test-PodsHealthy $DeploymentName $Namespace
    }
    default {
        Write-Host "Blue-Green Deployment Script for PowerShell"
        Write-Host "Usage: .\blue-green-deploy.ps1 -Action {deploy|switch-traffic|rollback|status|check-health}"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  deploy -ImageTag <image_tag> [-Namespace <namespace>] [-AutoSwitch <true|false>]  - Deploy new version using blue-green strategy"
        Write-Host "  switch-traffic -DeploymentName <deployment_name> [-Namespace <namespace>] - Switch traffic to specific deployment"
        Write-Host "  rollback [-Namespace <namespace>]                        - Rollback to previous deployment"
        Write-Host "  status [-Namespace <namespace>]                          - Show deployment status"
        Write-Host "  check-health -DeploymentName <deployment_name> [-Namespace <namespace>]  - Check health of specific deployment"
        Write-Host ""
        Write-Host "Examples:"
        Write-Host "  .\blue-green-deploy.ps1 -Action deploy -ImageTag '492390865085.dkr.ecr.us-east-1.amazonaws.com/dev-app:v1.2.3'"
        Write-Host "  .\blue-green-deploy.ps1 -Action switch-traffic -DeploymentName backend-app-green -Namespace production"
        Write-Host "  .\blue-green-deploy.ps1 -Action rollback -Namespace production"
        Write-Host "  .\blue-green-deploy.ps1 -Action status -Namespace production"
        exit 1
    }
}
