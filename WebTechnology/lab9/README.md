# IT‑Planet - Ansible
The task was performed on Docker containers: one server (control node) and two clients.
The playbook collects the client’s IP addresses, OS versions, hostnames and free disk space, and stores this information on the server in `/etc/ansible/IT-Planet`.
## Quick start
```bash
make all
```
## Full cycle manually
```bash
docker compose build
docker compose up -d
docker compose exec -T server ansible-playbook -i /work/inventory.ini /work/site.yml
docker compose exec -T server ls -la /etc/ansible/IT-Planet
docker compose exec -T server cat /etc/ansible/IT-Planet/client1.txt
docker compose exec -T server cat /etc/ansible/IT-Planet/client2.txt
```
## What is collected
- Client IP addresses
- Client OS version
- Client names
- Free space on the root disk
Report format:
```
client_name: client1
client_ips: 172.20.0.3
os_version: Ubuntu 22.04.5 LTS
disk_free_root: 336G
```
## How it works
- `server` generates an SSH key in the shared Docker volume `itp-keys` and copies it to `/home/ansible/.ssh`.
- `client1` and `client2` read the public key from the same volume and place it in `authorized_keys`, after which they start `sshd`.
- Ansible on the server connects to the clients via SSH and executes commands to collect data.
- Reports are written to the server in `/etc/ansible/IT-Planet` (the `itp-reports` volume).
If there are any `ansible_key`/`ansible_key.pub` files left in the project directory from the old version, they can be deleted as they are no longer in use.
## Makefile commands
- `make build` - build images
- `make up` - start containers
- `make run` - start the playbook
- `make show` - display log files
- `make all` - full cycle
- `make down` - stop
- `make clean` - stop and delete volumes
