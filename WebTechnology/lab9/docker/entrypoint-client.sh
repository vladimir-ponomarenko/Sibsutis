#!/usr/bin/env bash
set -euo pipefail

KEY_PUB=/keys/ansible_key.pub

# wait for key from server
for i in {1..60}; do
  [[ -f "$KEY_PUB" ]] && break
  sleep 1
done

if [[ ! -f "$KEY_PUB" ]]; then
  echo "Public key not found: $KEY_PUB" >&2
  exit 1
fi

cat "$KEY_PUB" > /home/ansible/.ssh/authorized_keys
chown -R ansible:ansible /home/ansible/.ssh
chmod 600 /home/ansible/.ssh/authorized_keys

exec /usr/sbin/sshd -D
