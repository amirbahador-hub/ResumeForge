from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI

from resumeforge.pipeline import ResumeForgePipeline
from resumeforge.schemas import PipelineRequest, PipelineResponse
from resumeforge.yaml_io import to_plain_data

api = FastAPI(
    title="ResumeForge",
    version="0.1.0",
    description="Multi-agent resume intelligence and truthful optimization API.",
)


@api.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@api.post("/pipeline/run", response_model=PipelineResponse)
async def run_pipeline(request: PipelineRequest) -> PipelineResponse:
    run_id = str(uuid4())
    artifact_dir = Path(request.artifact_dir) if request.artifact_dir else None
    result = await ResumeForgePipeline(artifact_dir=artifact_dir).run(request.input)
    return PipelineResponse(
        run_id=run_id,
        artifacts={
            artifact.artifact_type.value: to_plain_data(artifact) for artifact in result.artifacts()
        },
    )
