import random
import asyncio
from aether_bus import AetherBus
from identity import ZoIdentity
from memory.vault import Vault


class IntentProcessor:
    def __init__(self, bus: AetherBus):
        self.bus = bus
        self.identity = ZoIdentity(role="INTENT_CORE")
        self.vault = Vault()

    async def process_voice_input(self, text_input=""):
        """
        Simulate analyzing voice input and deciding Path A or Path B.
        """
        # Store raw input as a potential gem? Or only realized intent?
        # Let's store successful manifestations.

        # Simulate Processing Delay (MANANA state)
        await asyncio.sleep(2.0)

        # Decide Path (50/50 for simulation)
        is_ambiguous = random.random() > 0.5

        if is_ambiguous:
            # Path B: Ritual of Truth
            await self._trigger_path_b(text_input or "DELETE SECTOR 7?")
        else:
            # Path A: Direct Manifestation
            # We treat this as a "Resonated Intent" and store/update it
            await self._crystallize_intent(text_input or "Unknown Command")
            await self._trigger_path_a()

    async def confirm_intent(self):
        """
        Called when user confirms the Glyph (Path B success).
        """
        # Crystallize the confirmed truth
        await self._crystallize_intent(
            "Confirmed Glyph Intent"
        )  # In real app, pass the text ID

        # Transition to Manifestation
        await self._trigger_path_a()

    async def _crystallize_intent(self, text):
        """
        Store or update the intent in the Vault.
        """
        # In a real system, we'd query for semantic similarity first.
        # Here we just store it as a new gem for simulation.
        # The vault.store_gem call is now asynchronous and handles its own threading.
        await self.vault.store_gem(text, {"source": "voice", "confidence": 1.0})

    async def _trigger_path_b(self, text):
        payload = {
            "type": "VERIFY",
            "text": text,
            "vibe_state": {"mood": "WARNING", "energy_level": 0.8, "urgency": 0.5},
        }
        await self.bus.publish(
            "intent_verify", payload, self.identity.get_identity_header()
        )

    async def _trigger_path_a(self):
        # Generate random "Manifestation" parameters
        mood = random.choice(["FOCUSED", "WAKING", "CALM"])
        primary = "#00FFFF"
        secondary = "#FF00FF"

        if mood == "CALM":
            primary = "#00FF00"
            secondary = "#0000FF"

        payload = {
            "type": "MANIFEST",
            "vibe_state": {
                "mood": mood,
                "energy_level": random.uniform(0.5, 0.9),
                "urgency": 0.1,
            },
            "render_params": {
                "geometry": "FLUID_ORB",
                "chroma_primary": primary,
                "chroma_secondary": secondary,
                "pulse_frequency": 1.0,
                "bloom_factor": 0.8,
            },
        }
        await self.bus.publish(
            "intent_manifest", payload, self.identity.get_identity_header()
        )
