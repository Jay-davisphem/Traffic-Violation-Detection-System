from pydantic import BaseModel

class Violation(BaseModel):
    type: str
    bbox: list[int]
    position_description: str
    confidence: float

class ViolationResponse(BaseModel):
    violations: list[Violation]
