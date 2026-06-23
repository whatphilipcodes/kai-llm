from pydantic import BaseModel, Field

class DataReceive(BaseModel):
    """Schema for incoming data validation (prompts)."""
    timestamp: float = Field(..., description="Creation time of the payload")
    prompt: str = Field(..., description="Text prompt to generate from")

class DataSend(BaseModel):
    """Schema for outgoing data validation (tokens)."""
    timestamp: float = Field(..., description="Creation time of the payload")
    text_token: str = Field(..., description="LLM text token to process")
