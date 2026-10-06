#!/usr/bin/env bash
set -euo pipefail
umask 077
: "${SOFTMAX_RESEARCH_DIR:=$HOME/workspaces/rohit-optimizer}"
: "${SOFTMAX_POLICY_DIR:=$HOME/workspaces/rohit-gota-policy}"
: "${SOFTMAX_RESEARCH_REF:=codex/hermes-demo-profile}"
command -v git >/dev/null
command -v uv >/dev/null
clone_workspace() {
  local remote="$1" destination="$2" branch="$3"
  if [ -e "$destination" ]; then
    local configured_remote
    configured_remote="$(git -C "$destination" config --get remote.origin.url)"
    test "${configured_remote%.git}" = "${remote%.git}"
    git -C "$destination" status --short
  else
    mkdir -p "$(dirname "$destination")"
    git clone --branch "$branch" "$remote" "$destination"
  fi
}
clone_workspace https://github.com/Metta-AI/rohit-optimizer.git "$SOFTMAX_RESEARCH_DIR" "$SOFTMAX_RESEARCH_REF"
clone_workspace https://github.com/Metta-AI/rohit-gota-policy.git "$SOFTMAX_POLICY_DIR" main
uv sync --frozen --project "$SOFTMAX_RESEARCH_DIR" --python 3.12
"$SOFTMAX_RESEARCH_DIR/.venv/bin/coworld" --help >/dev/null
printf 'Research revision: '
git -C "$SOFTMAX_RESEARCH_DIR" rev-parse HEAD
printf 'Policy revision: '
git -C "$SOFTMAX_POLICY_DIR" rev-parse HEAD
printf '%s\n' 'CLI installed. Configure scoped auth before running experiments; no experiment was submitted.'
