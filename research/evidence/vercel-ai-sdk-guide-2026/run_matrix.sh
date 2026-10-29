#!/bin/bash
# Type-check the same four minimal programs plus seven single-symbol probes
# against ai major 5, 6 and 7.
#
# Self-contained: creates its own projects under $TMPDIR/mx, installs the
# dependency sets in ./programs/package.v{5,6,7}.json, copies the programs and
# writes every raw tsc result into $TMPDIR/mx/results.
#
# Usage: bash run_matrix.sh      (needs node, npm, python3 and npm-registry access)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
BASE="${TMPDIR:?run_matrix.sh needs TMPDIR set to a private scratch directory}/mx"
OUT="$BASE/results"
rm -rf "$BASE"
mkdir -p "$OUT"
: > "$OUT/summary.jsonl"
: > "$OUT/project_runs.jsonl"
: > "$OUT/probes.jsonl"
: > "$OUT/npm-install.log"

tsconfig() {
cat > "$1/tsconfig.json" <<'JSON'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true,
    "jsx": "react-jsx",
    "types": ["node"]
  },
  "include": ["*.ts", "*.tsx"]
}
JSON
}

# narrow tsconfig.one.json to a single file so one failing program cannot
# hide the exit code of the others
single_include() {
python3 - "$1" <<'PY'
import json, pathlib, sys
p = pathlib.Path('tsconfig.json')
d = json.loads(p.read_text())
d['include'] = [sys.argv[1]]
pathlib.Path('tsconfig.one.json').write_text(json.dumps(d, indent=2))
PY
}

for v in 5 6 7; do
  d="$BASE/v$v"
  mkdir -p "$d"
  cp "$HERE/programs/package.v$v.json" "$d/package.json" || exit 1
  cp "$HERE/programs/v$v"/* "$d/" || exit 1
  cd "$d" || exit 1

  echo "== v$v install"
  npm install --no-audit --no-fund --loglevel=error >> "$OUT/npm-install.log" 2>&1
  echo "{\"ai_major\": $v, \"step\": \"npm_install\", \"exit\": $?}" >> "$OUT/project_runs.jsonl"
  # retained record of what npm actually resolved, not just what was requested
  npm ls --json --depth=0 > "$OUT/npm-ls-v$v.json" 2> "$OUT/npm-ls-v$v.err"
  ./node_modules/.bin/tsc --version > "$OUT/tsc-version-v$v.txt"

  tsconfig "$d"
  ./node_modules/.bin/tsc --noEmit -p tsconfig.json > "$OUT/v$v.project.log" 2>&1
  echo "{\"ai_major\": $v, \"scope\": \"whole_project\", \"tsc_exit\": $?}" >> "$OUT/project_runs.jsonl"

  for f in stream.ts tool.ts chat.tsx legacy.tsx; do
    [ -f "$f" ] || continue
    single_include "$f"
    ./node_modules/.bin/tsc --noEmit -p tsconfig.one.json > "$OUT/v$v.$f.log" 2>&1
    code=$?
    echo "{\"ai_major\": $v, \"file\": \"$f\", \"tsc_exit\": $code, \"scope\": \"single_file\"}" >> "$OUT/summary.jsonl"
  done

  probe() {
    name="$1"; src="$2"
    printf '%s\n' "$src" > "p_$name.ts"
    single_include "p_$name.ts"
    ./node_modules/.bin/tsc --noEmit -p tsconfig.one.json > "$OUT/v$v.p_$name.log" 2>&1
    pcode=$?
    echo "{\"ai_major\": $v, \"probe\": \"$name\", \"tsc_exit\": $pcode, \"scope\": \"probe\"}" >> "$OUT/probes.jsonl"
  }

  probe stepcountis "import { stepCountIs } from 'ai';
export const condition = stepCountIs(3);"
  probe isstepcount "import { isStepCount } from 'ai';
export const condition = isStepCount(3);"
  probe system "import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';
export const result = streamText({ model: openai('gpt-4o-mini'), prompt: 'hi', system: 'terse' });"
  probe instructions "import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';
export const result = streamText({ model: openai('gpt-4o-mini'), prompt: 'hi', instructions: 'terse' });"
  probe maxsteps "import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';
export const result = streamText({ model: openai('gpt-4o-mini'), prompt: 'hi', maxSteps: 3 });"
  probe aiReact "import { useChat } from 'ai/react';
export const hook = useChat;"

  echo "== v$v done"
done
echo MATRIX_DONE
