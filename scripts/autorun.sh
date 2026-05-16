#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${GITHUB_TOKEN:-}" ]]; then
  echo "GITHUB_TOKEN is required" >&2
  exit 1
fi

workflow_file="${WORKFLOW_FILE:-autobot.yaml}"
ref="${GITHUB_REF_NAME:-main}"
repo="${GITHUB_REPOSITORY}"

api_url="https://api.github.com/repos/${repo}/actions/workflows/${workflow_file}/dispatches"

curl -sS -X POST \
  -H "Authorization: Bearer ${GITHUB_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  -d "{\"ref\":\"${ref}\"}" \
  "${api_url}"

echo "Dispatched ${workflow_file} on ref ${ref}"
