import os
import json
import smtplib
import urllib.request
import urllib.error
from email.message import EmailMessage
from typing import Tuple, Optional

# Load .env file automatically if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Built-in lightweight .env loader fallback
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as _f:
                for _line in _f:
                    _line = _line.strip()
                    if _line and not _line.startswith("#") and "=" in _line:
                        _k, _v = _line.split("=", 1)
                        _k, _v = _k.strip(), _v.strip().strip("'\"")
                        if _k and _k not in os.environ:
                            os.environ[_k] = _v
        except Exception:
            pass

# In-memory store for testing and local development fallback
_last_sent_codes = {}


def get_last_dev_code(email: str) -> Optional[str]:
    """Retrieve the most recently dispatched reset code for an email (for testing/dev)."""
    return _last_sent_codes.get(email.lower().strip())


def is_email_configured() -> bool:
    """Returns True if any valid email dispatch method (Resend, Gmail, or custom SMTP) is configured."""
    if os.environ.get("RESEND_API_KEY"):
        return True
    if os.environ.get("GMAIL_USER") and os.environ.get("GMAIL_APP_PASSWORD"):
        return True
    if os.environ.get("SMTP_HOST"):
        return True
    return False


def _send_via_resend(
    api_key: str,
    from_email: str,
    to_email: str,
    subject: str,
    text_content: str,
    html_content: str
) -> Tuple[bool, str]:
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "User-Agent": "SimpleNotes/1.0"
    }
    payload = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
        "text": text_content,
        "html": html_content
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return True, "Email sent via Resend API successfully"
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="ignore")
        try:
            err_json = json.loads(err_msg)
            msg = err_json.get("message", err_msg)
        except Exception:
            msg = err_msg

        if e.code in (403, 422) and ("testing" in msg.lower() or "domain" in msg.lower() or "only send" in msg.lower() or "invalid" in msg.lower()):
            msg += " (Tip: With onboarding@resend.dev, Resend sandbox only delivers to the email address registered with your Resend account. To send to any user, verify a domain at resend.com/domains)."

        return False, f"Resend API error ({e.code}): {msg}"
    except Exception as e:
        return False, f"Resend connection error: {str(e)}"


def _send_via_smtp(
    host: str,
    port: int,
    user: Optional[str],
    password: Optional[str],
    from_email: str,
    to_email: str,
    subject: str,
    text_content: str,
    html_content: str,
    use_tls: bool,
    use_ssl: bool
) -> Tuple[bool, str]:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(text_content)
    msg.add_alternative(html_content, subtype="html")

    try:
        if use_ssl or port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=15) as server:
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                if use_tls:
                    server.starttls()
                if user and password:
                    server.login(user, password)
                server.send_message(msg)
        return True, "Email sent via SMTP successfully"
    except smtplib.SMTPAuthenticationError as e:
        err_detail = e.smtp_error.decode("utf-8", errors="ignore") if hasattr(e, "smtp_error") and isinstance(e.smtp_error, bytes) else str(e)
        hint = ""
        if "gmail" in host.lower():
            hint = " Note: Gmail requires a 16-character App Password (google.com/account/security/apppasswords), not your regular password."
        return False, f"SMTP Authentication failed: {err_detail}.{hint}"
    except Exception as e:
        return False, f"SMTP connection error ({host}:{port}): {str(e)}"


def send_password_reset_email(to_email: str, code: str, allow_dev_fallback: bool = True, skip_external: bool = False) -> Tuple[bool, str, str]:
    """
    Sends a 6-digit password reset verification code to the recipient email address.
    Supports:
      1. Resend API (HTTP POST to https://api.resend.com/emails) via RESEND_API_KEY
      2. Gmail shortcut via GMAIL_USER and GMAIL_APP_PASSWORD
      3. Custom SMTP server via SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM
      4. Offline dev fallback (logs to console and dev banner) when testing or unconfigured

    Returns:
      (success: bool, status_message: str, method: str)
      where method is one of 'resend', 'smtp', 'dev', 'unconfigured', or 'error'.
    """
    clean_email = to_email.lower().strip()
    _last_sent_codes[clean_email] = code

    if skip_external:
        return True, "Verification code generated in local development mode", "dev"

    subject = f"SimpleNotes: Your Password Reset Code [{code}]"

    text_body = f"""Hello,

You requested a password reset for your SimpleNotes account.

Your 6-digit verification code is:
----------------------------------------
                 {code}
----------------------------------------

This code will expire in 15 minutes.
If you did not request this reset, you can safely ignore this email.

Best regards,
The SimpleNotes Team
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SimpleNotes Password Reset</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #1e293b; padding: 24px; margin: 0;">
  <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 520px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
    <tr>
      <td style="padding: 28px 32px; background: #0f172a; text-align: center;">
        <span style="font-size: 28px;">📒</span>
        <h1 style="color: #ffffff; font-size: 20px; margin: 8px 0 0 0; font-weight: 700;">SimpleNotes</h1>
      </td>
    </tr>
    <tr>
      <td style="padding: 32px;">
        <h2 style="font-size: 18px; margin-top: 0; color: #0f172a;">Password Reset Request</h2>
        <p style="font-size: 14px; line-height: 1.5; color: #475569;">
          We received a request to reset your password. Use the verification code below to complete your password reset:
        </p>
        <div style="text-align: center; margin: 28px 0;">
          <div style="display: inline-block; background-color: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 8px; padding: 14px 28px; font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #2563eb; font-family: monospace;">
            {code}
          </div>
        </div>
        <p style="font-size: 13px; color: #64748b; margin-bottom: 4px;">
          ⏱️ This verification code expires in <strong>15 minutes</strong>.
        </p>
        <p style="font-size: 13px; color: #64748b; margin-top: 4px;">
          If you did not request a password reset, you can safely ignore this email.
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding: 16px 32px; background-color: #f8fafc; border-top: 1px solid #e2e8f0; text-align: center; font-size: 12px; color: #94a3b8;">
        SimpleNotes &bull; Privacy-first Personal Note Taking
      </td>
    </tr>
  </table>
</body>
</html>
"""

    # 1. Option A: Resend API (HTTP REST - recommended for Vercel)
    resend_key = os.environ.get("RESEND_API_KEY")
    if resend_key:
        resend_from = os.environ.get("RESEND_FROM") or os.environ.get("EMAIL_FROM") or "SimpleNotes <onboarding@resend.dev>"
        ok, msg = _send_via_resend(resend_key, resend_from, clean_email, subject, text_body, html_body)
        if ok:
            print(f"📧 [Email Service] Successfully sent reset code to {clean_email} via Resend API.")
            return True, "Verification code sent to your email address", "resend"
        else:
            print(f"⚠️ [Email Service] Resend dispatch failed: {msg}")
            return False, f"Failed to send email via Resend: {msg}", "error"

    # 2. Option B: Gmail shortcut
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD")
    if gmail_user and gmail_pass:
        gmail_pass_clean = gmail_pass.replace(" ", "")
        from_addr = os.environ.get("SMTP_FROM") or f"SimpleNotes <{gmail_user.strip()}>"
        
        # Try port 465 (SSL - works across all ISPs and cloud providers)
        ok, msg = _send_via_smtp(
            host="smtp.gmail.com",
            port=465,
            user=gmail_user.strip(),
            password=gmail_pass_clean,
            from_email=from_addr,
            to_email=clean_email,
            subject=subject,
            text_content=text_body,
            html_content=html_body,
            use_tls=False,
            use_ssl=True
        )
        if not ok:
            # Fallback to port 587 (STARTTLS)
            ok, msg = _send_via_smtp(
                host="smtp.gmail.com",
                port=587,
                user=gmail_user.strip(),
                password=gmail_pass_clean,
                from_email=from_addr,
                to_email=clean_email,
                subject=subject,
                text_content=text_body,
                html_content=html_body,
                use_tls=True,
                use_ssl=False
            )

        if ok:
            print(f"📧 [Email Service] Successfully sent reset code to {clean_email} via Gmail SMTP.")
            return True, "Verification code sent to your email address", "smtp"
        else:
            print(f"⚠️ [Email Service] Gmail SMTP dispatch failed: {msg}")
            return False, msg, "error"

    # 3. Option C: Generic SMTP
    smtp_host = os.environ.get("SMTP_HOST")
    if smtp_host:
        smtp_port = int(os.environ.get("SMTP_PORT", 587))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")
        smtp_from = os.environ.get("SMTP_FROM", "SimpleNotes <noreply@simplenotes.local>")
        smtp_tls = os.environ.get("SMTP_TLS", "true").lower() in ("true", "1", "yes")
        smtp_ssl = os.environ.get("SMTP_SSL", "false").lower() in ("true", "1", "yes") or smtp_port == 465

        ok, msg = _send_via_smtp(
            host=smtp_host.strip(),
            port=smtp_port,
            user=smtp_user.strip() if smtp_user else None,
            password=smtp_pass if smtp_pass else None,
            from_email=smtp_from,
            to_email=clean_email,
            subject=subject,
            text_content=text_body,
            html_content=html_body,
            use_tls=smtp_tls,
            use_ssl=smtp_ssl
        )
        if ok:
            print(f"📧 [Email Service] Successfully sent reset code to {clean_email} via SMTP ({smtp_host}).")
            return True, "Verification code sent to your email address", "smtp"
        else:
            print(f"⚠️ [Email Service] SMTP dispatch failed: {msg}")
            return False, msg, "error"

    # 4. Fallback when no provider is configured
    if allow_dev_fallback:
        print(f"\n========================================================")
        print(f"📧 [SimpleNotes Mailer] (No live SMTP/Resend configured)")
        print(f"   Password Reset Code for {clean_email}: {code}")
        print(f"   To receive real emails in your inbox, set GMAIL_USER & GMAIL_APP_PASSWORD,")
        print(f"   or RESEND_API_KEY, or SMTP_HOST in .env or Vercel Environment Variables.")
        print(f"========================================================\n")
        return True, "Verification code generated in local development mode", "dev"

    return False, "Email service not configured. Please set SMTP credentials or RESEND_API_KEY in your environment.", "unconfigured"
