import asyncio
import time
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure we can import from the brain package
sys.path.append(os.path.join(os.getcwd(), "packages", "brain"))

# Mock chromadb
mock_chroma = MagicMock()
sys.modules['chromadb'] = mock_chroma
sys.modules['chromadb.config'] = MagicMock()

from memory.akashic_vault import AkashicVault

class MockGems:
    def upsert(self, **kwargs):
        # Simulate blocking I/O
        time.sleep(0.1)

async def measure_latency(stop_event):
    latencies = []
    while not stop_event.is_set():
        start = time.perf_counter()
        await asyncio.sleep(0.01)
        latencies.append(time.perf_counter() - start - 0.01)
    return max(latencies) if latencies else 0

async def benchmark_blocking():
    print("Benchmarking blocking commit_change...")
    with patch('chromadb.PersistentClient') as mock_client:
        mock_client.return_value.get_or_create_collection.return_value = MockGems()
        vault = AkashicVault(persist_path="mock_db")

        stop_event = asyncio.Event()
        latency_task = asyncio.create_task(measure_latency(stop_event))

        await asyncio.sleep(0.1)

        physics_params = {"vibe_score": 0.8, "emotional_tone": "WAKING"}
        text = "test intent"

        start_time = time.perf_counter()
        vault.commit_change(physics_params, text)
        end_time = time.perf_counter()

        print(f"commit_change took {end_time - start_time:.4f}s")

        stop_event.set()
        max_latency = await latency_task
        print(f"Max event loop latency: {max_latency:.4f}s")
        return max_latency

async def benchmark_non_blocking():
    print("\nBenchmarking non-blocking (to_thread) commit_change...")
    with patch('chromadb.PersistentClient') as mock_client:
        mock_client.return_value.get_or_create_collection.return_value = MockGems()
        vault = AkashicVault(persist_path="mock_db")

        stop_event = asyncio.Event()
        latency_task = asyncio.create_task(measure_latency(stop_event))

        await asyncio.sleep(0.1)

        physics_params = {"vibe_score": 0.8, "emotional_tone": "WAKING"}
        text = "test intent"

        start_time = time.perf_counter()
        await asyncio.to_thread(vault.commit_change, physics_params, text)
        end_time = time.perf_counter()

        print(f"await to_thread(commit_change) took {end_time - start_time:.4f}s")

        stop_event.set()
        max_latency = await latency_task
        print(f"Max event loop latency: {max_latency:.4f}s")
        return max_latency

async def main():
    m1 = await benchmark_blocking()
    m2 = await benchmark_non_blocking()

    print(f"\nSummary:")
    print(f"Blocking Max Latency: {m1:.4f}s")
    print(f"Non-blocking Max Latency: {m2:.4f}s")
    print(f"Improvement in event loop responsiveness: {m1 - m2:.4f}s")

if __name__ == "__main__":
    asyncio.run(main())
