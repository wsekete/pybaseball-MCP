#!/bin/bash

# GitHub Repository Setup Script
# This script helps push your local pybaseball MCP server to GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if we're in a git repository
check_git_repo() {
    if [ ! -d ".git" ]; then
        log_info "Initializing Git repository..."
        git init
        log_success "Git repository initialized"
    else
        log_info "Git repository already exists"
    fi
}

# Set up Git configuration if needed
setup_git_config() {
    log_info "Checking Git configuration..."
    
    if ! git config user.name > /dev/null; then
        read -p "Enter your Git username: " git_username
        git config user.name "$git_username"
    fi
    
    if ! git config user.email > /dev/null; then
        read -p "Enter your Git email: " git_email
        git config user.email "$git_email"
    fi
    
    log_success "Git configuration complete"
}

# Add GitHub remote
add_github_remote() {
    local repo_url="$1"
    
    # Check if origin remote exists
    if git remote | grep -q "origin"; then
        log_warning "Origin remote already exists"
        current_origin=$(git remote get-url origin)
        echo "Current origin: $current_origin"
        
        read -p "Do you want to update the origin URL? (y/N): " update_origin
        if [[ $update_origin =~ ^[Yy]$ ]]; then
            git remote set-url origin "$repo_url"
            log_success "Origin remote updated"
        fi
    else
        git remote add origin "$repo_url"
        log_success "Origin remote added"
    fi
}

# Stage and commit files
commit_files() {
    log_info "Staging files for commit..."
    
    # Add all files except those in .gitignore
    git add .
    
    # Check if there are changes to commit
    if git diff --staged --quiet; then
        log_warning "No changes to commit"
        return 0
    fi
    
    # Create commit
    log_info "Creating initial commit..."
    git commit -m "Initial commit: Pybaseball MCP Server

- Complete MCP server implementation with player, stats, and plotting tools
- Docker support for easy deployment
- Comprehensive documentation and examples
- CI/CD pipeline with GitHub Actions
- Installation scripts for multiple platforms
- Claude Desktop integration ready"
    
    log_success "Initial commit created"
}

# Push to GitHub
push_to_github() {
    log_info "Pushing to GitHub..."
    
    # Push to main branch
    if git branch | grep -q "main"; then
        git push -u origin main
    else
        # Create main branch if it doesn't exist
        git branch -M main
        git push -u origin main
    fi
    
    log_success "Code pushed to GitHub successfully!"
}

# Create GitHub repository (if using GitHub CLI)
create_github_repo() {
    if command -v gh &> /dev/null; then
        log_info "GitHub CLI detected. Do you want to create the repository?"
        read -p "Create GitHub repository 'pybaseball-MCP'? (y/N): " create_repo
        
        if [[ $create_repo =~ ^[Yy]$ ]]; then
            read -p "Make repository public? (y/N): " is_public
            
            if [[ $is_public =~ ^[Yy]$ ]]; then
                gh repo create pybaseball-MCP --public --description "A comprehensive Model Context Protocol (MCP) server for baseball statistics and analytics using pybaseball"
            else
                gh repo create pybaseball-MCP --private --description "A comprehensive Model Context Protocol (MCP) server for baseball statistics and analytics using pybaseball"
            fi
            
            log_success "GitHub repository created"
            return 0
        fi
    fi
    
    return 1
}

# Main setup process
main() {
    echo "============================================="
    echo "    GitHub Repository Setup"
    echo "============================================="
    echo ""
    
    # Change to script directory
    cd "$(dirname "$0")"
    
    # Check if GitHub CLI can create repo
    repo_created=false
    if create_github_repo; then
        repo_created=true
        repo_url="git@github.com:$(gh api user --jq .login)/pybaseball-MCP.git"
    fi
    
    # Manual setup if no GitHub CLI or user declined
    if [ "$repo_created" = false ]; then
        echo "Please create a GitHub repository manually:"
        echo "1. Go to https://github.com/new"
        echo "2. Repository name: pybaseball-MCP"
        echo "3. Description: A comprehensive Model Context Protocol (MCP) server for baseball statistics and analytics using pybaseball"
        echo "4. Choose public or private"
        echo "5. Do NOT initialize with README, .gitignore, or license (we have these already)"
        echo ""
        
        read -p "Enter the GitHub repository URL (SSH format): " repo_url
        
        if [ -z "$repo_url" ]; then
            log_error "Repository URL is required"
            exit 1
        fi
    fi
    
    # Setup Git
    check_git_repo
    setup_git_config
    add_github_remote "$repo_url"
    
    # Commit and push
    commit_files
    push_to_github
    
    echo ""
    echo "============================================="
    echo "           Setup Complete!"
    echo "============================================="
    echo ""
    log_success "Your Pybaseball MCP Server is now on GitHub!"
    echo ""
    echo "Repository URL: $repo_url"
    echo ""
    echo "Next steps:"
    echo "1. Visit your GitHub repository to verify everything uploaded correctly"
    echo "2. Consider creating a release tag: git tag v1.0.0 && git push origin v1.0.0"
    echo "3. Set up branch protection rules in GitHub repository settings"
    echo "4. Enable GitHub Actions if they haven't been enabled automatically"
    echo "5. Consider adding collaborators or setting up teams"
    echo ""
    echo "Your repository includes:"
    echo "- ✅ Complete MCP server implementation"
    echo "- ✅ Docker support"
    echo "- ✅ CI/CD pipeline"
    echo "- ✅ Installation scripts"
    echo "- ✅ Comprehensive documentation"
    echo ""
    echo "People can now install your MCP server with:"
    echo "git clone $repo_url && cd pybaseball-MCP && ./install.sh"
    echo ""
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "GitHub Repository Setup Script"
        echo ""
        echo "This script helps you push your Pybaseball MCP Server to GitHub"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --dry-run      Show what would be done without making changes"
        echo ""
        exit 0
        ;;
    --dry-run)
        echo "DRY RUN MODE - No changes will be made"
        echo ""
        echo "This script would:"
        echo "1. Initialize Git repository (if needed)"
        echo "2. Set up Git configuration"
        echo "3. Add GitHub remote"
        echo "4. Commit all files"
        echo "5. Push to GitHub"
        echo ""
        exit 0
        ;;
esac

# Run main setup
main "$@"
