#!/usr/bin/env bash
set -euo pipefail

KEY_PRIV=/keys/ansible_key
KEY_PUB=/keys/ansible_key.pub

if [[ ! -f "$KEY_PRIV" ]]; then
  ssh-keygen -t ed25519 -N "" -f "$KEY_PRIV" >/dev/null
  chmod 600 "$KEY_PRIV"
  chmod 644 "$KEY_PUB"
fi

cp "$KEY_PRIV" /home/ansible/.ssh/id_ed25519
cp "$KEY_PUB" /home/ansible/.ssh/id_ed25519.pub
chown -R ansible:ansible /home/ansible/.ssh
chmod 600 /home/ansible/.ssh/id_ed25519

exec sleep infinity
