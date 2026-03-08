import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import JobDescription, ResumeDocument, ResumeVersion, TailorRun
from app.schemas import ResumeCreateRequest, ResumePatchRequest, ResumeVersionCreateRequest
from app.workers.tasks import compile_pdf


class ResumeService:
    def __init__(self, db: Session):
        self.db = db

    def create_resume(self, user_id: uuid.UUID, payload: ResumeCreateRequest) -> ResumeDocument:
        now = datetime.now(UTC)
        resume = ResumeDocument(
            id=uuid.uuid4(),
            user_id=user_id,
            source_file_url=payload.source_file_url,
            source_file_type=payload.source_file_type.value,
            canonical_json=None,
            created_at=now,
            updated_at=now,
        )
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def patch_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID, payload: ResumePatchRequest) -> ResumeDocument:
        resume = self.get_resume(user_id, resume_id)
        if payload.source_file_url is not None:
            resume.source_file_url = payload.source_file_url
        if payload.canonical_json is not None:
            resume.canonical_json = payload.canonical_json
        resume.updated_at = datetime.now(UTC)
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def list_resumes(self, user_id: uuid.UUID) -> list[ResumeDocument]:
        statement: Select[tuple[ResumeDocument]] = (
            select(ResumeDocument).where(ResumeDocument.user_id == user_id).order_by(ResumeDocument.created_at.desc())
        )
        return list(self.db.execute(statement).scalars())

    def get_resume(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> ResumeDocument:
        row = self.db.execute(
            select(ResumeDocument).where(
                ResumeDocument.id == resume_id,
                ResumeDocument.user_id == user_id,
            )
        ).scalar_one_or_none()

        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
        return row

    def create_version(
        self,
        user_id: uuid.UUID,
        resume_id: uuid.UUID,
        payload: ResumeVersionCreateRequest,
    ) -> ResumeVersion:
        resume = self.get_resume(user_id, resume_id)

        if payload.based_on_version_id is not None:
            base_version = self.get_version(user_id, resume_id, payload.based_on_version_id)
            if base_version.resume_document_id != resume.id:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid base version")

        if payload.job_description_id is not None:
            jd_exists = self.db.execute(
                select(JobDescription).where(
                    JobDescription.id == payload.job_description_id,
                    JobDescription.user_id == user_id,
                )
            ).scalar_one_or_none()
            if jd_exists is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid job description")

        current_max = self.db.execute(
            select(func.max(ResumeVersion.version_no)).where(ResumeVersion.resume_document_id == resume.id)
        ).scalar_one_or_none()
        next_version = (current_max or 0) + 1

        version = ResumeVersion(
            id=uuid.uuid4(),
            resume_document_id=resume.id,
            version_no=next_version,
            based_on_version_id=payload.based_on_version_id,
            job_description_id=payload.job_description_id,
            latex_source=payload.latex_source,
            pdf_file_url=None,
            compile_status="PENDING",
            created_by=payload.created_by.value,
            created_at=datetime.now(UTC),
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def list_versions(self, user_id: uuid.UUID, resume_id: uuid.UUID) -> list[ResumeVersion]:
        self.get_resume(user_id, resume_id)
        statement: Select[tuple[ResumeVersion]] = (
            select(ResumeVersion).where(ResumeVersion.resume_document_id == resume_id).order_by(ResumeVersion.version_no.desc())
        )
        return list(self.db.execute(statement).scalars())

    def get_version(self, user_id: uuid.UUID, resume_id: uuid.UUID, version_id: uuid.UUID) -> ResumeVersion:
        self.get_resume(user_id, resume_id)
        row = self.db.execute(
            select(ResumeVersion).where(
                ResumeVersion.id == version_id,
                ResumeVersion.resume_document_id == resume_id,
            )
        ).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume version not found")
        return row

    def queue_compile(self, user_id: uuid.UUID, resume_id: uuid.UUID, version_id: uuid.UUID) -> ResumeVersion:
        version = self.get_version(user_id, resume_id, version_id)
        version.compile_status = "RUNNING"
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        compile_pdf.delay(str(version.id))
        return version

    def get_ats(self, user_id: uuid.UUID, resume_id: uuid.UUID, version_id: uuid.UUID) -> dict:
        version = self.get_version(user_id, resume_id, version_id)
        if version.job_description_id is None:
            return {"score": 0, "breakdown": {"keyword_alignment": 0, "format_compliance": 100, "content_quality": 0}}

        run = self.db.execute(
            select(TailorRun).where(
                TailorRun.output_resume_version_id == version.id,
                TailorRun.user_id == user_id,
            )
        ).scalar_one_or_none()
        alignment = (run.ats_keyword_alignment if run else None) or {}
        keyword_score = int(alignment.get("alignment_score") or 0)
        format_score = 100 if version.compile_status in {"RUNNING", "SUCCEEDED"} else 60
        content_score = min(100, max(0, int((len(version.latex_source) / 1200) * 100)))
        total = round((keyword_score * 0.6) + (format_score * 0.2) + (content_score * 0.2))
        return {
            "score": total,
            "breakdown": {
                "keyword_alignment": keyword_score,
                "format_compliance": format_score,
                "content_quality": content_score,
            },
        }

    def get_skills_gap(self, user_id: uuid.UUID, resume_id: uuid.UUID, version_id: uuid.UUID) -> dict:
        version = self.get_version(user_id, resume_id, version_id)
        if version.job_description_id is None:
            return {"critical_missing": [], "nice_to_have_missing": []}

        jd = self.db.execute(
            select(JobDescription).where(
                JobDescription.id == version.job_description_id,
                JobDescription.user_id == user_id,
            )
        ).scalar_one_or_none()
        if jd is None or not jd.extracted_requirements:
            return {"critical_missing": [], "nice_to_have_missing": []}

        keywords = [str(k).lower() for k in jd.extracted_requirements.get("keywords", [])]
        text = version.latex_source.lower()
        missing = [k for k in keywords if k not in text]
        split = max(0, len(missing) // 2)
        critical = missing[:split] if split else missing[: min(3, len(missing))]
        nice = missing[split:] if split else missing[min(3, len(missing)) :]
        return {"critical_missing": critical, "nice_to_have_missing": nice}
