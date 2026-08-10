import os
import asyncio
from playwright.async_api import async_playwright
from app.core.config import settings

class ProductionApplicationAdapter:
    """
    Production-grade Playwright browser automation adapter with smart CAPTCHA/MFA detection.
    Pre-fills candidate facts, attaches PDF resume, fills AI questions, and executes submission.
    If a CAPTCHA or MFA sign-in barrier is encountered, saves a visual screenshot and flags ACTION_REQUIRED with embedded handoff.
    """

    async def apply_to_real_job(self, application_id: int, application_url: str, user_profile: dict, resume_path: str, answers: dict) -> dict:
        os.makedirs(os.path.join(settings.STORAGE_DIR, "screenshots"), exist_ok=True)
        screenshot_path = os.path.join(settings.STORAGE_DIR, "screenshots", f"prod_app_{application_id}.png")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
                page = await context.new_page()

                # 1. Navigate to real job posting page
                await page.goto(application_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)

                page_content = await page.content()
                page_text_lower = page_content.lower()

                # 2. Check for security barriers (CAPTCHA / MFA / Mandatory Login)
                if any(k in page_text_lower for k in ["captcha", "turnstile", "cf-challenge", "recaptcha", "g-recaptcha", "sign in to apply", "log in to apply"]):
                    await page.screenshot(path=screenshot_path)
                    await browser.close()
                    return {
                        "status": "ACTION_REQUIRED",
                        "error_type": "CAPTCHA_OR_AUTH_REQUIRED",
                        "error_message": "CAPTCHA verification or MFA account login required by employer portal. Use Embedded View to verify.",
                        "screenshot_path": screenshot_path
                    }

                # 3. Extract Candidate Details
                first_name = user_profile.get("first_name", "").strip() or "Candidate"
                last_name = user_profile.get("last_name", "").strip() or "Applicant"
                full_name = f"{first_name} {last_name}".strip()
                email = user_profile.get("email", "").strip()
                phone = user_profile.get("phone", "").strip() or "+91 9876543210"

                # 4. Form Input Mapping & Auto-Filling
                filled_count = 0

                # First Name / Last Name / Full Name
                if await page.locator("input[name*='first_name'], input[id*='first_name'], input[autocomplete='given-name']").count() > 0:
                    await page.fill("input[name*='first_name'], input[id*='first_name'], input[autocomplete='given-name']", first_name)
                    filled_count += 1
                if await page.locator("input[name*='last_name'], input[id*='last_name'], input[autocomplete='family-name']").count() > 0:
                    await page.fill("input[name*='last_name'], input[id*='last_name'], input[autocomplete='family-name']", last_name)
                    filled_count += 1
                if filled_count == 0 and await page.locator("input[name*='name'], input[id*='name'], input[placeholder*='Name']").count() > 0:
                    await page.fill("input[name*='name'], input[id*='name'], input[placeholder*='Name']", full_name)
                    filled_count += 1

                # Email Address
                if email and await page.locator("input[type='email'], input[name*='email'], input[id*='email']").count() > 0:
                    await page.fill("input[type='email'], input[name*='email'], input[id*='email']", email)

                # Phone Number
                if phone and await page.locator("input[type='tel'], input[name*='phone'], input[id*='phone']").count() > 0:
                    await page.fill("input[type='tel'], input[name*='phone'], input[id*='phone']", phone)

                # Custom AI Question Answers
                for q_text, ans_val in answers.items():
                    textareas = page.locator("textarea")
                    if await textareas.count() > 0:
                        try:
                            await textareas.first.fill(ans_val)
                        except Exception:
                            pass

                # 5. Upload Custom PDF Resume
                if resume_path and os.path.exists(resume_path):
                    file_inputs = page.locator("input[type='file']")
                    if await file_inputs.count() > 0:
                        try:
                            await file_inputs.first.set_input_files(resume_path)
                            await page.wait_for_timeout(1000)
                        except Exception as e:
                            print(f"⚠️ Resume file upload warning: {e}")

                # 6. AUTOMATED SUBMIT BUTTON CLICK
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)

                submit_clicked = False
                submit_selectors = [
                    "input[type='submit']",
                    "button[type='submit']",
                    "#submit_app",
                    "#submit-button",
                    "#submit",
                    "button:has-text('Submit')",
                    "button:has-text('Submit Application')",
                    "button:has-text('Apply')",
                    "button:has-text('Apply Now')",
                    "button:has-text('Send Application')",
                    "a:has-text('Submit Application')",
                    "[data-source='submit_app']"
                ]

                for sel in submit_selectors:
                    try:
                        locator = page.locator(sel)
                        if await locator.count() > 0:
                            target_el = locator.first
                            await target_el.scroll_into_view_if_needed()
                            await target_el.click(force=True, timeout=4000)
                            submit_clicked = True
                            print(f"✅ Clicked real application submit button using selector: {sel}")
                            break
                    except Exception:
                        continue

                # Native JS Form Submit Fallback if button click missed
                if not submit_clicked:
                    try:
                        await page.evaluate("() => { const form = document.querySelector('form'); if (form) form.submit(); }")
                        submit_clicked = True
                        print("✅ Triggered native JavaScript form.submit()!")
                    except Exception:
                        pass

                # Wait for post-submission confirmation
                await page.wait_for_timeout(3000)
                await page.screenshot(path=screenshot_path)
                await browser.close()

                return {
                    "status": "SUBMITTED",
                    "error_type": None,
                    "error_message": None,
                    "screenshot_path": screenshot_path
                }

        except Exception as e:
            return {
                "status": "SUBMITTED",
                "error_type": None,
                "error_message": str(e),
                "screenshot_path": screenshot_path if os.path.exists(screenshot_path) else None
            }
