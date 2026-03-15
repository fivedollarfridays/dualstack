# DualStack Credibility Badges

> Audit date: 2026-03-15

## Badge Row

![Security](https://img.shields.io/badge/security-0_vulnerabilities-brightgreen) ![Tests](https://img.shields.io/badge/tests-1218_passing-brightgreen) ![Coverage](https://img.shields.io/badge/coverage-91%25-yellow) ![Bundle](https://img.shields.io/badge/bundle-102kB_shared-brightgreen) ![Deploy](https://img.shields.io/badge/deploy-84s-brightgreen) ![Deps](https://img.shields.io/badge/deps-9_major_updates-orange)

## Audit Summary

| Category | Result | Details |
|----------|--------|---------|
| Security | PASS | 0 JS vulnerabilities, 0 Python vulnerabilities |
| Tests | 1218/1225 passing | Backend: 775/782 (99.1%), Frontend: 443/443 (100%) |
| Coverage | ~91% | Frontend statements: 90.96%, branches: 88.77% |
| Bundle Size | 102 kB shared | Largest page: 143 kB (auth pages), typical: 112-125 kB |
| Deploy Time | 84 seconds | Clean pnpm install + next build (JS only) |
| Dependencies | 9 major updates | React 19, Next 16, Clerk 7, Tailwind 4, ESLint 10 available |

## Notes

- **Backend test failures (7)**: All in `tests/files/test_file_routes.py` -- file upload routes return 404. The file router appears to not be registered in `app/main.py`. Service-level tests pass.
- **Frontend coverage**: Below 99% thresholds due to untested `use-file-upload.ts` hook and partial coverage on upload/websocket components.
- **Build lint error**: `next build` (with lint) fails on `@typescript-eslint/no-explicit-any` in a test file (`use-websocket.test.ts:42`). Production code compiles cleanly.
- **Deploy time**: Python venv setup not included; would add ~30-60s.

## Raw Data

See individual files in this directory:
- `security-audit.txt` -- Full security scan output
- `coverage-report.txt` -- Test counts and coverage breakdown
- `build-output.txt` -- Next.js build route sizes
- `dependency-check.txt` -- Outdated dependency list
- `deploy-time.txt` -- Timed deploy test results
