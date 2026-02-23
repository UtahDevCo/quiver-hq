# Quiver HQ NixOS Configuration

This repository contains the complete NixOS and home-manager configuration for the hosts and development environments used at Quiver HQ. It is designed to be fully reproducible and managed via this git repository.

## Workflows

There are two primary workflows for using this repository: managing an existing system and installing a new system from scratch.

### 1. Day-to-Day System Management (Existing System)

This is the most common workflow. Use it to apply updates or configuration changes to a system that is already running this configuration.

1.  **Edit Configuration**: Make any desired changes to the `.nix` files in this repository.
2.  **Apply Changes**: From within this repository's root directory (`/home/chris/dev/quiver-hq`), run the following command to apply the configuration to your running system:

    ```bash
    sudo nixos-rebuild switch --flake .#quiver-wsl
    ```

    *   `sudo nixos-rebuild switch`: The standard command to build and activate a new system generation.
    *   `--flake .`: Tells the command to use the `flake.nix` in the current directory.
    *   `#quiver-wsl`: Specifies which `nixosConfigurations` output from your `flake.nix` to build and apply.

3.  **Commit**: Once you are happy with the changes, commit them to git to track your configuration's history.

    ```bash
    git add .
    git commit -m "feat: add new package and update shell alias"
    ```

### 2. "From Scratch" Installation (New System)

Use this workflow to install a completely new NixOS system (e.g., a new WSL instance, a new VM, or a new physical machine) using this repository as the source of truth.

1.  **Boot Installer**: Boot the target machine using a standard NixOS installer image.
2.  **Prepare Disks**: Partition and format the disks as required for your new system.
3.  **Mount Filesystems**: Mount the newly created filesystems under `/mnt`. For example, mount your root partition on `/mnt` and your boot partition on `/mnt/boot`.
4.  **Clone Repository**: Clone this repository onto the installation medium.

    ```bash
    git clone https://github.com/your-username/quiver-hq.git /mnt/etc/nixos
    ```
    *(Note: It's common practice to clone the configuration into `/mnt/etc/nixos`)*

5.  **Run Installation**: Instead of generating a new configuration, run `nixos-install` and point it directly to the host definition within your cloned flake:

    ```bash
    sudo nixos-install --flake /mnt/etc/nixos#quiver-wsl
    ```

After the installation is complete and you reboot, the new system will be running the exact configuration defined in this repository.

## Configuration Recommendations

Your configuration is well-structured. Here are a few recommendations to make it even more robust and portable.

### Use Portable Paths

Your `home.nix` contains aliases with hardcoded absolute paths (e.g., `/home/chris/dev/quiver-hq`). This can break if you clone the repo to a different location or use it for another user.

**Recommendation**: Modify the `reload` alias in `nixos/home.nix` to be independent of its absolute path. A more robust version would change directory to the known location first:

*   **From**: `alias reload="sudo nixos-rebuild switch --flake /home/chris/dev/quiver-hq#quiver-wsl"`
*   **To**: `alias reload='(cd /home/chris/dev/quiver-hq && sudo nixos-rebuild switch --flake .#quiver-wsl)'`

This ensures the command always runs from the correct directory context.

### Centralize Shell Configuration

You have correctly placed your Zsh configuration inside `home.nix` using `programs.zsh.initContent`. The file at `nixos/files/.zshrc` appears to be unused, as its content is managed by home-manager. This is good! Centralizing configuration in `home.nix` is the idiomatic approach.

### Hardware Configuration

The file `nixos/hosts/wsl/hardware-configuration.nix` is specific to your current machine. When installing on a new machine, NixOS will generate a new version of this file that is specific to that new hardware. Your current setup correctly isolates this file from the common configuration.
