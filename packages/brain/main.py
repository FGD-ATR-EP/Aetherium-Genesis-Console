import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from aether_bus import AetherBus
from sati import SATI
from identity import PRGX_Triad
from memory.akashic_vault import AkashicVault
from rituals.startup_ritual import perform_startup_ritual

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Systems
bus = AetherBus()
sati = SATI()
prgx = PRGX_Triad()
vault = AkashicVault()

@app.on_event("startup")
async def startup_event():
    success = await perform_startup_ritual()
    if not success:
        print("FATAL: Startup Ritual Failed")
        exit(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to AetherBus Gateway")

    async def send_to_client(message: str):
        await websocket.send_text(message)

    bus.subscribe(send_to_client)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                method = message.get("method")

                if method == "input/voice_data":
                    print("Brain: Received Voice Data.")
                    params = message.get("params", {})
                    text = params.get("text", "")

                    # 1. SATI Observation
                    # Mock Vibe Score extraction (In real system, this comes from Audio Model)
                    vibe_score = 0.8 # Mock Positive
                    tone = "WAKING"
                    current_vibe = sati.observe(text, vibe_score, tone)
                    intent_vector = sati.encode_intent(text)

                    # 2. PRGX1 Sentry Check
                    valid, reason = prgx.sentry.inspect({"intent_vector": intent_vector, "vibe_score": vibe_score})
                    if not valid:
                        print(f"PRGX1 Blocked: {reason}")
                        # Trigger Diplomat?
                        continue

                    # 3. PRGX2 Alchemist Transmutation (RSI Loop)
                    physics_params = prgx.alchemist.transmute(current_vibe, intent_vector)

                    # 4. Akashic Record Commit
                    vault.commit_change(physics_params, text)

                    # 5. GenUI Manifestation (Publish)
                    await bus.publish("ui:shader_intent", physics_params, {"source": "brain"})

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        print("Client disconnected")
        if send_to_client in bus.subscribers:
            bus.subscribers.remove(send_to_client)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
