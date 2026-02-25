#!/usr/bin/env bash

# manage-submodules.sh - A tool to manage project submodules

set -e

# Function to sign in to 1Password and hydrate secrets
hydrate_secrets() {
    echo "Signing in to 1Password..."
    # Since we're in a script, we use the standard command directly
    eval $(op signin)
    
    echo "Hydrating project secrets..."
    if [ -f "./quiver-secrets" ]; then
        ./quiver-secrets hydrate projects
    else
        go run cmd/quiver-secrets/main.go hydrate projects
    fi
}

echo "Quiver Submodule Manager"
echo "------------------------"
echo "What would you like to do?"
echo "1) Add a new submodule"
echo "2) Remove a submodule"
echo "3) Update a specific submodule"
echo "4) Update all submodules"
echo "5) Exit"
read -p "Select an option [1-5]: " choice

case $choice in
    1)
        read -p "Enter the repository URL: " repo_url
        read -p "Enter the destination path (e.g., projects/my-project): " dest_path
        echo "Adding submodule $repo_url to $dest_path..."
        git submodule add "$repo_url" "$dest_path"
        hydrate_secrets
        ;;
    2)
        # List existing submodules
        echo "Current submodules:"
        git submodule status
        read -p "Enter the path of the submodule to remove: " dest_path
        echo "Removing submodule at $dest_path..."
        git submodule deinit -f "$dest_path"
        rm -rf ".git/modules/$dest_path"
        git rm -f "$dest_path"
        echo "Submodule removed."
        ;;
    3)
        echo "Current submodules:"
        git submodule status
        read -p "Enter the path of the submodule to update: " dest_path
        echo "Updating submodule $dest_path..."
        git submodule update --init --remote "$dest_path"
        hydrate_secrets
        ;;
    4)
        echo "Updating all submodules..."
        git submodule update --init --recursive --remote
        hydrate_secrets
        ;;
    5)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo "Invalid option."
        exit 1
        ;;
esac

echo "Done!"
