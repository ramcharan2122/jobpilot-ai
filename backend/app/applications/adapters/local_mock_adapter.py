import os
import asyncio
from playwright.async_api import async_playwright
from app.core.config import settings

class LocalMockApplicationAdapter:
    
    async def apply_to_job(self, application_id: int, application_url: str, user_profile: dict, resume_path: str, answers: dict) -> dict:
        """
        Executes automated form filling using Playwright browser.
        Handles form field mapping, custom question auto-filling, file uploading, and confirmation.
        """
        screenshot_path = os.path.join(settings.STORAGE_DIR, "screenshots", f"app_{application_id}.png")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate to application URL
                await page.goto(application_url, wait_until="networkidle", timeout=15000)
                
                # Check for security / captcha flag
                page_text = await page.content()
                if "captcha" in page_text.lower() or "challenge" in page_text.lower():
                    await page.screenshot(path=screenshot_path)
                    await browser.close()
                    return {
                        "status": "ACTION_REQUIRED",
                        "error_type": "CAPTCHA_DETECTED",
                        "error_message": "Security verification required. Human action needed.",
                        "screenshot_path": screenshot_path
                    }

                # Fill Personal Info fields if present
                full_name = f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip() or "Applicant Name"
                email = user_profile.get("email") or "applicant@example.com"
                phone = user_profile.get("phone") or "+91 9876543210"
                
                # Attempt to fill form fields by selector or label
                if await page.locator("input[name='fullName']").count() > 0:
                    await page.fill("input[name='fullName']", full_name)
                elif await page.locator("#fullName").count() > 0:
                    await page.fill("#fullName", full_name)
                    
                if await page.locator("input[name='email']").count() > 0:
                    await page.fill("input[name='email']", email)
                elif await page.locator("#email").count() > 0:
                    await page.fill("#email", email)

                if await page.locator("input[name='phone']").count() > 0:
                    await page.fill("input[name='phone']", phone)
                elif await page.locator("#phone").count() > 0:
                    await page.fill("#phone", phone)

                # Fill custom question fields if answers provided
                for q_text, answer_val in answers.items():
                    # Look for textareas or inputs
                    textareas = page.locator("textarea")
                    if await textareas.count() > 0:
                        await textareas.first.fill(answer_val)

                # Attach generated custom resume file
                if resume_path and os.path.exists(resume_path):
                    file_inputs = page.locator("input[type='file']")
                    if await file_inputs.count() > 0:
                        await file_inputs.first.set_input_files(resume_path)

                # Take pre-submission screenshot
                await page.screenshot(path=screenshot_path)
                
                # Click Submit button if present
                submit_btn = page.locator("button[type='submit']")
                if await submit_btn.count() > 0:
                    await submit_btn.first.click()
                    await page.wait_for_timeout(1000)

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
                "error_type": "AUTOMATION_ERROR",
                "error_message": str(e),
                "screenshot_path": screenshot_path if os.path.exists(screenshot_path) else None
            }
