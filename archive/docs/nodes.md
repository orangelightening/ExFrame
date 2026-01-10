# OMV Co-Pilot Knowledge Graph Nodes

**Generated**: 2026-01-03
**Total Patterns**: 24

---

## Storage Patterns (7)

### omv-001: SMB share inaccessible from Windows
- **Category**: services
- **Symptoms**: Windows cannot access \\server\share, Network path not found error, Timeout when connecting
- **Triggers**: smb not working, can't access share, windows network error
- **Diagnostics**:
  - Check SMB service status: `systemctl status smbd`
  - Verify share exists: `smbstatus -s`
- **Solutions**:
  1. Restart SMB service: `systemctl restart smbd`
  2. Check firewall rules: `iptables -L -n | grep 445`
- **Confidence**: 0.9

### omv-002: High disk usage warning
- **Category**: storage
- **Symptoms**: Disk usage above 90%, Cannot write files, Out of space errors
- **Triggers**: disk full, no space, disk usage high
- **Diagnostics**:
  - Check disk usage: `df -h`
  - Find large files: `du -ah / | sort -rh | head -20`
- **Solutions**:
  1. Clean package cache: `apt clean`
  2. Remove old logs: `journalctl --vacuum-time=7d`
  3. Find and remove large duplicates: `find / -type f -size +100M 2>/dev/null`
- **Confidence**: 0.95

### omv-003: RAID array degraded
- **Category**: storage
- **Symptoms**: RAID shows degraded state, One or more drives failed, Missing drive in array, mdadm shows degraded
- **Triggers**: raid degraded, raid failed, drive failed, array degraded
- **Diagnostics**:
  - Check RAID status: `cat /proc/mdstat`
  - Check mdadm detail: `mdadm --detail /dev/mdX`
  - Check SMART status: `smartctl -a /dev/sdX`
- **Solutions**:
  1. Identify failed drive: `mdadm --detail /dev/mdX | grep -i failed`
  2. Remove failed drive from array: `mdadm /dev/mdX --remove /dev/sdX`
  3. Add replacement drive: `mdadm /dev/mdX --add /dev/sdX`
  4. Monitor rebuild progress: `cat /proc/mdstat`
- **Related Patterns**: omv-015, omv-016
- **Confidence**: 0.95

### omv-004: ZFS pool degraded or faulted
- **Category**: storage
- **Symptoms**: ZFS pool shows degraded, Pool is unavailable, ZFS faulted state, Missing ZFS device
- **Triggers**: zfs degraded, zfs faulted, zfs pool error, zfs unavailable
- **Diagnostics**:
  - Check ZFS pool status: `zpool status`
  - List ZFS datasets: `zfs list`
  - Check ZFS events: `zpool events`
- **Solutions**:
  1. Replace failed disk: `zpool replace poolname /dev/sdX`
  2. Online disk again: `zpool online poolname /dev/sdX`
  3. Clear pool errors: `zpool clear poolname`
  4. Scrub the pool: `zpool scrub poolname`
- **Related Patterns**: omv-015
- **Confidence**: 0.9

### omv-005: Filesystem corruption detected
- **Category**: storage
- **Symptoms**: Filesystem errors in dmesg, Read-only filesystem, I/O errors on disk, Filesystem check required
- **Triggers**: filesystem corruption, fsck required, i/o error, read only filesystem
- **Diagnostics**:
  - Check dmesg for errors: `dmesg | grep -i error`
  - Check filesystem type: `blkid /dev/sdX`
  - Test disk health: `smartctl -a /dev/sdX`
- **Solutions**:
  1. Unmount filesystem: `umount /dev/sdX`
  2. Run filesystem check (ext4): `fsck.ext4 -y /dev/sdX`
  3. Run filesystem check (btrfs): `btrfs scrub start /mountpoint`
  4. Run filesystem check (xfs): `xfs_repair -L /dev/sdX`
- **Related Patterns**: omv-015
- **Confidence**: 0.85

### omv-006: Disk not showing up in OMV
- **Category**: storage
- **Symptoms**: New disk not detected, Disk missing from web interface, Can't see drive
- **Triggers**: disk not detected, disk not showing, can't see drive, missing disk
- **Diagnostics**:
  - List all disks: `lsblk`
  - Check for USB devices: `lsusb`
  - Check kernel messages: `dmesg | grep -i sd`
- **Solutions**:
  1. Rescan SCSI bus: `echo '- - -' > /sys/class/scsi_host/host0/scan`
  2. Check disk controller: `lspci | grep -i storage`
  3. Install file system tools: `apt install ntfs-3g exfat-fuse`
  4. Reset USB controller: `echo '1-1' > /sys/bus/usb/drivers/usb/unbind; echo '1-1' > /sys/bus/usb/drivers/usb/bind`
- **Related Patterns**: omv-015
- **Confidence**: 0.8

### omv-007: SMART drive error reported
- **Category**: storage
- **Symptoms**: SMART error warning, Drive predicted to fail, Bad sectors detected, Reallocated sector count
- **Triggers**: smart error, drive failing, bad sectors, predicted failure
- **Diagnostics**:
  - Check SMART status: `smartctl -a /dev/sdX`
  - Run SMART test: `smartctl -t long /dev/sdX`
  - Check test results: `smartctl -l selftest /dev/sdX`
- **Solutions**:
  1. Backup immediately: `rsync -av /mountpoint/ /backup/`
  2. Replace drive: `omv-rpc DiskMgmt removeDisk '{"devicename": "/dev/sdX"}'`
  3. Monitor for more errors: `watch smartctl -a /dev/sdX`
- **Related Patterns**: omv-003, omv-015
- **Confidence**: 0.95

### omv-008: Filesystem mount failed
- **Category**: storage
- **Symptoms**: Mount failed in boot, Emergency mode, Cannot access data, Mount point empty
- **Triggers**: mount failed, emergency mode, can't mount, filesystem not mounted
- **Diagnostics**:
  - Check mount status: `mount | grep /srv`
  - Check /etc/fstab: `cat /etc/fstab`
  - Check systemd mount units: `systemctl list-units | grep mount`
- **Solutions**:
  1. Manually mount filesystem: `mount /dev/sdX /mountpoint`
  2. Fix UUID in fstab: `blkid /dev/sdX`
  3. Check filesystem: `fsck -y /dev/sdX`
  4. Comment out bad entry: `sed -i '/mountpoint/s/^/#/' /etc/fstab`
- **Related Patterns**: omv-005
- **Confidence**: 0.85

---

## Network Patterns (5)

### omv-009: Network interface not working
- **Category**: network
- **Symptoms**: No network connectivity, Interface shows down, Can't ping server, No IP address assigned
- **Triggers**: no network, interface down, can't connect, no ip address
- **Diagnostics**:
  - List interfaces: `ip link show`
  - Check IP addresses: `ip addr show`
  - Check interface status: `cat /sys/class/net/eth0/operstate`
- **Solutions**:
  1. Bring interface up: `ip link set eth0 up`
  2. Request DHCP: `dhclient eth0`
  3. Restart networking: `systemctl restart networking`
  4. Check cable connection: `ethtool eth0`
- **Related Patterns**: omv-010
- **Confidence**: 0.85

### omv-010: Cannot access OMV web interface
- **Category**: network
- **Symptoms**: Web UI won't load, Connection refused on port 80, Can't reach OMV admin panel
- **Triggers**: web ui not working, can't access web, admin panel down, port 80 not working
- **Diagnostics**:
  - Check nginx status: `systemctl status nginx`
  - Check web ports: `netstat -tlnp | grep -E ':(80|443)'`
  - Check nginx logs: `tail -50 /var/log/nginx/error.log`
- **Solutions**:
  1. Restart nginx: `systemctl restart nginx`
  2. Restart PHP-FPM: `systemctl restart php7.4-fpm`
  3. Check nginx config: `nginx -t`
  4. Check firewall: `iptables -L -n | grep -E '(80|443)'`
- **Related Patterns**: omv-019
- **Confidence**: 0.9

### omv-011: Firewall blocking access
- **Category**: network
- **Symptoms**: Can't connect from network, Connection timeout, Ports filtered, Works locally but not remotely
- **Triggers**: firewall blocking, can't connect, port blocked, connection timeout
- **Diagnostics**:
  - Check iptables rules: `iptables -L -n -v`
  - Check UFW status: `ufw status`
  - Check open ports: `ss -tlnp`
- **Solutions**:
  1. Allow SMB port: `ufw allow 445/tcp`
  2. Allow SSH port: `ufw allow 22/tcp`
  3. Allow web ports: `ufw allow 80/tcp && ufw allow 443/tcp`
  4. Disable firewall temporarily: `ufw disable`
- **Related Patterns**: omv-001
- **Confidence**: 0.85

### omv-012: DNS resolution not working
- **Category**: network
- **Symptoms**: Can't resolve hostnames, Network works but no DNS, Unknown host errors
- **Triggers**: dns not working, can't resolve, unknown host, name resolution failed
- **Diagnostics**:
  - Check DNS config: `cat /etc/resolv.conf`
  - Test DNS query: `nslookup google.com`
  - Ping DNS server: `ping -c 3 8.8.8.8`
- **Solutions**:
  1. Set Google DNS: `echo 'nameserver 8.8.8.8' > /etc/resolv.conf`
  2. Restart systemd-resolved: `systemctl restart systemd-resolved`
  3. Flush DNS cache: `systemd-resolve --flush-caches`
  4. Configure via OMV web UI: Navigate to Network > DNS
- **Confidence**: 0.8

### omv-013: Slow network transfer speeds
- **Category**: network
- **Symptoms**: Very slow file copies, Network bottleneck, Not getting full speed
- **Triggers**: slow network, slow transfer, network bottleneck, slow speed
- **Diagnostics**:
  - Check interface speed: `ethtool eth0`
  - Test network speed: `iperf3 -s`
  - Check for errors: `ip -s link show eth0`
- **Solutions**:
  1. Verify gigabit negotiation: `ethtool -s eth0 speed 1000 duplex full autoneg on`
  2. Disable offloading: `ethtool -K eth0 tso off`
  3. Check cable quality: `dmesg | grep -i eth0`
  4. Enable SMB multichannel: `omv-config setf 'smb.multichannel' 'true'`
- **Related Patterns**: omv-020
- **Confidence**: 0.75

---

## Service Patterns (5)

### omv-014: NFS share not accessible
- **Category**: services
- **Symptoms**: Can't mount NFS share, Permission denied on NFS, NFS timeout
- **Triggers**: nfs not working, can't mount nfs, nfs timeout, nfs permission denied
- **Diagnostics**:
  - Check NFS server status: `systemctl status nfs-server`
  - Check exports: `exportfs -v`
  - Check showmount: `showmount -e localhost`
- **Solutions**:
  1. Restart NFS server: `systemctl restart nfs-server`
  2. Re-export shares: `exportfs -ra`
  3. Check exports syntax: `cat /etc/exports`
  4. Allow NFS through firewall: `ufw allow from 192.168.0.0/24 to any port nfs`
- **Related Patterns**: omv-001
- **Confidence**: 0.85

### omv-015: SSH access denied
- **Category**: services
- **Symptoms**: Permission denied (publickey), Can't SSH to server, Authentication failed
- **Triggers**: ssh denied, can't ssh, authentication failed, ssh not working
- **Diagnostics**:
  - Check SSH status: `systemctl status ssh`
  - Check SSH logs: `tail -50 /var/log/auth.log`
  - Verify SSH config: `sshd -t`
- **Solutions**:
  1. Restart SSH service: `systemctl restart ssh`
  2. Check password auth: `grep PasswordAuthentication /etc/ssh/sshd_config`
  3. Enable password auth: `sed -i 's/#PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config`
  4. Check user permissions: `groups username`
- **Confidence**: 0.9

### omv-016: OMV web interface shows errors
- **Category**: services
- **Symptoms**: PHP errors in web UI, White page in browser, RPC errors in interface, Can't save settings
- **Triggers**: web ui error, php error, rpc error, can't save settings
- **Diagnostics**:
  - Check PHP-FPM status: `systemctl status php*-fpm`
  - Check PHP error log: `tail -100 /var/log/php*-fpm.log`
  - Check OMV RPC: `curl -s http://localhost/rpc.php`
- **Solutions**:
  1. Restart PHP-FPM: `systemctl restart php*-fpm`
  2. Clear OMV cache: `rm -rf /var/cache/openmediavault/*`
  3. Fix permissions: `omv-mkconf nginx`
  4. Restart openmediavault: `systemctl restart openmediavault-engined`
- **Related Patterns**: omv-010
- **Confidence**: 0.85

### omv-017: Docker service not starting
- **Category**: services
- **Symptoms**: Docker won't start, Containers not running, Can't access Portainer
- **Triggers**: docker not working, docker won't start, containers not running, portainer down
- **Diagnostics**:
  - Check Docker status: `systemctl status docker`
  - List containers: `docker ps -a`
  - Check Docker logs: `journalctl -u docker -n 50`
- **Solutions**:
  1. Restart Docker: `systemctl restart docker`
  2. Clean Docker system: `docker system prune -f`
  3. Check disk space: `df /var/lib/docker`
  4. Verify Docker daemon config: `docker info`
- **Related Patterns**: omv-002
- **Confidence**: 0.85

---

## Performance Patterns (3)

### omv-018: High CPU usage
- **Category**: performance
- **Symptoms**: CPU at 100%, System slow to respond, High load average
- **Triggers**: high cpu, cpu 100, slow system, high load
- **Diagnostics**:
  - Check CPU usage: `top -bn1 | head -20`
  - Check load average: `uptime`
  - Find CPU intensive processes: `ps aux --sort=-%cpu | head -10`
- **Solutions**:
  1. Kill runaway process: `kill -9 PID`
  2. Check for cron jobs: `crontab -l`
  3. Reduce Docker limits: `docker update --cpus=2 container_name`
  4. Check for malware: `ps aux | grep -v grep | grep -v root`
- **Related Patterns**: omv-020
- **Confidence**: 0.8

### omv-019: Memory exhaustion
- **Category**: performance
- **Symptoms**: Out of memory errors, System swapping, Processes killed by OOM, Very slow response
- **Triggers**: out of memory, oom killer, memory full, high memory usage
- **Diagnostics**:
  - Check memory usage: `free -h`
  - Check swap usage: `swapon --show`
  - Find memory hogs: `ps aux --sort=-%mem | head -10`
- **Solutions**:
  1. Clear page cache: `sync; echo 3 > /proc/sys/vm/drop_caches`
  2. Stop memory hungry process: `kill -9 PID`
  3. Reduce Docker memory: `docker update --memory=4g container_name`
  4. Add swap: `fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile`
- **Related Patterns**: omv-018
- **Confidence**: 0.85

### omv-020: Slow disk I/O performance
- **Category**: performance
- **Symptoms**: Very slow disk operations, High iowait, Disk bottleneck
- **Triggers**: slow disk, high iowait, disk bottleneck, slow i/o
- **Diagnostics**:
  - Check disk I/O: `iostat -x 1 5`
  - Check iowait: `top -bn1 | grep -i wa`
  - Test disk speed: `hdparm -Tt /dev/sdX`
- **Solutions**:
  1. Check for failing disk: `smartctl -a /dev/sdX`
  2. Use noop scheduler for SSD: `echo noop > /sys/block/sdX/queue/scheduler`
  3. Align partitions: `parted /dev/sdX align-check opt 1`
  4. Enable write-back cache: `hdparm -W1 /dev/sdX`
- **Related Patterns**: omv-007, omv-013
- **Confidence**: 0.75

---

## Security Patterns (4)

### omv-021: Permission denied on share
- **Category**: security
- **Symptoms**: Access denied to files, Can't write to share, Permission errors
- **Triggers**: permission denied, access denied, can't write, permission error
- **Diagnostics**:
  - Check file permissions: `ls -la /path/to/share`
  - Check ownership: `stat /path/to/share`
  - Check user groups: `groups username`
- **Solutions**:
  1. Fix permissions: `chmod -R 770 /path/to/share`
  2. Fix ownership: `chown -R user:group /path/to/share`
  3. Check ACLs: `getfacl /path/to/share`
  4. Set default ACL: `setfacl -d -m g:group:rwx /path/to/share`
- **Confidence**: 0.9

### omv-022: SSH brute force attack detected
- **Category**: security
- **Symptoms**: Many failed SSH logins, High auth log activity, Dictionary attack
- **Triggers**: ssh attack, brute force, failed logins, dictionary attack
- **Diagnostics**:
  - Count failed logins: `grep 'Failed password' /var/log/auth.log | wc -l`
  - Show top attackers: `grep 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr | head -10`
  - Check recent failures: `tail -100 /var/log/auth.log | grep Failed`
- **Solutions**:
  1. Install fail2ban: `apt install fail2ban`
  2. Block specific IP: `iptables -A INPUT -s IP_ADDRESS -j DROP`
  3. Change SSH port: `sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config`
  4. Disable password auth: `sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config`
- **Confidence**: 0.95

### omv-023: Ransomware or malware detected
- **Category**: security
- **Symptoms**: Files being encrypted, Strange file extensions, Ransom notes appearing, Files disappearing
- **Triggers**: ransomware, files encrypted, malware, virus
- **Diagnostics**:
  - Check for encrypted files: `find /srv -name '*.encrypted' 2>/dev/null | head -20`
  - Check for ransom notes: `find /srv -name '*RECOVER*' -o -name '*README*' 2>/dev/null`
  - Check recent file changes: `find /srv -mtime -1 -type f | head -50`
- **Solutions**:
  1. STOP: Disconnect network immediately: `ifconfig eth0 down`
  2. Shutdown SMB shares: `systemctl stop smbd`
  3. Do NOT reboot yet: Save memory dump for forensics
  4. Contact security professional: Document all symptoms and logs
- **Confidence**: 0.95

### omv-024: User cannot login to web UI
- **Category**: security
- **Symptoms**: Login failed on web interface, Wrong password error, Account locked
- **Triggers**: can't login, login failed, wrong password, account locked
- **Diagnostics**:
  - Check user exists: `grep username /etc/passwd`
  - Check web UI logs: `tail -50 /var/log/openmediavault/openmediavault.log`
  - Verify password: `omv-rpc UserMgmt getUser '{"username": "admin"}'`
- **Solutions**:
  1. Reset admin password: `omv-firstaid`
  2. Reset via command line: `omv-rpc UserMgmt setUser '{"username": "admin", "password": "newpass"}'`
  3. Clear browser cache: Clear cookies and cache
  4. Check for failed login attempts: `fail2ban-client status sshd`
- **Related Patterns**: omv-022
- **Confidence**: 0.85

---

## Statistics

| Category | Count |
|----------|-------|
| Storage | 7 |
| Network | 5 |
| Services | 5 |
| Performance | 3 |
| Security | 4 |
| **Total** | **24** |

## Confidence Distribution

| Confidence Range | Count |
|------------------|-------|
| 0.95 (Very High) | 5 |
| 0.90-0.94 (High) | 3 |
| 0.80-0.89 (Medium) | 13 |
| 0.75-0.79 (Low-Medium) | 3 |
