from kai_shared.config_shared import SharedConfig
from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class VLLMConfig(BaseModel):
    model: str = "google/gemma-4-E4B-it-qat-w4a16-ct"
    tensor_parallel_size: int = 1
    max_num_batched_tokens: int = 8192
    max_model_len: int | None = 4096
    limit_mm_per_prompt: dict[str, int] = {"video": 1, "audio": 1}
    gpu_memory_utilization: float = 0.2


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")
    shared: SharedConfig = SharedConfig()
    vllm_config: VLLMConfig = VLLMConfig()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)


settings_llm = LLMConfig()
