import asyncio
import sys

from src.kai_llm.utils.logger import get_logger, setup_logging
from src.kai_llm.io.sender import Sender
from src.kai_llm.io.receiver import Receiver
from src.kai_llm.engine import LLMEngine
from src.kai_llm.processor import StreamProcessor

setup_logging()
logger = get_logger(__name__)

async def amain():
    logger.critical("Launching kai_llm module...")
    
    # Initialize networking nodes
    sender = Sender()
    receiver = Receiver()
    
    # Initialize engine and processor
    logger.info("Initializing vLLM engine...")
    engine = LLMEngine()
    
    logger.info("Initializing processor...")
    processor = StreamProcessor(receiver, sender, engine)
    
    # Start the components
    receiver.start()
    
    try:
        logger.info("Ready. Waiting for prompts. Press Ctrl+C to exit.")
        await processor.start()
    except asyncio.CancelledError:
        logger.info("Shutdown signal received.")
    finally:
        processor.stop()
        receiver.stop()
        sender.close()

def main():
    try:
        asyncio.run(amain())
    except KeyboardInterrupt:
        logger.info("Interrupted. Shutting down gracefully.")
        sys.exit(0)

if __name__ == "__main__":
    main()
