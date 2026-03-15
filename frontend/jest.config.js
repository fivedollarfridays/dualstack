/** @type {import('jest').Config} */
const config = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/.next/', '<rootDir>/e2e/'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', {
      tsconfig: {
        jsx: 'react-jsx',
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
        moduleResolution: 'node',
        module: 'commonjs',
        strict: true,
      },
    }],
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.test.{ts,tsx}',
    '!src/app/layout.tsx',
    '!src/app/globals.css',
    // ORM schemas - callbacks execute at database runtime, not unit-testable
    '!src/db/schema/**/*',
    // Database scripts - migration and test utilities
    '!src/db/migrate.ts',
    // Type-only files - no executable logic
    '!src/types/**/*',
    // Middleware - tested via integration
    '!src/middleware.ts',
    // Barrel exports - re-export only, no logic
    '!src/**/index.ts',
    // API client wrappers - thin fetch calls, tested via integration/E2E
    '!src/lib/api/**/*',
    // Page-level components - orchestration tested via E2E
    '!src/app/**/page.tsx',
    // Dashboard layout - tested via E2E
    '!src/app/(dashboard)/layout.tsx',
  ],
  coverageThreshold: {
    global: {
      statements: 99,
      branches: 99,
      functions: 99,
      lines: 99,
    },
    // Per-file overrides for files with SSR-only or jsdom-unreachable branches:
    // - auth-config.ts: `typeof window` SSR check, `getDevToken` null branch
    // - use-websocket.ts: defensive already-open guard, closure-captured retry branches
    // - file-upload.tsx: optional-chaining on ref that is always non-null in jsdom
    './src/lib/auth-config.ts': { branches: 80 },
    './src/hooks/use-websocket.ts': { branches: 80 },
    './src/hooks/use-onboarding.ts': { branches: 75 },
    './src/components/upload/file-upload.tsx': { branches: 85 },
  },
};

module.exports = config;
