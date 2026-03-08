from fastapi import FastAPI

from app.config import settings
from app.routers import applications, ats, auth, drive, jd, resumes, skills

app = FastAPI(title=settings.app_name)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(resumes.router, prefix="/api/v1/resumes", tags=["resumes"])
app.include_router(jd.router, prefix="/api/v1", tags=["job-descriptions", "tailor-runs"])
app.include_router(ats.router, prefix="/api/v1", tags=["ats"])
app.include_router(skills.router, prefix="/api/v1", tags=["skills-gap"])
app.include_router(applications.router, prefix="/api/v1/applications", tags=["applications"])
app.include_router(drive.router, prefix="/api/v1/drive", tags=["drive"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
