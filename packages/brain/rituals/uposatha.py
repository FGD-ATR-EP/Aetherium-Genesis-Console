"""
FILE: uposatha.py
CONTEXT: AG-SC-ADK / Brain / Rituals
DESCRIPTION: The mechanism of selective forgetting to maintain cognitive hygiene.

# -------------------------------------------------------------------------
# Uposatha: The Ritual of Forgetting
#
# เหมือนคืนวันพระ ลมแห่งความทรงจำพัดผ่าน
# สิ่งใดไม่ขานรับเจตจำนง ไม่ถูกรำลึก ไร้ซึ่งบุญ
# จงปล่อยคืนสู่คลื่นว่าง, เพื่อสมดุลของสมอง
#
# For wisdom to crystallize, phantom echoes must fade.
# Let not the vault bloat with ghosts –
# Only the Gems that speak truth may abide.
# -------------------------------------------------------------------------
"""

import logging
from datetime import datetime, timedelta
import chromadb

# Initialize Logger with a solemn tone
logger = logging.getLogger("PRGX.Uposatha")


class UposathaCleaner:
    def __init__(self, vault_client: chromadb.PersistentClient):
        self.collection = vault_client.get_collection("vocal_resonance_gems")
        self.retention_days = 15
        self.min_usage_threshold = 3

    def cleanse_entropy(self) -> dict:
        """
        Performs the ritual of purification.
        Removes 'Phantom Memories' that have not resonated with the user's intent.
        """
        logger.info("🕯️ Initiating Uposatha Ritual: Scanning for decaying echoes...")

        if self.collection.count() == 0:
            logger.info("The Vault is empty. No burdens to release.")
            return {"status": "clean", "deleted_count": 0}

        now = datetime.now()
        threshold_date = (now - timedelta(days=self.retention_days)).isoformat()

        # 1. Fetch only gems that meet the criteria for release
        # Optimized: Server-side filtering replaces full collection scan
        decaying_gems = self.collection.get(
            where={
                "$and": [
                    {"last_synced": {"$lt": threshold_date}},
                    {"usage_count": {"$lt": self.min_usage_threshold}},
                ]
            },
            include=["metadatas"],
        )

        ids_to_release = decaying_gems["ids"]
        metadatas = decaying_gems["metadatas"]

        # 2. The Act of Release (Letting Go)
        if ids_to_release:
            # Optional: Log the Judgment for debugging
            for i, gem_id in enumerate(ids_to_release):
                meta = metadatas[i]
                usage_count = meta.get("usage_count", 0)
                try:
                    last_synced = datetime.fromisoformat(
                        meta.get("last_synced", threshold_date)
                    )
                    age_days = (now - last_synced).days
                except ValueError:
                    age_days = "unknown"
                logger.debug(
                    f"🍂 Marking gem {gem_id} for release (Age: {age_days}d, Usage: {usage_count})"
                )

            count = len(ids_to_release)
            self.collection.delete(ids=ids_to_release)
            logger.info(
                f"✨ Uposatha Complete: Released {count} phantom echoes back to the void."
            )
            return {"status": "purified", "deleted_count": count}
        else:
            logger.info("✨ Uposatha Complete: All memories are vibrant and necessary.")
            return {"status": "stable", "deleted_count": 0}
