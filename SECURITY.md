# 🔒 Security Policy

## Security Features

This application implements multiple layers of security to protect your data when deployed publicly:

### 1. **Credential Protection**
- ✅ Service account credentials stored in Streamlit Secrets (encrypted)
- ✅ `.gitignore` prevents accidental credential commits
- ✅ No sensitive data in source code
- ✅ Credentials never exposed in client-side code

### 2. **Authentication & Authorization**
- ✅ **Password Protection:** Admin dashboard requires password
- ✅ **Session Timeout:** Auto-logout after 1 hour of inactivity
- ✅ **Failed Login Protection:**
  - Max 5 failed login attempts
  - 15-minute lockout after 5 failures
  - Prevents brute-force attacks

### 3. **Input Validation & Sanitization**
- ✅ **HTML/Script Tag Removal:** Prevents XSS attacks
- ✅ **URL Validation:** LinkedIn links validated before storage
- ✅ **Length Limits:**
  - Company Name: 200 characters
  - Notes: 1000 characters
- ✅ **Special Character Filtering:** Removes injection attack vectors

### 4. **Rate Limiting**
- ✅ **Form Submissions:** Max 10 submissions per hour per user
- ✅ **Automatic Reset:** Rate limits reset after 1 hour
- ✅ **Prevents Spam:** Protects against automated bots

### 5. **Google Sheets Security**
- ✅ **Service Account:** Limited permissions (Sheets API only)
- ✅ **Specific Sheet Access:** Only accesses designated spreadsheet
- ✅ **No Drive API:** Reduced attack surface

## Deployment Checklist

Before deploying to production, ensure:

### Required Steps:

1. **Change Admin Password**
   ```toml
   # In Streamlit Cloud Secrets
   ADMIN_PASSWORD = "your_strong_password_here"
   ```
   - Use a strong password (12+ characters)
   - Mix uppercase, lowercase, numbers, symbols
   - Never use default password in production

2. **Add Google Credentials to Secrets**
   ```toml
   [gsheet_credentials]
   type = "service_account"
   project_id = "your-project"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   # ... rest of credentials
   ```

3. **Verify .gitignore**
   - Ensure `creds.json` is never committed
   - Check no secrets in git history

4. **Share Google Sheet Properly**
   - Share only with service account email
   - Grant only Editor permissions (not Owner)
   - Don't share publicly

### Optional (Recommended):

5. **Enable HTTPS** (Streamlit Cloud does this automatically)

6. **Monitor Access Logs**
   - Check Streamlit Cloud analytics
   - Review Google Sheets activity log

7. **Regular Password Rotation**
   - Change admin password every 90 days
   - Rotate service account keys annually

## Security Best Practices

### For Administrators:

- ✅ Always logout when done
- ✅ Don't share admin password
- ✅ Use private/incognito browser for admin access
- ✅ Don't access admin panel on public WiFi
- ✅ Enable 2FA on your Google account

### For Developers:

- ✅ Never commit `creds.json` or secrets
- ✅ Use environment variables for sensitive config
- ✅ Review code before deployment
- ✅ Keep dependencies updated
- ✅ Test security features before deploying

## Vulnerability Reporting

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email: [your-email@domain.com]
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours.

## Security Limitations

This application has the following limitations:

⚠️ **User Authentication:** No individual user accounts (single admin password)
⚠️ **IP Blocking:** No IP-based blocking (relies on session-based rate limiting)
⚠️ **Audit Logging:** Limited audit trail (relies on Google Sheets timestamp)
⚠️ **Data Encryption:** Data encrypted in transit (HTTPS) but not at rest in Google Sheets

For enterprise deployments requiring higher security:
- Consider implementing proper user authentication (OAuth, SAML)
- Add IP whitelisting
- Implement comprehensive audit logging
- Use encrypted database instead of Google Sheets

## Compliance

This application:
- ✅ Uses HTTPS for all connections
- ✅ Sanitizes user input
- ✅ Implements rate limiting
- ✅ Protects credentials
- ❌ Not GDPR-compliant by default (no data deletion mechanism)
- ❌ Not HIPAA-compliant (don't store medical data)

## Updates & Patches

Security updates will be released as needed:
- Critical: Immediate patch
- High: Within 7 days
- Medium: Within 30 days
- Low: Next regular release

## License

This security policy is part of the overall project license.

---

Last Updated: 2025-12-08
Security Contact: [Your Contact Info]
