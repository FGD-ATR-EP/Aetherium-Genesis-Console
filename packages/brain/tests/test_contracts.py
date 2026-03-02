from pathlib import Path
import sys
import asyncio
import json

sys.path.append(str(Path(__file__).resolve().parents[1]))

from aether_bus import AetherBus
from identity import PRGX1_Sentry


def test_aether_bus_publish_builds_mcp_payload_contract():
    bus = AetherBus()
    received = []

    async def subscriber(message_text):
        received.append(json.loads(message_text))

    bus.subscribe(subscriber)
    payload = {"intent_vector": "LIGHT", "vibe_score": 0.4}
    identity_header = {"source_id": "unit-test"}

    asyncio.run(bus.publish("ui:shader_intent", payload, identity_header))

    assert len(received) == 1
    message = received[0]
    assert message["jsonrpc"] == "2.0"
    assert message["method"] == "tools/ui:shader_intent"
    assert message["params"]["name"] == "ui:shader_intent"
    assert message["params"]["arguments"] == payload
    assert message["params"]["_identity"] == identity_header


def test_prgx1_sentry_guardrails():
    valid, reason = PRGX1_Sentry.inspect({"intent_vector": "", "vibe_score": 0.0})
    assert (valid, reason) == (False, "MISSING_VECTOR")

    valid, reason = PRGX1_Sentry.inspect({"intent_vector": "RUN", "vibe_score": -0.95})
    assert (valid, reason) == (False, "PARAJIKA")

    valid, reason = PRGX1_Sentry.inspect({"intent_vector": "RUN", "vibe_score": 0.2})
    assert (valid, reason) == (True, "CLEAN")
