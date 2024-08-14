Sure, here's a README file and a script file for the commands you provided:

## README

This repository contains a script file that sets up a Kubernetes cluster on an Ubuntu machine using Docker and Containerd as the container runtime.

### Prerequisites

- Ubuntu 20.04 or later
- Root access or sudo privileges

### Installation

1. Run the following command to set the hostname of the machine:

```bash
sudo hostnamectl set-hostname ubuntu
```

2. Install the necessary packages:

```bash
sudo apt install -y net-tools
```

3. Create the script file named `kubernetes-setup.sh` and copy the following commands into it:

```bash
#!/bin/bash

# Install Docker
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install containerd.io

# Configure Containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml >/dev/null 2>&1
sudo sed -i 's/SystemdCgroup \= false/SystemdCgroup \= true/g' /etc/containerd/config.toml
sudo systemctl restart containerd
sudo systemctl enable containerd

# Load required kernel modules
sudo tee /etc/modules-load.d/containerd.conf <<EOF
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

# Configure sysctl parameters
sudo tee /etc/sysctl.d/kubernetes.conf <<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sudo sysctl --system

# Install Kubernetes components
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-get update

# Disable firewall
sudo systemctl stop ufw
sudo systemctl disable ufw

# Initialize the Kubernetes cluster
sudo kubeadm init --pod-network-cidr=10.42.0.0/16 --apiserver-advertise-address=192.168.122.204

# Deploy the Calico network plugin
kubectl create -f https://raw.githubusercontent.com/syslabtech/tmp/master/calico.yml
```

4. Make the script executable:

```bash
chmod +x kubernetes-setup.sh
```

5. Run the script with sudo privileges:

```bash
sudo ./kubernetes-setup.sh
```

The script will install Docker, configure Containerd, load required kernel modules, configure sysctl parameters, install Kubernetes components, disable the firewall, initialize the Kubernetes cluster, and deploy the Calico network plugin.

After running the script, you should have a Kubernetes cluster up and running on your Ubuntu machine.
