from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/mock-portal", tags=["Mock Portal"])

@router.get("/apply", response_class=HTMLResponse)
async def mock_application_form(job: str = "demo-001"):
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Mock ATS Career Portal - Job Application</title>
        <style>
            body {{ font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; display: flex; justify-content: center; }}
            .card {{ background: #1e293b; border-radius: 12px; padding: 32px; width: 100%; max-width: 600px; border: 1px solid #334155; }}
            h2 {{ margin-top: 0; color: #38bdf8; }}
            .form-group {{ margin-bottom: 20px; }}
            label {{ display: block; margin-bottom: 8px; font-weight: 500; font-size: 14px; color: #94a3b8; }}
            input[type="text"], input[type="email"], input[type="tel"], textarea {{
                width: 100%; padding: 10px 14px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 14px; box-sizing: border-box;
            }}
            input[type="file"] {{ color: #94a3b8; }}
            button {{ background: #0284c7; color: #fff; border: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; cursor: pointer; width: 100%; margin-top: 10px; }}
            button:hover {{ background: #0369a1; }}
            .badge {{ background: #0369a1; color: #e0f2fe; padding: 4px 8px; border-radius: 4px; font-size: 12px; display: inline-block; margin-bottom: 16px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <span class="badge">DEMO ATS PORTAL</span>
            <h2>Apply for Position ({job})</h2>
            <form action="/api/v1/mock-portal/submit" method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="fullName">Full Name *</label>
                    <input type="text" id="fullName" name="fullName" placeholder="John Doe" required />
                </div>
                <div class="form-group">
                    <label for="email">Email Address *</label>
                    <input type="email" id="email" name="email" placeholder="john@example.com" required />
                </div>
                <div class="form-group">
                    <label for="phone">Phone Number *</label>
                    <input type="tel" id="phone" name="phone" placeholder="+91 9876543210" required />
                </div>
                <div class="form-group">
                    <label for="questions">Why do you want to work here & expected salary?</label>
                    <textarea id="questions" name="questions" rows="4" placeholder="Enter details..."></textarea>
                </div>
                <div class="form-group">
                    <label for="resume">Attach Tailored PDF Resume *</label>
                    <input type="file" id="resume" name="resume" accept=".pdf" />
                </div>
                <button type="submit" id="submitBtn">Submit Application</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post("/submit", response_class=HTMLResponse)
async def mock_submit_success():
    return HTMLResponse(content="""
    <html>
    <body style="background:#0f172a; color:#f8fafc; font-family:sans-serif; text-align:center; padding-top:100px;">
        <h1 style="color:#4ade80;">Application Submitted Successfully!</h1>
        <p>Thank you for applying. Confirmation ID: #DEMO-SUBMIT-2026</p>
    </body>
    </html>
    """)
