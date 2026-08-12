import uvloop
from kai_shared.io.node import PipelineNode
from kai_shared.utils.logger import setup_logging

from src.kai_llm.config_llm import settings_llm


async def main() -> None:
    setup_logging()
    node = PipelineNode(settings_llm.shared)
    await node.run()


if __name__ == "__main__":
    uvloop.run(main())


# import asyncio
# from collections.abc import AsyncGenerator
# from typing import Any

# from kai_shared.config_shared import SharedConfig
# from kai_shared.io.node import PipelineNode
# from kai_shared.schemata.ipc import StreamMetadata
# from pydantic import ValidationError
# from vllm.engine.arg_utils import AsyncEngineArgs
# from vllm.engine.protocol import StreamingInput
# from vllm.sampling_params import SamplingParams
# from vllm.v1.engine.async_llm import AsyncLLM

# from src.kai_llm.config_llm import settings_llm


# class LLMNode(PipelineNode):
#     def __init__(self, config: SharedConfig):
#         super().__init__(config)
#         self.engine: AsyncLLM | None = None
#         self.active_queues: dict[str, asyncio.Queue[tuple[StreamMetadata, bytes]]] = {}

#     async def start(self) -> None:
#         engine_args_dict = settings_llm.vllm_config.model_dump(exclude_none=True)
#         engine_args = AsyncEngineArgs(**engine_args_dict)
#         self.engine = AsyncLLM.from_engine_args(engine_args)
#         await super().start()

#     async def handle_data(
#         self, topic: bytes, metadata_bytes: bytes, payload: bytes
#     ) -> None:
#         try:
#             metadata = StreamMetadata.model_validate_json(metadata_bytes)
#         except ValidationError:
#             return

#         if metadata.stream_type != "audio":
#             return

#         req_id = metadata.request_id
#         if req_id not in self.active_queues:
#             queue: asyncio.Queue[tuple[StreamMetadata, bytes]] = asyncio.Queue()
#             self.active_queues[req_id] = queue
#             asyncio.create_task(self._process_stream(req_id, queue))
#         else:
#             queue = self.active_queues[req_id]

#         await queue.put((metadata, payload))

#     async def _input_generator(
#         self, req_id: str, queue: asyncio.Queue[tuple[StreamMetadata, bytes]]
#     ) -> AsyncGenerator[StreamingInput]:
#         while True:
#             metadata, payload = await queue.get()

#             prompt_data: Any = {
#                 "prompt": "<|audio|>",
#                 "multi_modal_data": {"audio": payload},
#             }

#             yield StreamingInput(prompt=prompt_data)

#             if metadata.is_final:
#                 break

#     async def _process_stream(
#         self, req_id: str, queue: asyncio.Queue[tuple[StreamMetadata, bytes]]
#     ) -> None:
#         if self.engine is None:
#             raise RuntimeError("Engine is not initialized.")

#         sampling_params = SamplingParams(max_tokens=1)

#         try:
#             output_generator = self.engine.generate(
#                 prompt=self._input_generator(req_id, queue),
#                 sampling_params=sampling_params,
#                 request_id=req_id,
#             )

#             async for output in output_generator:
#                 if output.outputs:
#                     token_text = output.outputs[0].text
#                     is_final = output.finished
#                     out_meta = StreamMetadata(
#                         request_id=req_id, is_final=is_final, stream_type="token"
#                     )
#                     await self.publisher.send_stream(
#                         topic=b"llm_output",
#                         metadata=out_meta,
#                         payload=token_text.encode("utf-8"),
#                     )
#                     if is_final:
#                         break
#         finally:
#             if req_id in self.active_queues:
#                 del self.active_queues[req_id]


# async def main() -> None:
#     node = LLMNode(settings_llm.shared)
#     await node.run()


# if __name__ == "__main__":
#     asyncio.run(main())
