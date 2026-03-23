# GitHub Secrets Setup Guide

## Overview

This guide explains how to configure GitHub Secrets required for the CI pipeline to run successfully.

## Required Secrets

### GEMINI_API_KEY

The Gemini API key is required for AI-powered fraud explanations and investigation queries.

#### How to Add the Secret

1. **Navigate to Repository Settings**
   - Go to your GitHub repository
   - Click on "Settings" tab
   - In the left sidebar, click "Secrets and variables" → "Actions"

2. **Create New Secret**
   - Click "New repository secret" button
   - Name: `GEMINI_API_KEY`
   - Value: Your Google Gemini API key
   - Click "Add secret"

3. **Verify Secret**
   - The secret should now appear in the list (value will be hidden)
   - The CI pipeline will automatically use this secret

#### Getting a Gemini API Key

If you don't have a Gemini API key:

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Add it to GitHub Secrets as described above

**Note**: The current API key in the codebase is for demonstration purposes. For production use, generate your own key.

## Optional Secrets

### CODECOV_TOKEN (Optional)

If you want to use Codecov for coverage tracking:

1. Sign up at [codecov.io](https://codecov.io)
2. Add your repository
3. Copy the upload token
4. Add as secret: `CODECOV_TOKEN`

## Testing Without Secrets

The CI pipeline is designed to work even without the Gemini API key:

- Tests will use mocked responses when `TEST_MODE=true`
- Core functionality tests will still run
- Some AI-related tests may be skipped

## Security Best Practices

1. **Never commit secrets to the repository**
   - Use `.gitignore` to exclude `.env` files
   - Use GitHub Secrets for CI/CD
   - Use environment variables for local development

2. **Rotate keys regularly**
   - Update API keys periodically
   - Revoke old keys after rotation

3. **Limit secret access**
   - Only add secrets that are necessary
   - Use repository secrets (not organization secrets) unless needed

4. **Monitor usage**
   - Check API usage in Google Cloud Console
   - Set up usage alerts
   - Monitor for unauthorized access

## Local Development

For local development, use a `.env` file:

```bash
# .env
GEMINI_API_KEY=your_api_key_here
TEST_MODE=false
```

**Important**: The `.env` file is already in `.gitignore` and will not be committed.

## Troubleshooting

### Secret Not Working

If the CI pipeline can't access the secret:

1. Verify the secret name matches exactly: `GEMINI_API_KEY`
2. Check that the secret is set at the repository level (not organization)
3. Ensure the workflow has permission to access secrets
4. Try re-creating the secret

### API Key Invalid

If you get authentication errors:

1. Verify the API key is correct
2. Check if the key has been revoked
3. Ensure the key has the necessary permissions
4. Generate a new key if needed

## Verification

To verify secrets are working:

1. Push a commit to trigger the CI pipeline
2. Go to Actions tab
3. Click on the running workflow
4. Check the "Run property-based tests" step
5. Look for successful API connections (or mocked responses if TEST_MODE=true)

## Support

For issues with GitHub Secrets:
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Google AI Studio Help](https://ai.google.dev/tutorials/setup)
