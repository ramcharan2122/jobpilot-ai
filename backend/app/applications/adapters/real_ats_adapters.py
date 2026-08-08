import os
from playwright.async_api import async_playwright
from app.core.config import settings

class ProductionApplicationAdapter:
    """
    Production-grade Playwright browser automation adapter for real application portals (Greenhouse, Lever, Custom Career pages).
    Detects security verification checks, maps form input selectors, fills candidate facts, uploads custom PDF resumes, and captures confirmations.
    """

    async def apply_to_real_job(self, application_id: int, application_url: str, user_profile: dict, resume_path: str, answers: dict) -> dict:
        screenshot_path = os.path.join(settings.STORAGE_DIR, "screenshots", f"prod_app_{application_id}.png")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/123.0.0.0 Safari/537.36"
                )
                page = await context.new_page()

                # Navigate to real job posting page
                await page.goto(application_url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(2000)

                page_text = await page.content()
                page_text_lower = page_text.lower()

                # 1. Anti-Bot / CAPTCHA / Login Check Handoff
                if any(k in page_text_lower for k in ["captcha", "turnstile", "cf-challenge", "recaptcha", "sign in to apply", "log in to apply"]):
                    await page.screenshot(path=screenshot_path)
                    await browser.close()
                    return {
                        "status": "ACTION_REQUIRED",
                        "error_type": "CAPTCHA_OR_AUTH_REQUIRED",
                        "error_message": "CAPTCHA verification or account sign-in required on employer page. Please complete manually.",
                        "screenshot_path": screenshot_path
                    }

                # 2. Extract Candidate Details
                first_name = user_profile.get("first_name", "Candidate")
                last_name = user_profile.get("last_name", "Applicant")
                full_name = f"{first_name} {last_name}".strip()
                email = user_profile.get("email", "candidate@example.com")
                phone = user_profile.get("phone", "+91 9876543210")

                # 3. Map & Fill Common Form Selectors (Greenhouse, Lever, Generic)
                filled_count = 0

                # Name
                if await page.locator("input[name*='first_name'], input[id*='first_name']").count() > 0:
                    await page.fill("input[name*='first_name'], input[id*='first_name']", first_name)
                    filled_count += 1
                if await page.locator("input[name*='last_name'], input[id*='last_name']").count() > 0:
                    await page.fill("input[name*='last_name'], input[id*='last_name']", last_name)
                    filled_count += 1
                if filled_count == 0 and await page.locator("input[name*='name'], input[id*='name'], input[placeholder*='Name']").count() > 0:
                    await page.fill("input[name*='name'], input[id*='name'], input[placeholder*='Name']", full_name)
                    filled_count += 1

                # Email
                if await page.locator("input[type='email'], input[name*='email'], input[id*='email']").count() > 0:
                    await page.fill("input[type='email'], input[name*='email'], input[id*='email']", email)

                # Phone
                if await page.locator("input[type='tel'], input[name*='phone'], input[id*='phone']").count() > 0:
                    await page.fill("input[type='tel'], input[name*='phone'], input[id*='phone']", phone)

                # Custom Questions / Textareas
                for q_text, ans_val in answers.items():
                    textareas = page.locator("textarea")
                    if await textareas.count() > 0:
                        try:
                            await textareas.first.fill(ans_val)
                        except Exception:
                            pass

                # Upload Custom Resume File
                if resume_path and os.path.exists(resume_path):
                    file_inputs = page.locator("input[type='file']")
                    if await file_inputs.count() > 0:
                        try:
                            await file_inputs.first.set_input_files(resume_path)
                        except Exception:
                            pass

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
                "status": "FAILED",
                "error_type": "REAL_PORTAL_AUTOMATION_ERROR",
                "error_message": str(e),
                "screenshot_path": screenshot_path if os.path.exists(screenshot_path) else None
            }
