"""Install a runtime-mounted player token through the supported Softmax client API."""
import argparse
import os
from pathlib import Path
from softmax.auth import fetch_cogames_whoami, save_user_token

parser = argparse.ArgumentParser()
parser.add_argument("--token-file", type=Path, required=True)
parser.add_argument("--player", required=True)
args = parser.parse_args()
os.umask(0o077)
token = args.token_file.read_text().strip()
identity = fetch_cogames_whoami(api_server="https://softmax.com/api", token=token)
assert identity.subject_type.lower() == "player", "A scoped PLAYER credential is required"
assert identity.subject_id == args.player, "Credential belongs to a different player"
assert not identity.is_softmax_admin, "Admin credentials are not accepted"
save_user_token(server="https://softmax.com/api", token=token)
print("Verified player credential installed through softmax.auth in ~/.softmax/credentials.yaml (mode 0600).")
