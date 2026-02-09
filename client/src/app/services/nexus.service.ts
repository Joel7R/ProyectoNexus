/**
 * Nexus Service - SSE connection to Python backend
 * Handles streaming chat responses and artifacts
 * 
 * Features:
 * - 5 minute timeout for slow Ollama responses
 * - Keepalive status updates showing elapsed time
 * - Cancel request functionality
 * - Better error messages
 */
import { Injectable, signal, computed, OnDestroy } from '@angular/core';
import { environment } from '../../environments/environment';

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'thinking';
    content: string;
    timestamp: Date;
    artifact?: Artifact;
    sources?: Source[];
}

export interface Source {
    title: string;
    url: string;
}

export interface Artifact {
    type: 'table' | 'build' | 'guide' | 'empty' | 'error';
    display: string;
    timestamp: string;
    [key: string]: any;
}

export interface StreamEvent {
    type: 'thinking' | 'response' | 'error' | 'done';
    content?: string;
    artifact?: Artifact;
    sources?: Source[];
}

// Timeout configuration (10 minutes for Ollama which can be slow)
const REQUEST_TIMEOUT_MS = 600000; // 10 minutes
const KEEPALIVE_INTERVAL_MS = 3000; // Update status every 3 seconds

@Injectable({
    providedIn: 'root'
})
export class NexusService implements OnDestroy {
    private readonly apiUrl = environment.apiUrl;
    private sessionId = this.generateSessionId();
    private abortController: AbortController | null = null;
    private keepaliveInterval: ReturnType<typeof setInterval> | null = null;
    private startTime: number = 0;

    // Reactive state with signals
    private _messages = signal<ChatMessage[]>([]);
    private _currentArtifact = signal<Artifact | null>(null);
    private _isLoading = signal(false);
    private _thinkingStatus = signal<string>('');
    private _elapsedTime = signal<number>(0);

    // Public computed values
    readonly messages = this._messages.asReadonly();
    readonly currentArtifact = this._currentArtifact.asReadonly();
    readonly isLoading = this._isLoading.asReadonly();
    readonly thinkingStatus = this._thinkingStatus.asReadonly();
    readonly elapsedTime = this._elapsedTime.asReadonly();

    readonly hasArtifact = computed(() => this._currentArtifact() !== null);

    ngOnDestroy(): void {
        this.cleanup();
    }

    /**
     * Send a message and stream the response via SSE
     */
    async sendMessage(content: string): Promise<void> {
        if (!content.trim() || this._isLoading()) return;

        // Cleanup any previous request
        this.cleanup();

        // Add user message
        const userMessage: ChatMessage = {
            id: this.generateId(),
            role: 'user',
            content: content.trim(),
            timestamp: new Date()
        };

        this._messages.update(msgs => [...msgs, userMessage]);
        this._isLoading.set(true);
        this._thinkingStatus.set('Conectando con Gaming Nexus...');
        this.startTime = Date.now();
        this._elapsedTime.set(0);

        // Start keepalive interval to show elapsed time
        this.startKeepalive();

        // Create abort controller for timeout
        this.abortController = new AbortController();
        const timeoutId = setTimeout(() => {
            this.abortController?.abort();
        }, REQUEST_TIMEOUT_MS);

        try {
            const response = await fetch(`${this.apiUrl}/api/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: content.trim(),
                    session_id: this.sessionId
                }),
                signal: this.abortController.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error: ${response.status}`);
            }

            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) {
                throw new Error('No response body');
            }

            let assistantMessage: ChatMessage | null = null;
            let receivedDone = false;

            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    if (!receivedDone && !assistantMessage) {
                        throw new Error('La conexión se cerró inesperadamente antes de recibir una respuesta.');
                    }
                    break;
                }

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    const trimmedLine = line.trim();
                    if (!trimmedLine) continue;

                    if (trimmedLine.startsWith('data: ')) {
                        try {
                            const eventData = trimmedLine.slice(6);
                            if (eventData === '[DONE]') {
                                receivedDone = true;
                                continue;
                            }

                            const event: StreamEvent = JSON.parse(eventData);

                            switch (event.type) {
                                case 'thinking':
                                    this._thinkingStatus.set(event.content || '');
                                    break;

                                case 'response':
                                    assistantMessage = {
                                        id: this.generateId(),
                                        role: 'assistant',
                                        content: event.content || '',
                                        timestamp: new Date(),
                                        artifact: event.artifact,
                                        sources: event.sources
                                    };

                                    this._messages.update(msgs => [...msgs, assistantMessage!]);

                                    if (event.artifact) {
                                        this._currentArtifact.set(event.artifact);
                                    }
                                    break;

                                case 'error':
                                    receivedDone = true; // Consider it handled
                                    this._messages.update(msgs => [...msgs, {
                                        id: this.generateId(),
                                        role: 'assistant',
                                        content: `❌ Error del Agente: ${event.content}`,
                                        timestamp: new Date()
                                    }]);
                                    break;

                                case 'done':
                                    receivedDone = true;
                                    break;
                            }
                        } catch (e) {
                            console.error('Failed to parse SSE event:', e, 'Line:', trimmedLine);
                        }
                    }
                }
            }

        } catch (error: any) {
            console.error('Stream error:', error);

            let errorMessage = '';
            if (error.name === 'AbortError') {
                errorMessage = '⏱️ Timeout: La solicitud tardó demasiado. Ollama puede estar ocupado o el modelo es muy lento. Intenta de nuevo.';
            } else if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
                errorMessage = '🔌 Error de conexión: No se pudo conectar al servidor. Verifica que el backend esté corriendo en http://localhost:8000';
            } else {
                errorMessage = `❌ Error: ${error.message || 'Error desconocido'}. Verifica que el servidor esté corriendo.`;
            }

            this._messages.update(msgs => [...msgs, {
                id: this.generateId(),
                role: 'assistant',
                content: errorMessage,
                timestamp: new Date()
            }]);
        } finally {
            this.cleanup();
            this._isLoading.set(false);
            this._thinkingStatus.set('');
            this._elapsedTime.set(0);
        }
    }

    /**
     * Cancel current request
     */
    cancelRequest(): void {
        if (this.abortController) {
            this.abortController.abort();
            this._messages.update(msgs => [...msgs, {
                id: this.generateId(),
                role: 'assistant',
                content: '🛑 Solicitud cancelada por el usuario.',
                timestamp: new Date()
            }]);
        }
        this.cleanup();
        this._isLoading.set(false);
        this._thinkingStatus.set('');
    }

    /**
     * Clear chat history
     */
    clearHistory(): void {
        this.cleanup();
        this._messages.set([]);
        this._currentArtifact.set(null);
        this._isLoading.set(false);
        this._thinkingStatus.set('');
        this.sessionId = this.generateSessionId();
    }

    /**
     * Close artifact sidebar
     */
    closeArtifact(): void {
        this._currentArtifact.set(null);
    }

    private startKeepalive(): void {
        this.keepaliveInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            this._elapsedTime.set(elapsed);

            const currentStatus = this._thinkingStatus();
            const baseStatus = currentStatus.split(' (')[0] || 'Procesando';

            // Show different messages based on elapsed time
            if (elapsed > 60) {
                this._thinkingStatus.set(`${baseStatus} (${elapsed}s - Ollama procesando, paciencia...)`);
            } else if (elapsed > 30) {
                this._thinkingStatus.set(`${baseStatus} (${elapsed}s)`);
            } else if (elapsed > 10) {
                this._thinkingStatus.set(`${baseStatus} (${elapsed}s)`);
            }
        }, KEEPALIVE_INTERVAL_MS);
    }

    private cleanup(): void {
        if (this.keepaliveInterval) {
            clearInterval(this.keepaliveInterval);
            this.keepaliveInterval = null;
        }
        if (this.abortController) {
            this.abortController = null;
        }
    }

    private generateId(): string {
        return `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    }

    private generateSessionId(): string {
        return `session-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
    }
}
