#!/usr/bin/env bash
# PostToolUse hook: after Edit/Write to collectors, renderer, template, or tests,
# run `make check && make test`. Exit 2 blocks-and-reports per Claude Code hook
# semantics; stderr is fed back to the model.
set -uo pipefail

payload="$(cat)"
file_path="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"

# Guard the brief's named paths (collectors, renderer/template, tests) plus the
# enforcement surface itself (gate finding): the linter, snapshots, Makefile,
# the sources ledger, and this hook's own config. Bash-tool writes bypass
# PostToolUse hooks by design — CI runs the same checks on every push and is
# the authority (see RISKS.md).
case "$file_path" in
  */collectors/*|*/site/*|*/tests/*|*/tools/*|*/data/*|*/Makefile|Makefile|*/governance/SOURCES.md|*/.claude/settings.json|*/.claude/hooks/*) ;;
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
