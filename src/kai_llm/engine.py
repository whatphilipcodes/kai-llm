import uuid
from typing import AsyncGenerator

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm import SamplingParams

from src.kai_llm.config import settings

class LLMEngine:
    def __init__(self):
        engine_args = AsyncEngineArgs(
            model=settings.llm.model,
            tensor_parallel_size=settings.llm.tensor_parallel_size,
            max_num_batched_tokens=settings.llm.max_num_batched_tokens,
            max_model_len=settings.llm.max_model_len,
            limit_mm_per_prompt=settings.llm.limit_mm_per_prompt,
        )
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    async def generate_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        request_id = str(uuid.uuid4())
        # Using some default sampling parameters for now
        sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=1024)
        
        results_generator = self.engine.generate(prompt, sampling_params, request_id)
        
        last_text_len = 0
        async for request_output in results_generator:
            text = request_output.outputs[0].text
            new_text = text[last_text_len:]
            if new_text:
                last_text_len = len(text)
                yield new_text
