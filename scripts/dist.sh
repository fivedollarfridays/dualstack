#!/usr/bin/env bash
set -euo pipefail

# Dist packaging script for DualStack marketplace delivery
# Usage: ./scripts/dist.sh [version]
# If no version is provided, defaults to today's date (YYYYMMDD).

VERSION="${1:-$(date +%Y%m%d)}"
DIST_DIR="dist"
OUTPUT_FILE="${DIST_DIR}/dualstack-${VERSION}.zip"

# Navigate to project root (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# Create output directory
mkdir -p "${DIST_DIR}"

echo "==> Packaging DualStack v${VERSION}..."

zip -r "${OUTPUT_FILE}" . \
    -x ".git/*" \
    -x ".gitattributes" \
    -x ".gitmodules" \
    -x ".paircoder/*" \
    -x ".paircoder-audit.jsonl" \
    -x ".claude/*" \
    -x "CLAUDE.md" \
    -x "AGENTS.md" \
    -x "node_modules/*" \
    -x "*/node_modules/*" \
    -x ".venv/*" \
    -x "venv/*" \
    -x "__pycache__/*" \
    -x "*/__pycache__/*" \
    -x ".env" \
    -x ".env.local" \
    -x ".env.production" \
    -x "*/.env" \
    -x "*/.env.local" \
    -x "*/.env.production" \
    -x "*.db" \
    -x "*.db-journal" \
    -x "*.sqlite" \
    -x "monitoring/grafana/data/*" \
    -x "monitoring/prometheus/data/*" \
    -x "dist/*" \
    -x "audit-report.md" \
    -x "product-line-plan.md" \
    -x "sprint-estimates.md" \
    -x "dualstack-sellable.md" \
    -x "htmlcov/*" \
    -x ".coverage" \
    -x "coverage/*" \
    -x ".next/*" \
    -x "test-results/*" \
    -x "playwright-report/*" \
    -x "*.pyc" \
    -x "*.pyo"

FILE_SIZE=$(du -h "${OUTPUT_FILE}" | cut -f1)
echo "==> Created ${OUTPUT_FILE} (${FILE_SIZE})"
