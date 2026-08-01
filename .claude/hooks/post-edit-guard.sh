#!/usr/bin/env bash
# PostToolUse hook: after Edit/Write to collectors, renderer, template, or tests,
# run `make check && make test`. Exit 2 blocks-and-reports per Claude Code hook
# semantics; stderr is fed back to the model.
set -uo pipefail

payload="$(cat)"
file_path="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"

# Only guard the paths the brief names: collectors, renderer/template, tests.
case "$file_path" in
  */collectors/*|*/site/*|*/tests/*) ;;
  *) exit 0 ;;
esac

cd "$(dirname "$0")/../.." || exit 0

out="$(make check 2>&1 && make test 2>&1)"
status=$?
if [ $status -ne 0 ]; then
  echo "post-edit-guard: make check/test FAILED after editing $file_path" >&2
  echo "$out" | tail -40 >&2
  exit 2
fi
exit 0
