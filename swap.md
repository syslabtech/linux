To increase swap memory in an Ubuntu system, you can create a swap file and configure it. Here’s a step-by-step guide on how to do this, including how to make the changes persistent by editing the `/etc/fstab` file.

## Steps to Increase Swap Memory

### 1. Check Existing Swap Space

Before adding swap space, check if there is any existing swap configured:

```bash
sudo swapon --show
```

If there is no output, it means no swap space is currently available. You can also check memory usage with:

```bash
free -h
```

### 2. Create a Swap File

To create a new swap file, use the `fallocate` command. For example, to create a 1 GB swap file, run:

```bash
sudo fallocate -l 1G /swap.img
```

You can adjust the size as needed (e.g., `2G`, `4G`, etc.).

### 3. Set Permissions

Change the permissions of the swap file to ensure that only the root user can read and write to it:

```bash
sudo chmod 600 /swap.img
```

### 4. Mark the File as Swap

Next, mark the file as a swap file using the `mkswap` command:

```bash
sudo mkswap /swap.img
```

### 5. Enable the Swap File

Activate the swap file with the following command:

```bash
sudo swapon /swap.img
```

### 6. Verify the Swap Space

To confirm that the swap space is active, use:

```bash
sudo swapon --show
```

You can also check the total memory status again with:

```bash
free -h
```

### 7. Make the Swap File Permanent

To ensure that the swap file is used after a reboot, you need to add it to the `/etc/fstab` file. Open the file in a text editor:

```bash
sudo nano /etc/fstab
```

Add the following line at the end of the file:

```
/swap.img none swap sw 0 0
```

Save and exit the editor (in nano, you can do this by pressing `CTRL + X`, then `Y`, and `Enter`).

### 8. Adjust Swappiness (Optional)

The swappiness parameter controls how often the system uses swap space. The default value is 60, but you can adjust it for better performance based on your needs. To check the current swappiness value:

```bash
cat /proc/sys/vm/swappiness
```

To temporarily change the swappiness value (e.g., to 10):

```bash
sudo sysctl vm.swappiness=10
```

To make this change permanent, add the following line to `/etc/sysctl.conf`:

```
vm.swappiness=10
```

## Conclusion

By following these steps, you can successfully increase the swap memory in your Ubuntu system and ensure that it persists across reboots. This can help improve system performance, especially in low-memory situations[1][4].

Citations:
[1] https://www.tecmint.com/add-swap-space-on-ubuntu/
[2] https://askubuntu.com/questions/168359/how-to-increase-swap-memory
[3] https://docs.vultr.com/how-to-add-swap-memory-in-ubuntu-24-04
[4] https://tecadmin.net/how-to-add-swap-space-in-ubuntu-22-04/
[5] https://www.linuxndroid.com/2021/02/how-to-create-swap-ram-in-linux.html?m=1
