import time
import sys
from unittest.mock import MagicMock
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.config'] = MagicMock()

from datetime import datetime, timedelta
from memory.vault import Vault
from rituals.uposatha import UposathaCleaner
import asyncio

async def verify_uposatha():
    print("Initializing Vault...")
    vault = Vault(persist_path="test_vault")

    # 1. Create Gems (Memories)
    # Gem A: Vibrant (New, Used often)
    await vault.store_gem("I am vibrant", {"id": "gem_vibrant", "usage_count": 10, "last_synced": datetime.now().isoformat()})

    # Gem B: Phantom (Old, Rare)
    old_date = (datetime.now() - timedelta(days=20)).isoformat()
    await vault.store_gem("I am a ghost", {"id": "gem_phantom", "usage_count": 1, "last_synced": old_date})

    # Gem C: Sleeping (Old, but used enough) -> Should keep?
    # Threshold is usage < 3. So if usage >= 3, it stays.
    await vault.store_gem("I am sleeping giant", {"id": "gem_sleeping", "usage_count": 5, "last_synced": old_date})

    print("Gems stored.")

    # 2. Run Ritual
    cleaner = UposathaCleaner(vault.client)
    print("Invoking Uposatha...")
    result = await cleaner.cleanse_entropy()
    print(f"Ritual Result: {result}")

    # 3. Verify Survival
    remaining = vault.gems.get()
    ids = remaining['ids']
    print(f"Remaining Gems: {ids}")

    if "gem_phantom" not in ids:
        print("SUCCESS: Phantom Echo released.")
    else:
        print("FAIL: Phantom Echo remains.")

    if "gem_vibrant" in ids and "gem_sleeping" in ids:
        print("SUCCESS: Noble Gems preserved.")
    else:
        print("FAIL: Noble Gems lost.")

if __name__ == "__main__":
    asyncio.run(verify_uposatha())
