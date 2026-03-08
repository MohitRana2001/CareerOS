import re
import uuid
from collections import Counter
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import JobDescription
from app.schemas import JobDescriptionCreateRequest


class JobDescriptionService:
    def __init__(self, db: Session):
        self.db = db

    def create_job_description(self, user_id: uuid.UUID, payload: JobDescriptionCreateRequest) -> JobDescription:
        now = datetime.now(UTC)
        extracted = _extract_requirements(payload.raw_text)
        jd = JobDescription(
            id=uuid.uuid4(),
            user_id=user_id,
            company_name=payload.company_name,
            position_title=payload.position_title,
            source_url=payload.source_url,
            raw_text=payload.raw_text,
            extracted_requirements=extracted,
            created_at=now,
        )
        self.db.add(jd)
        self.db.commit()
        self.db.refresh(jd)
        return jd

    def get_job_description(self, user_id: uuid.UUID, job_description_id: uuid.UUID) -> JobDescription:
        row = self.db.execute(
            select(JobDescription).where(
                JobDescription.id == job_description_id,
                JobDescription.user_id == user_id,
            )
        ).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job description not found")
        return row


def _extract_requirements(raw_text: str) -> dict[str, list[str]]:
    words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", raw_text)]
    stop_words = {
        "with",
        "and",
        "for",
        "you",
        "your",
        "this",
        "that",
        "the",
        "are",
        "our",
        "will",
        "from",
        "have",
        "has",
        "all",
        "job",
        "role",
        "team",
    }
    filtered = [w for w in words if w not in stop_words]
    top = [term for term, _count in Counter(filtered).most_common(20)]
    return {"keywords": top}
