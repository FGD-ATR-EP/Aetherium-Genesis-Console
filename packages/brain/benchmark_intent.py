import asyncio
import time
import random
from unittest.mock import MagicMock, patch

# Mock dependencies before importing IntentProcessor
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[0]))

# Mock chromadb and other modules that might not be present
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()

class MockVault:
    async def store_gem(self, text, metadata):
        # Simulate non-blocking I/O
        await asyncio.sleep(0.1)

class MockBus:
    async def publish(self, topic, payload, identity):
        pass

# Mock ZoIdentity since it's missing from identity.py but imported in intent_processor.py
class MockZoIdentity:
    def __init__(self, role="UNKNOWN"):
        self.role = role
    def get_identity_header(self):
        return {"role": self.role, "source_id": "mock_id"}

import identity
identity.ZoIdentity = MockZoIdentity

# Now import IntentProcessor
from intent_processor import IntentProcessor

async def measure_latency(stop_event):
    max_latency = 0
    while not stop_event.is_set():
        start = time.perf_counter()
        await asyncio.sleep(0.01)
        latency = time.perf_counter() - start - 0.01
        if latency > max_latency:
            max_latency = latency
    return max_latency

async def run_benchmark():
    print("Starting benchmark...")

    # Setup mocks
    mock_bus = MockBus()

    # Patch Vault and AetherBus in intent_processor
    with patch('intent_processor.Vault', return_value=MockVault()), \
         patch('intent_processor.AetherBus', return_value=mock_bus), \
         patch('random.random', return_value=0.0): # Ensure Path A (is_ambiguous = False)

        processor = IntentProcessor(mock_bus)

        stop_event = asyncio.Event()
        latency_task = asyncio.create_task(measure_latency(stop_event))

        # We need to wait a bit for the latency task to start and settle
        await asyncio.sleep(0.1)

        print("Processing voice input (this should block)...")
        # process_voice_input has an internal await asyncio.sleep(2.0)
        # We want to measure the block during _crystallize_intent
        await processor.process_voice_input("Benchmark Intent")

        stop_event.set()
        max_latency = await latency_task

    print(f"Max event loop latency: {max_latency:.4f} seconds")
    return max_latency

if __name__ == "__main__":
    asyncio.run(run_benchmark())
