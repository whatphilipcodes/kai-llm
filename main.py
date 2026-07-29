import asyncio

from kai_shared.io.node import PipelineNode
from kai_shared.utils.logger import get_logger, setup_logging

from src.kai_llm.config_llm import settings_llm

setup_logging()
logger = get_logger(__name__)


async def main() -> None:
    app_node = PipelineNode(config=settings_llm.shared)
    await app_node.run()


if __name__ == "__main__":
    asyncio.run(main())
