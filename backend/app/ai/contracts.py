from pydantic import BaseModel, ConfigDict, Field


class TailorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tailored_summary: str = Field(min_length=20)
    rewritten_bullets: list[str] = Field(min_length=3, max_length=12)
    keywords_used: list[str] = Field(min_length=3, max_length=20)


def validate_tailor_output(payload: dict) -> TailorOutput:
    return TailorOutput.model_validate(payload)
