import time
import math
import random
import asyncio
from identity import ZoIdentity
from aether_bus import AetherBus

class MockBioDriver:
    def __init__(self, bus: AetherBus):
        self.bus = bus
        self.identity = ZoIdentity(role="BIO_DRIVER")
        self.start_time = time.time()
        self.base_heart_rate = 75.0
        self.base_temp = 36.6
        self.running = False

    async def start_loop(self):
        self.running = True
        print("BioDriver Loop Started")
        identity_header = self.identity.get_identity_header()
        while self.running:
            vitals = self._generate_vitals()
            payload = self._construct_payload(vitals)

            # Publish to AetherBus
            await self.bus.publish("render_light", payload, identity_header)

            # 10Hz update
            await asyncio.sleep(0.1)

    def _generate_vitals(self):
        now = time.time()
        elapsed = now - self.start_time

        hr_variation = 10.0 * math.sin(elapsed * 0.5)
        hr_noise = random.uniform(-2.0, 2.0)
        heart_rate = self.base_heart_rate + hr_variation + hr_noise

        temp_variation = 0.2 * math.sin(elapsed * 0.05)
        body_temp = self.base_temp + temp_variation

        energy_level = 0.5 + 0.4 * math.sin(elapsed * 0.2 + 1.0)

        mood = "IDLE"
        if energy_level > 0.8:
            mood = "FOCUSED"
        elif energy_level < 0.2:
            mood = "WARNING"
        else:
            mood = "WAKING"

        return {
            "timestamp": now,
            "heart_rate": round(heart_rate, 1),
            "body_temperature": round(body_temp, 2),
            "energy_level": round(energy_level, 3),
            "mood": mood,
            "urgency": round(abs(hr_variation) / 10.0, 2)
        }

    def _construct_payload(self, vitals):
        # Color Logic based on Mood
        primary_color = "#00FFFF" # Cyan
        secondary_color = "#FF00FF" # Magenta

        if vitals["mood"] == "WARNING":
            primary_color = "#FF0000"
            secondary_color = "#FFA500"
        elif vitals["mood"] == "FOCUSED":
            primary_color = "#FFFFFF"
            secondary_color = "#0000FF"

        return {
            "vibe_state": {
                "mood": vitals["mood"],
                "energy_level": vitals["energy_level"],
                "urgency": vitals["urgency"]
            },
            "render_params": {
                "geometry": "FLUID_ORB",
                "chroma_primary": primary_color,
                "chroma_secondary": secondary_color,
                "pulse_frequency": vitals["heart_rate"] / 60.0,
                "bloom_factor": 0.5 + (vitals["energy_level"] * 0.5)
            }
        }
