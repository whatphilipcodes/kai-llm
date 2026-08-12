import asyncio
import json
import re
import time

import uvloop
from kai_shared.io.node import PipelineNode
from kai_shared.schemata.ipc import TokenStreamMetadata
from kai_shared.utils.logger import get_logger, setup_logging
from pydantic import ValidationError
from vllm import AsyncEngineArgs, AsyncLLMEngine, SamplingParams

from src.kai_llm.config_llm import settings_llm

logger = get_logger(__name__)


class LLMNode(PipelineNode):
    def __init__(self, config):
        super().__init__(config)
        engine_args_dict = settings_llm.vllm_config.model_dump(exclude_none=True)
        engine_args = AsyncEngineArgs(**engine_args_dict)
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    async def handle_reliable(self, payload: bytes) -> None:
        meta_len = int.from_bytes(payload[:4], byteorder="big")
        meta_json_str = payload[4 : 4 + meta_len].decode("utf-8")

        try:
            meta_dict = json.loads(meta_json_str)
            if meta_dict.get("stream_type") != "token":
                return
            meta = TokenStreamMetadata(**meta_dict)
        except ValidationError, json.JSONDecodeError:
            return

        prompt_text = payload[4 + meta_len :].decode("utf-8")
        formatted_prompt = f"<bos><start_of_turn>user\n{prompt_text}<end_of_turn>\n<start_of_turn>model\n"

        logger.info(f"Received text payload for LLM processing: '{prompt_text}'")
        asyncio.create_task(
            self._generate_and_stream(meta.request_id, formatted_prompt)
        )

    async def _generate_and_stream(self, request_id: str, prompt: str):
        sampling_params = SamplingParams(
            max_tokens=256, temperature=0.7, repetition_penalty=1.1
        )
        results_generator = self.engine.generate(
            prompt, sampling_params, request_id=str(time.time())
        )

        previous_text = ""
        buffer = ""

        async for request_output in results_generator:
            text = request_output.outputs[0].text
            delta = text[len(previous_text) :]
            previous_text = text
            buffer += delta

            is_final = request_output.finished

            if re.search(r"[.!?\n]", buffer) or is_final:
                if buffer.strip():
                    logger.info(f"Emitting text chunk to TTS: '{buffer.strip()}'")
                    out_meta = TokenStreamMetadata(
                        request_id=request_id,
                        is_final=is_final,
                    )
                    out_meta_json = out_meta.model_dump_json().encode("utf-8")
                    out_meta_len = len(out_meta_json).to_bytes(4, byteorder="big")
                    out_payload = out_meta_len + out_meta_json + buffer.encode("utf-8")

                    await self.send_reliable(out_payload)
                    buffer = ""


async def main() -> None:
    setup_logging()
    node = LLMNode(settings_llm.shared)
    await node.run()


if __name__ == "__main__":
    uvloop.run(main())
