#!/bin/bash
# setup_kali.sh - OS Tuning for High-Speed Masscan & Proxy Operations

echo "🚀 Modifying OS limits for High-Speed network scanning..."

# 1. Increase File Descriptor limits
echo "* hard nofile 1000000" | sudo tee -a /etc/security/limits.conf
echo "* soft nofile 1000000" | sudo tee -a /etc/security/limits.conf
echo "root hard nofile 1000000" | sudo tee -a /etc/security/limits.conf
echo "root soft nofile 1000000" | sudo tee -a /etc/security/limits.conf

# 2. Modify sysctl (TCP Stack Tuning)
sudo sysctl -w fs.file-max=1000000
sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
sudo sysctl -w net.core.rmem_max=16777216
sudo sysctl -w net.core.wmem_max=16777216
sudo sysctl -w net.core.netdev_max_backlog=50000
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=30000
sudo sysctl -w net.ipv4.tcp_max_tw_buckets=2000000
sudo sysctl -w net.ipv4.tcp_tw_reuse=1
sudo sysctl -w net.ipv4.tcp_fin_timeout=10
sudo sysctl -w net.ipv4.tcp_slow_start_after_idle=0

# Save sysctl changes to persist across reboots (optional but good)
cat <<EOF | sudo tee /etc/sysctl.d/99-masscan.conf
fs.file-max=1000000
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.core.netdev_max_backlog=50000
net.ipv4.tcp_max_syn_backlog=30000
net.ipv4.tcp_max_tw_buckets=2000000
net.ipv4.tcp_tw_reuse=1
net.ipv4.tcp_fin_timeout=10
net.ipv4.tcp_slow_start_after_idle=0
EOF

echo "✅ OS Tuning applied! Please run 'ulimit -n 1000000' in your current terminal session before running masscan."
