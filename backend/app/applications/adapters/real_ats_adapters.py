import os
import asyncio
from playwright.async_api import async_playwright
from app.core.config import settings

class ProductionApplicationAdapter:
    """
    Production-grade Playwright browser automation adapter for real application portals (Greenhouse, Lever, SmartRecruiters, Ashby).
    Automates form filling, PDF resume upload, custom AI question answering, submits the application form, and captures visual proof.
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
                await page.goto(application_url, wait_until="domcontentloaded", timeout=25000)
                await page.wait_for_timeout(2000)

                page_content = await page.content()
                page_text_lower = page_content.lower()

                # Security / CAPTCHA / Auth Check Handoff
                if any(k in page_text_lower for k in ["captcha", "turnstile", "cf-challenge", "recaptcha", "sign in to apply", "log in to apply"]):
                    await page.screenshot(path=screenshot_path)
                    await browser.close()
                    return {
                        "status": "ACTION_REQUIRED",
                        "error_type": "CAPTCHA_OR_AUTH_REQUIRED",
                        "error_message": "Employer page requires manual CAPTCHA verification or account login. Click link to complete application manually.",
                        "screenshot_path": screenshot_path
                    }

                # 2. Extract Candidate Details
                first_name = user_profile.get("first_name", "").strip() or "Candidate"
                last_name = user_profile.get("last_name", "").strip() or "Applicant"
                full_name = f"{first_name} {last_name}".strip()
                email = user_profile.get("email", "").strip()
                phone = user_profile.get("phone", "").strip() or "+91 9876543210"

                # 3. Form Input Mapping & Auto-Filling
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

                # 4. Upload Custom PDF Resume
                if resume_path and os.path.exists(resume_path):
                    file_inputs = page.locator("input[type='file']")
                    if await file_inputs.count() > 0:
                        try:
                            await file_inputs.first.set_input_files(resume_path)
                            await page.wait_for_timeout(1000)
                        except Exception as e:
                            print(f"⚠️ Resume file upload warning: {e}")

                # 5. EXECUTE REAL SUBMIT BUTTON CLICK
                submit_clicked = False
                submit_selectors = [
                    "input[type='submit']",
                    "button[type='submit']",
                    "button:has-text('Submit')",
                    "button:has-text('Submit Application')",
                    "button:has-text('Apply')",
                    "#submit_app",
                    "#submit-button"
                ]

                for sel in submit_selectors:
                    try:
                        locator = page.locator(sel)
                        if await locator.count() > 0 and await locator.first.is_visible():
                            await locator.first.click()
                            submit_clicked = True
                            print(f"✅ Clicked real application submit button using selector: {sel}")
                            break
                    except Exception as e:
                        continue

                # Wait for post-submission page response
                if submit_clicked:
                    await page.wait_for_timeout(4000)

                # Capture visual proof screenshot of submission result
                await page.screenshot(path=screenshot_path)
                await browser.close()

                return {
                    "status": "SUBMITTED" if submit_clicked else "ACTION_REQUIRED",
                    "error_type": None if submit_clicked else "MANUAL_SUBMIT_REQUIRED",
                    "error_message": None if submit_clicked else "Form inputs filled & resume attached. Please click link to complete final submission.",
                    "screenshot_path": screenshot_path
                }

        except Exception as e:
            return {
                "status": "FAILED",
                "error_type": "REAL_PORTAL_AUTOMATION_ERROR",
                "error_message": str(e),
                "screenshot_path": screenshot_path if os.path.exists(screenshot_path) else None
            }
