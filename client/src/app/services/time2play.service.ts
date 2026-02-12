/**
 * Time2Play Service
 * Handles HLTB API calls
 */
import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface GameTimeData {
    success: boolean;
    game: string;
    times?: {
        main_story: number | null;
        main_extras: number | null;
        completionist: number | null;
    };
    worth?: {
        verdict: string;
        emoji: string;
        cost_per_hour: number;
        total_hours: number;
        price: number;
        reason: string;
    };
    message?: string;
    reasoning?: string[];
}

export interface BacklogData {
    success: boolean;
    total_games: number;
    found_games: number;
    games: Array<{
        game: string;
        main_story: number | null;
        main_extras: number | null;
        completionist: number | null;
    }>;
    totals: {
        main_story: number;
        main_extras: number;
        completionist: number;
    };
    time_estimates: {
        casual_2h_per_day: number | null;
        moderate_4h_per_day: number | null;
        hardcore_8h_per_day: number | null;
    };
    reasoning: string[];
}

export interface MarathonData {
    success: boolean;
    game: string;
    hours_per_day: number;
    estimates: {
        main_story_days?: number;
        main_extras_days?: number;
        completionist_days?: number;
    };
    message?: string;
    reasoning: string[];
}

@Injectable({
    providedIn: 'root'
})
export class Time2PlayService {
    private apiUrl = 'http://localhost:8000/api/hltb';

    // Signals for reactive state
    isLoading = signal(false);
    currentGame = signal<GameTimeData | null>(null);
    backlogData = signal<BacklogData | null>(null);
    marathonData = signal<MarathonData | null>(null);
    error = signal<string | null>(null);

    constructor(private http: HttpClient) { }

    async searchGame(gameName: string): Promise<GameTimeData> {
        this.isLoading.set(true);
        this.error.set(null);

        try {
            const result = await firstValueFrom<GameTimeData>(
                this.http.post<GameTimeData>(`${this.apiUrl}/game`, { game_name: gameName })
            );

            this.currentGame.set(result);
            return result;
        } catch (err: any) {
            const errorMsg = err.error?.message || 'Failed to fetch game data';
            this.error.set(errorMsg);
            throw err;
        } finally {
            this.isLoading.set(false);
        }
    }

    async calculateBacklog(games: string[]): Promise<BacklogData> {
        this.isLoading.set(true);
        this.error.set(null);

        try {
            const result = await firstValueFrom<BacklogData>(
                this.http.post<BacklogData>(`${this.apiUrl}/backlog`, { games })
            );

            this.backlogData.set(result);
            return result;
        } catch (err: any) {
            const errorMsg = err.error?.message || 'Failed to calculate backlog';
            this.error.set(errorMsg);
            throw err;
        } finally {
            this.isLoading.set(false);
        }
    }

    async calculateMarathon(gameName: string, hoursPerDay: number): Promise<MarathonData> {
        this.isLoading.set(true);
        this.error.set(null);

        try {
            const result = await firstValueFrom<MarathonData>(
                this.http.post<MarathonData>(`${this.apiUrl}/marathon`, {
                    game_name: gameName,
                    hours_per_day: hoursPerDay
                })
            );

            this.marathonData.set(result);
            return result;
        } catch (err: any) {
            const errorMsg = err.error?.message || 'Failed to calculate marathon mode';
            this.error.set(errorMsg);
            throw err;
        } finally {
            this.isLoading.set(false);
        }
    }

    clearData() {
        this.currentGame.set(null);
        this.backlogData.set(null);
        this.marathonData.set(null);
        this.error.set(null);
    }
}
