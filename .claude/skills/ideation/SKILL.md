---
name: ideation
description: Transforms a rough idea into a codebase-aware structured brief for /draft-backlog. Runs inventory discovery, integration mapping, constraint identification, and impact analysis against the actual codebase so the backlog is built from ground truth, not memory.
---

# Ideating

## When to Use

When the user has a rough idea and wants to turn it into a sprint. Sits between "I want to build X" and `/draft-backlog`. The user invokes this with `/ideating <idea>` or by describing what they want to build.

The output is a structured brief that becomes the input to `/draft-backlog`. Better input = fewer review rounds.

## Input

A rough idea. Can be a sentence, a paragraph, a bullet list, or a file path to notes. Examples:
- "add OCR receipt scanning"
- "rip out the old auth middleware and replace with JWT"
- "sprint to harden the API against the OWASP top 10"
- A path to a design doc or feature request

## Steps

Run steps 1-4 in parallel (independent reads), then synthesize sequentially.

### 1. Understand the Codebase Surface

Discover what exists. Build from the filesystem, not from memory.

```bash
# Directory structure (top 3 levels)
find . -type d -maxdepth 3 -not -path '*__pycache__*' -not -path '*/node_modules/*' -not -path '*/\.*' -not -path '*/.git/*' | sort

# File count by directory
find . -type f \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.svelte' \) -not -path '*__pycache__*' -not -path '*/node_modules/*' | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -20

# Oversized files (complexity hotspots)
find . \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' \) -not -path '*__pycache__*' -not -path '*/node_modules/*' -not -name 'test_*' | while read f; do
    lines=$(wc -l < "$f"); [ "$lines" -gt 200 ] && echo "$lines $f"
done | sort -rn

# Unfinished work in the path of the new feature
grep -rn 'NotImplementedError\|# TODO\|# FIXME\|# HACK\|pass$' . --include='*.py' --include='*.ts' --include='*.js' | grep -v test | grep -v __pycache__ | grep -v node_modules
```

### 2. Map Integration Points

Find the seams where the new feature will connect to existing code.

```bash
# API routes — what endpoints exist
grep -rn '@router\.\|@app\.\|APIRouter\|app\.get\|app\.post\|express\.\|fastify\.' . --include='*.py' --include='*.ts' --include='*.js' | grep -v test | grep -v __pycache__ | grep -v node_modules

# Event/message channels
grep -rn 'publish\|subscribe\|emit\|on_event\|bus\.\|addEventListener\|dispatch' . --include='*.py' --include='*.ts' --include='*.js' | grep -v test | grep -v __pycache__ | grep -v node_modules | head -30

# Database/storage layer
grep -rn 'db\.\|collection\|Collection\|get_collection\|IndexedDB\|localStorage\|openDB\|createStore' . --include='*.py' --include='*.ts' --include='*.js' | grep -v test | grep -v __pycache__ | grep -v node_modules | head -30

# Background/async work
grep -rn 'background\|scheduled\|cron\|periodic\|supervisor\|asyncio\.create_task\|setInterval\|Worker' . --include='*.py' --include='*.ts' --include='*.js' | grep -v test | grep -v __pycache__ | grep -v node_modules

# Config and environment
find . -name '*.env*' -o -name 'config.*' -o -name 'settings.*' | grep -v node_modules | grep -v __pycache__
```

### 3. Identify Constraints

Find things that will shape or limit the implementation.

```bash
# Architecture limits (if bpsai-pair is available)
bpsai-pair arch check . 2>/dev/null || echo "arch check not available"

# Test coverage — what's tested, what's not
find . \( -name 'test_*' -o -name '*.test.*' -o -name '*.spec.*' \) -not -path '*/node_modules/*' | wc -l
find . \( -name '*.py' -o -name '*.ts' -o -name '*.js' \) -not -name 'test_*' -not -name '*.test.*' -not -name '*.spec.*' -not -path '*/node_modules/*' -not -path '*__pycache__*' | wc -l

# Dependencies — what's available
cat pyproject.toml 2>/dev/null | grep -A 50 '\[project\]' | grep -A 50 'dependencies' | head -30
cat package.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'  {k}: {v}') for k,v in {**d.get('dependencies',{}), **d.get('devDependencies',{})}.items()]" 2>/dev/null

# Broad exception masking in the feature's path
grep -rn 'except Exception\|except:' . --include='*.py' | grep -v test | grep -v __pycache__ | wc -l
```

### 4. Check Prior Sprint Context

Understand what's already been built and what's in flight.

```bash
# Recent sprint history
cat .paircoder/context/state.md 2>/dev/null | head -80

# Existing plans
ls .paircoder/plans/ 2>/dev/null
ls plans/backlogs/ 2>/dev/null

# Recent git activity in areas the feature will touch
git log --oneline -20
```

### 5. Synthesize the Brief

Using the discovery from steps 1-4, produce a structured brief. This is the primary output — it becomes the input to `/draft-backlog`.

**Format:**

```markdown
# Feature Brief: [Title]

## Idea
[One paragraph restating the user's idea with clarity]

## Codebase Context
- **Stack:** [language, framework, key deps]
- **Size:** [file count, test count, LOC estimate]
- **Current sprint:** [what's active, what just shipped]

## What Exists That This Touches
[List existing modules, routes, DB tables, UI components that the new feature
will integrate with, import from, or modify. File paths and line numbers.]

## What Needs to Be Built
[List the new modules, routes, endpoints, UI components. Group by layer
(data model → logic → API → UI) or by phase if the feature has natural stages.]

## Integration Points
[For each new component, specify how it wires into the existing system:
- What it imports from
- What events it publishes/subscribes to
- What routes it registers
- What DB collections/tables it uses
- What existing UI it appears in]

## Constraints & Risks
- **Oversized files in the path:** [list any >200 line files that will need modification]
- **Unfinished work:** [TODOs, FIXMEs, stubs in the feature's path]
- **Missing tests:** [areas with no test coverage that the feature depends on]
- **Dependencies needed:** [new packages/libraries required]
- **Tech debt to address:** [broad excepts, dead code, naming inconsistencies]

## Impact on Existing Code
[What existing code will break or need updating:
- Import paths that change
- Tests that need updating
- Config/env vars that need adding
- Files that will exceed size limits after modification]

## Suggested Phases
[Natural grouping of work into phases for the backlog:
- Phase 1: data model + core logic
- Phase 2: API/routes + integration
- Phase 3: UI + polish
Suggest parallel vs sequential based on dependencies.]

## Out of Scope
[Explicitly state what this sprint does NOT include, to prevent scope creep
during engage. This is as important as what's in scope.]
```

### 6. Deliver

End the response with:

```
Brief ready. To generate the backlog:

  /draft-backlog <paste or reference the brief above>
```

## Decision Rules

- **If the idea is vague** ("make it faster", "improve the API"): ask one clarifying question before running discovery. Don't guess.
- **If the codebase is empty/new** (< 5 source files): skip steps 1-3, the brief is mostly "What Needs to Be Built" with minimal integration points.
- **If the idea touches > 50% of the codebase**: flag this as a refactor, not a feature. Suggest splitting into multiple sprints.
- **If unfinished work (TODOs/stubs) blocks the new feature**: include cleanup tasks in the brief's suggested phases.
- **If an existing module will exceed 400 lines after modification**: include a split task in the brief.

## What This Skill Does NOT Do

- Write the backlog (that's `/draft-backlog`)
- Validate the backlog (that's `/prepare-to-engage`)
- Review code (that's `/reviewing-code`)
- Analyze review output (that's `/analyzing-review-report`)

This skill's only job is to produce a brief that makes `/draft-backlog` produce a better backlog on the first pass.
