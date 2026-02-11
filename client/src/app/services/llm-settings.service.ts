import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { tap } from 'rxjs/operators';

export interface LLMSettings {
    provider: 'ollama' | 'gemini';
    api_key?: string;
    has_key?: boolean;
    model?: string;
}

@Injectable({
    providedIn: 'root'
})
export class LlmSettingsService {
    private apiUrl = `${environment.apiUrl}/api/settings/llm`;

    // Signals for reactive state
    settings = signal<LLMSettings>({ provider: 'ollama', has_key: false });
    loading = signal<boolean>(false);

    constructor(private http: HttpClient) {
        this.loadSettings();
    }

    loadSettings() {
        this.loading.set(true);
        this.http.get<LLMSettings>(this.apiUrl).subscribe({
            next: (data) => {
                this.settings.set(data);
                this.loading.set(false);
            },
            error: (err) => {
                console.error('Failed to load LLM settings', err);
                this.loading.set(false);
            }
        });
    }

    updateSettings(provider: 'ollama' | 'gemini', apiKey?: string) {
        this.loading.set(true);
        const payload = { provider, api_key: apiKey };

        return this.http.post<{ status: string, settings: LLMSettings }>(this.apiUrl, payload).pipe(
            tap(response => {
                this.settings.set(response.settings);
                this.loading.set(false);
            })
        );
    }
}
