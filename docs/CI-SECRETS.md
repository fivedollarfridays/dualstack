# CI Secrets Guide

## E2E Test Credentials in GitHub Actions

The Playwright E2E tests require Clerk authentication credentials. These must
be stored as GitHub Actions secrets — never committed to the repository.

### Required Secrets

| Secret | Description |
|--------|-------------|
| `E2E_CLERK_USER_USERNAME` | Username/email of a dedicated Clerk test user |
| `E2E_CLERK_USER_PASSWORD` | Password for the Clerk test user |

### Setup Steps

1. **Create a test user** in your Clerk dashboard with password authentication
   enabled. Use a dedicated test account, not a real user.

2. **Add secrets to GitHub:**

   ```bash
   gh secret set E2E_CLERK_USER_USERNAME --body "test@example.com"
   gh secret set E2E_CLERK_USER_PASSWORD --body "your-test-password"
   ```

   Or via the GitHub UI: Settings > Secrets and variables > Actions > New
   repository secret.

3. **Reference in workflow:**

   ```yaml
   env:
     E2E_CLERK_USER_USERNAME: ${{ secrets.E2E_CLERK_USER_USERNAME }}
     E2E_CLERK_USER_PASSWORD: ${{ secrets.E2E_CLERK_USER_PASSWORD }}
   ```

### Other Secrets for CI

| Secret | Required For | Notes |
|--------|-------------|-------|
| `CLERK_SECRET_KEY` | Clerk API calls (if backend tests need it) | Not currently used in backend tests |
| `STRIPE_SECRET_KEY` | Billing integration tests | Use Stripe test mode key |
| `STRIPE_WEBHOOK_SECRET` | Webhook signature verification | Use `whsec_test...` from Stripe CLI |

### Best Practices

- Use separate Clerk/Stripe test environments for CI
- Rotate test credentials periodically
- Never log secret values in CI output
- Use environment-scoped secrets if deploying to multiple environments
