from pydantic import BaseModel, Field


class ParsedResume(BaseModel):
    file_name: str
    file_type: str
    raw_text: str
    warnings: list[str] = Field(default_factory=list)


class ResumeIssue(BaseModel):
    category: str
    description: str
    severity: int = Field(ge=1, le=5)
    evidence: str


class OptimizationStep(BaseModel):
    round_number: int = Field(ge=1, le=3)
    goal: str
    action_name: str
    result: str


class EvaluationResult(BaseModel):
    score: int = Field(ge=0, le=100)
    covered_issues: list[str]
    remaining_issues: list[str]
    should_continue: bool
    feedback: str


class AgentTrace(BaseModel):
    round: int
    agent: str
    thought: str
    action: str
    observation: str


class OptimizeResumeRequest(BaseModel):
    target_company: str
    target_role: str
    jd_text: str


class OptimizeResumeResponse(BaseModel):
    diagnosis: str
    react_trace: list[AgentTrace]
    optimized_resume: str
    interview_questions: list[str]
    warnings: list[str] = Field(default_factory=list)
