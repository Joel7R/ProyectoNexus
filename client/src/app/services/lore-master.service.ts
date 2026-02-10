/**
 * Lore Master Service
 * Handles game lore and character relationship API calls
 */
import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface LoreData {
    success: boolean;
    game: string;
    summary: string;
    spoiler_level: string;
    key_events: string[];
    spoiler_warnings: string[];
    sources?: Array<{ title: string; url: string }>;
    reasoning: string[];
    message?: string;
}

export interface CharacterData {
    name: string;
    role: string;
    relationships: string[];
}

export interface CharacterMapData {
    success: boolean;
    game: string;
    characters: CharacterData[];
    mermaid_graph: string;
    reasoning: string[];
    message?: string;
}

@Injectable({
    providedIn: 'root'
})
export class LoreMasterService {
    private apiUrl = 'http://localhost:8000/api/lore';

    isLoading = signal(false);
    currentLore = signal<LoreData | null>(null);
    characterMap = signal<CharacterMapData | null>(null);
    error = signal<string | null>(null);

    constructor(private http: HttpClient) { }

    async getLore(gameName: string, spoilerLevel: string = 'light'): Promise<LoreData> {
        this.isLoading.set(true);
        this.error.set(null);

        try {
            const result = await firstValueFrom(
                this.http.post<LoreData>(`${this.apiUrl}/story`, {
                    game_name: gameName,
                    spoiler_level: spoilerLevel
                })
            );

            this.currentLore.set(result);
            return result;
        } catch (err: any) {
            const errorMsg = err.error?.message || 'Failed to fetch lore';
            this.error.set(errorMsg);
            throw err;
        } finally {
            this.isLoading.set(false);
        }
    }

    async getCharacterMap(gameName: string): Promise<CharacterMapData> {
        this.isLoading.set(true);
        this.error.set(null);

        try {
            const result = await firstValueFrom(
                this.http.post<CharacterMapData>(`${this.apiUrl}/characters`, {
                    game_name: gameName
                })
            );

            this.characterMap.set(result);
            return result;
        } catch (err: any) {
            const errorMsg = err.error?.message || 'Failed to fetch character map';
            this.error.set(errorMsg);
            throw err;
        } finally {
            this.isLoading.set(false);
        }
    }

    clearData() {
        this.currentLore.set(null);
        this.characterMap.set(null);
        this.error.set(null);
    }
}
