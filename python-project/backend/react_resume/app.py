import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.react_resume.config import Settings
from backend.react_resume.llm import DeepSeekProvider, LLMProviderError
from backend.react_resume.models import OptimizeResumeResponse, ParsedResume
from backend.react_resume.parsers import UnsupportedFileTypeError, parse_resume_file
from backend.react_resume.workflow import ResumeOptimizationWorkflow

settings = Settings()

app = FastAPI(title="Resume ReAct Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def build_workflow() -> ResumeOptimizationWorkflow:
    provider = DeepSeekProvider(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        model=settings.deepseek_model,
    )
    return ResumeOptimizationWorkflow(provider)


def build_parsed_resume(
    file_name: str | None,
    content: bytes | None,
    resume_text: str | None,
) -> ParsedResume:
    clean_resume_text = (resume_text or "").strip()

    if content:
        if len(content) > settings.max_resume_bytes:
            raise HTTPException(status_code=400, detail="简历文件过大，请上传 5MB 以内的文件。")
        parsed = parse_resume_file(file_name or "resume", content)
    elif clean_resume_text:
        parsed = ParsedResume(
            file_name="pasted-resume.txt",
            file_type="text",
            raw_text=clean_resume_text,
            warnings=[],
        )
    else:
        raise HTTPException(status_code=400, detail="请上传简历文件或粘贴简历内容。")
    return parsed


def process_resume_request(
    file_name: str | None,
    content: bytes | None,
    resume_text: str | None,
    jd_text: str,
    target_company: str,
    target_role: str,
) -> OptimizeResumeResponse:
    parsed = build_parsed_resume(file_name=file_name, content=content, resume_text=resume_text)

    workflow = build_workflow()
    return workflow.run(
        parsed_resume=parsed,
        jd_text=jd_text,
        target_company=target_company,
        target_role=target_role,
    )


@app.post("/api/optimize-resume")
async def optimize_resume(
    target_company: str = Form(...),
    target_role: str = Form(...),
    jd_text: str = Form(...),
    resume_text: str = Form(default=""),
    resume_file: UploadFile | None = File(default=None),
):
    content = await resume_file.read() if resume_file else None
    try:
        return await run_in_threadpool(
            process_resume_request,
            file_name=resume_file.filename if resume_file else None,
            content=content,
            resume_text=resume_text,
            jd_text=jd_text,
            target_company=target_company,
            target_role=target_role,
        )
    except (UnsupportedFileTypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def encode_stream_event(event: dict) -> str:
    event_name = event.get("type", "message")
    payload = json.dumps(event, ensure_ascii=False)
    return f"event: {event_name}\ndata: {payload}\n\n"


def stream_resume_response(
    parsed_resume: ParsedResume,
    jd_text: str,
    target_company: str,
    target_role: str,
):
    try:
        workflow = build_workflow()
        for event in workflow.stream(
            parsed_resume=parsed_resume,
            jd_text=jd_text,
            target_company=target_company,
            target_role=target_role,
        ):
            yield encode_stream_event(event)
    except LLMProviderError as exc:
        yield encode_stream_event({"type": "error", "message": str(exc)})


@app.post("/api/optimize-resume/stream")
async def optimize_resume_stream(
    target_company: str = Form(...),
    target_role: str = Form(...),
    jd_text: str = Form(...),
    resume_text: str = Form(default=""),
    resume_file: UploadFile | None = File(default=None),
):
    content = await resume_file.read() if resume_file else None
    try:
        parsed_resume = await run_in_threadpool(
            build_parsed_resume,
            file_name=resume_file.filename if resume_file else None,
            content=content,
            resume_text=resume_text,
        )
    except (UnsupportedFileTypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return StreamingResponse(
        stream_resume_response(
            parsed_resume=parsed_resume,
            jd_text=jd_text,
            target_company=target_company,
            target_role=target_role,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
