import { PhysicsParams } from '../types/intent';

export class AetherBusClient {
    private ws: WebSocket;
    private messageHandler: ((payload: PhysicsParams) => void) | null = null;

    constructor(url: string) {
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
            console.log('Connected to AetherBus');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // Validate MCP & PhysicsParams (support both direct and tools/ prefixed methods)
                const isShaderIntentMethod =
                    data.method === "ui:shader_intent" || data.method === "tools/ui:shader_intent";

                if (data.jsonrpc === "2.0" && isShaderIntentMethod && data.params) {
                    const physics = data.params.arguments as PhysicsParams;
                    if (this.messageHandler) {
                        this.messageHandler(physics);
                    }
                }
            } catch (e) {
                console.error('Failed to parse PhysicsParams:', e);
            }
        };

        this.ws.onclose = () => {
            console.log('Disconnected from AetherBus');
        };
    }

    public onMessage(handler: (payload: PhysicsParams) => void) {
        this.messageHandler = handler;
    }

    public send(message: string) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        }
    }

    public close() {
        this.ws.close();
    }
}
