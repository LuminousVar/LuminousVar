#!/usr/bin/env bash
set -euo pipefail

# Append a WIB timestamp to a daily log
log_file="logs/daily.md"
mkdir -p "$(dirname "${log_file}")"

wib_time=$(TZ=Asia/Jakarta date "+%Y-%m-%d %H:%M %Z")
note_text="${NOTE:-update several changes}"

echo "${wib_time} - auto update | Note: ${note_text}" >> "${log_file}"

commit_message="${note_text}"
if [[ ! "${commit_message}" =~ ^[Uu]pdate: ]]; then
	commit_message="update: ${commit_message}"
fi

if [[ -n "${GITHUB_ENV:-}" ]]; then
	echo "COMMIT_MESSAGE=${commit_message}" >> "${GITHUB_ENV}"
fi
