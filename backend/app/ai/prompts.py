def build_tailor_prompt(resume_text: str, jd_text: str, prompt_version: str | None) -> str:
    version = prompt_version or "v1"
    return (
        f"You are a resume tailoring assistant. Prompt version: {version}.\\n"
        "Constraints:\\n"
        "1) Do not invent experience, companies, or metrics.\\n"
        "2) Keep claims grounded in provided resume content.\\n"
        "3) Optimize for ATS keyword alignment from JD.\\n"
        "4) Return strict JSON only with keys: tailored_summary, rewritten_bullets, keywords_used.\\n"
        "5) rewritten_bullets must have 3-8 bullets.\\n\\n"
        f"Resume source:\\n{resume_text}\\n\\n"
        f"Job description:\\n{jd_text}"
    )
