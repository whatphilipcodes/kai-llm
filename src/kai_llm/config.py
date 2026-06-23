from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

from src.kai_llm.utils.custom_types import LogLevel, NetworkProtocol

class SystemConfig(BaseModel):
    log_level: LogLevel = LogLevel.INFO

class NetworkConfig(BaseModel):
    protocol: NetworkProtocol = NetworkProtocol.TCP
    port_in: int = 5554
    port_out: int = 5555

class LLMConfig(BaseModel):
    model: str = "google/gemma-4-E4B-it-qat-w4a16-ct"
    tensor_parallel_size: int = 1
    max_num_batched_tokens: int = 8192
    max_model_len: int | None = None
    limit_mm_per_prompt: dict[str, int] = {"video": 1, "audio": 1}

class GlobalConfig(BaseSettings):
    model_config = ConfigDict(frozen=True)
    system: SystemConfig = SystemConfig()
    network: NetworkConfig = NetworkConfig()
    llm: LLMConfig = LLMConfig()

settings = GlobalConfig()
