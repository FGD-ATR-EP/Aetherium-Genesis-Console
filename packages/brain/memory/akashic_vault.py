import logging
import uuid
from datetime import datetime
from memory.vault import Vault

logger = logging.getLogger("Akashic.Vault")

class AkashicVault(Vault):
    """
    Wrapper around the standard Vault (ChromaDB) to support
    Akashic Record integration and 'Commit Rituals'.
    """
    def __init__(self, persist_path="akashic_record"):
        super().__init__(persist_path)

    async def commit_change(self, physics_params, original_text, ritual_tag="normal"):
        """
        Commit a significant change/intent to the Record.
        """
        gem_id = str(uuid.uuid4())

        metadata = {
            "id": gem_id,
            "resolved_intent": original_text,
            "usage_count": 1,
            "last_synced": datetime.now().isoformat(),
            "ritual_tag": ritual_tag,
            "vibe_score": physics_params["vibe_score"],
            "emotional_tone": physics_params["emotional_tone"]
        }

        # Store vector (using the intent vector from params if possible, or text embedding)
        # Here we store text for simplicity of retrieval in this prototype
        await self.store_gem(original_text, metadata)

        logger.info(f"📜 Akashic Record Committed: {gem_id} [{ritual_tag}]")
        return gem_id
