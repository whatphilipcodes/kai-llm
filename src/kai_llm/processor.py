import asyncio
import time
from typing import Optional

from src.kai_llm.engine import LLMEngine
from src.kai_llm.io.receiver import Receiver
from src.kai_llm.io.sender import Sender
from src.kai_llm.schemata.ipc import DataReceive, DataSend
from src.kai_llm.utils.logger import get_logger

logger = get_logger(__name__)

class StreamProcessor:
    def __init__(self, receiver: Receiver, sender: Sender, engine: LLMEngine):
        self.receiver = receiver
        self.sender = sender
        self.engine = engine
        self.prompt_queue: asyncio.Queue[DataReceive] = asyncio.Queue()
        self._running = False
        
        # Register the callback from the Receiver to put items in our async queue
        self.receiver.register_callback(self._on_receive)

    def _on_receive(self, data: DataReceive) -> None:
        """Called by the receiver's listener thread when a payload arrives."""
        logger.info(f"Received prompt: {data.prompt}")
        # Put into the queue thread-safely
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(self.prompt_queue.put_nowait, data)
        except RuntimeError:
            # If there's no running loop in the thread, we might be starting up or shutting down
            logger.warning("No running loop available to enqueue the prompt.")

    async def start(self) -> None:
        """Starts the main async processing loop."""
        self._running = True
        logger.info("StreamProcessor started.")
        while self._running:
            try:
                # Wait for a prompt to arrive
                data = await self.prompt_queue.get()
                logger.info(f"Processing prompt: {data.prompt}")
                
                # Stream the output tokens
                async for text_token in self.engine.generate_stream(data.prompt):
                    if not self._running:
                        break
                    
                    payload = DataSend(
                        timestamp=time.time(),
                        text_token=text_token
                    )
                    self.sender.send_payload(payload)
                
                logger.info("Finished processing prompt.")
                self.prompt_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error during stream processing: {e}")

    def stop(self) -> None:
        """Signals the processor to stop."""
        self._running = False
        logger.info("StreamProcessor stopped.")
