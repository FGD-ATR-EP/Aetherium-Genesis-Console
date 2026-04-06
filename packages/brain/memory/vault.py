import chromadb
from chromadb.config import Settings
import logging
import os
import time
import hashlib
from datetime import datetime
import asyncio

logger = logging.getLogger("PRGX.Vault")

class Vault:
    def __init__(self, persist_path="vault_db"):
        # Use pysqlite3-binary to ensure SQLite version compatibility
        try:
            __import__('pysqlite3')
            import sys
            sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
        except ImportError:
            pass

        self.persist_path = persist_path
        self.client = chromadb.PersistentClient(path=self.persist_path)

        # Initialize Collections
        self.gems = self.client.get_or_create_collection("vocal_resonance_gems")

    def _embed_text(self, text, dimensions=384):
        """
        Build a small deterministic embedding locally.
        This avoids online model downloads in constrained environments.
        """
        seed = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        while len(vector) < dimensions:
            vector.extend([byte / 255.0 for byte in seed])
            seed = hashlib.sha256(seed).digest()
        return vector[:dimensions]

    async def store_gem(self, text, metadata):
        """
        Store a realized intent as a 'Gem'.
        """
        gem_id = metadata.get("id", str(time.time()))

        # Add basic metadata if missing
        metadata.setdefault("usage_count", 1)
        metadata.setdefault("last_synced", datetime.now().isoformat())

        await asyncio.to_thread(
            self.gems.upsert,
            documents=[text],
            metadatas=[metadata],
            embeddings=[self._embed_text(text)],
            ids=[gem_id]
        )
        logger.info(f"💎 Stored Gem: {text[:20]}... (ID: {gem_id})")

    async def update_resonance(self, gem_id):
        """
        Increment usage count (Resonance) for a gem.
        """
        try:
            existing = await asyncio.to_thread(
                self.gems.get,
                ids=[gem_id],
                include=["metadatas"]
            )
            if existing and existing['metadatas']:
                meta = existing['metadatas'][0]
                meta['usage_count'] = meta.get('usage_count', 0) + 1
                meta['last_synced'] = datetime.now().isoformat()

                await asyncio.to_thread(
                    self.gems.update,
                    ids=[gem_id],
                    metadatas=[meta]
                )
                logger.debug(f"✨ Resonance amplified for Gem {gem_id}")
        except Exception as e:
            logger.error(f"Failed to update resonance: {e}")
