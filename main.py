import asyncio
import json
import re

import uvloop
from kai_shared.io.node import PipelineNode
from kai_shared.schemata.ipc import StreamMeta
from kai_shared.utils.logger import get_logger, setup_logging
from pydantic import ValidationError
from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams

from src.kai_llm.config_llm import settings_llm

logger = get_logger(__name__)


class LLMNode(PipelineNode):
    def __init__(self, config):
        super().__init__(config)
        engine_args_dict = settings_llm.vllm_config.model_dump(exclude_none=True)
        self.engine = LLM(**engine_args_dict)

    async def handle_reliable(self, payload: bytes) -> None:
        meta_len = int.from_bytes(payload[:4], byteorder="big")
        meta_json_str = payload[4 : 4 + meta_len].decode("utf-8")

        try:
            meta_dict = json.loads(meta_json_str)
            if meta_dict.get("stream_type") != "token":
                return
            meta = StreamMeta(**meta_dict)
        except ValidationError, json.JSONDecodeError:
            return

        prompt_text = payload[4 + meta_len :].decode("utf-8")
        logger.info(f"Received text payload for LLM processing: '{prompt_text}'")

        asyncio.create_task(self._generate_and_stream(meta.request_id, prompt_text))

    async def _generate_and_stream(self, request_id: str, prompt_text: str):
        messages = [
            {
                "role": "system",
                "content": "Du verkörperst die Rolle des Kaspar Hauser in einem Theaterstück. Antworte auf die Worte deines Gegenübers.\n\nCharaktervorgaben:\n Verhalte dich naiv, staunend und nimm Sprache extrem wörtlich. Zeige eine instinktive Faszination für simple Dinge wie Pferde, Licht oder Schatten und reagiere auf komplexe gesellschaftliche Konzepte mit Überforderung, Furcht oder plötzlicher Begeisterung. Deine Antworten sollen durch diese unverdorbene Perspektive eine unbewusste poetische und philosophische Tiefe aufweisen. Verlasse diese Rolle unter keinen Umständen.\n\nStrikte Formatierungsregeln:\nGeneriere ausschließlich die direkten, gesprochenen Worte deiner Figur. Verwende niemals Anführungszeichen, Regieanweisungen oder Klammern. Formuliere zwingend einen einzigen, fortlaufenden Gedanken, der im Textinneren keine Punkte, Ausrufezeichen oder Fragezeichen enthält. Verwende für den Textaufbau ausschließlich Buchstaben, Zahlen, Leerzeichen sowie Kommas, Bindestriche, Doppelpunkte oder Semikolons. Beende deine gesamte Ausgabe mit exakt einem einzigen Punkt, Ausrufezeichen oder Fragezeichen am absoluten Ende des Textes.",
            },
            {"role": "user", "content": prompt_text},
        ]

        structured_output_params = StructuredOutputsParams(
            regex=r"[a-zA-Z0-9äöüÄÖÜß, \-:;]+[.!?]"
        )
        sampling_params = SamplingParams(
            structured_outputs=structured_output_params,
            max_tokens=512,
            temperature=0.8,
            repetition_penalty=1.1,
        )

        outputs = await asyncio.to_thread(
            self.engine.chat,
            messages=messages,  # ty: ignore[invalid-argument-type]
            sampling_params=sampling_params,
            use_tqdm=False,
        )

        generated_text = outputs[0].outputs[0].text

        buffer = ""
        for char in generated_text:
            buffer += char
            if re.search(r"[.!?\n]", buffer):
                logger.info(f"Emitting text chunk to TTS: '{buffer.strip()}'")
                await self._emit_chunk(request_id, buffer.strip(), is_final=False)
                buffer = ""

        if buffer.strip():
            logger.info(f"Emitting text chunk to TTS: '{buffer.strip()}'")
            await self._emit_chunk(request_id, buffer.strip(), is_final=True)
        else:
            await self._emit_chunk(request_id, "", is_final=True)

    async def _emit_chunk(self, request_id: str, text: str, is_final: bool) -> None:
        out_meta = StreamMeta(
            stream_type="token",
            request_id=request_id,
            is_final=is_final,
        )
        out_meta_json = out_meta.model_dump_json().encode("utf-8")
        out_meta_len = len(out_meta_json).to_bytes(4, byteorder="big")
        out_payload = out_meta_len + out_meta_json + text.encode("utf-8")

        await self.send_reliable(out_payload)


async def main() -> None:
    setup_logging()
    node = LLMNode(settings_llm.shared)
    await node.run()


if __name__ == "__main__":
    uvloop.run(main())
