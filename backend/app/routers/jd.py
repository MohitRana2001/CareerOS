from fastapi import APIRouter

router = APIRouter()


@router.post("/job-descriptions")
def create_jd() -> dict[str, str]:
    return {"message": "TODO: create job description"}


@router.post("/tailor-runs")
def create_tailor_run() -> dict[str, str]:
    return {"message": "TODO: start tailoring run"}


@router.get("/tailor-runs/{run_id}")
def get_tailor_run(run_id: str) -> dict[str, str]:
    return {"message": f"TODO: get tailor run {run_id}"}
