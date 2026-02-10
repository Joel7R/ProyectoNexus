/**
 * Event Service
 * Manages gaming event data
 */
import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface GameEvent {
    id: string;
    name: string;
    category: string;
    estimated_date: string;
    countdown_seconds: number;
    is_live: boolean;
    source_url?: string;
}

export interface Rumor {
    title: string;
    confidence: 'probable' | 'possible' | 'dream';
    source: string;
    url: string;
}

@Injectable({
    providedIn: 'root'
})
export class EventService {
    private http = inject(HttpClient);
    private apiUrl = 'http://localhost:8000/api/events';

    events = signal<GameEvent[]>([]);
    rumors = signal<Rumor[]>([]);
    isLoading = signal(false);
    error = signal<string | null>(null);

    async loadUpcomingEvents(hours: number = 48) {
        this.isLoading.set(true);
        this.error.set(null);

        try {
            const response: any = await this.http.get(`${this.apiUrl}/upcoming?hours=${hours}`).toPromise();

            if (response.success) {
                this.events.set(response.events);
            } else {
                this.error.set('Failed to load events');
            }
        } catch (err: any) {
            this.error.set(err.message || 'Error loading events');
        } finally {
            this.isLoading.set(false);
        }
    }

    async loadRumors(eventId: string) {
        try {
            const response: any = await this.http.post(`${this.apiUrl}/rumors`, { event_id: eventId }).toPromise();

            if (response.success) {
                this.rumors.set(response.rumors);
            }
        } catch (err) {
            console.error('Error loading rumors:', err);
        }
    }

    formatCountdown(seconds: number): string {
        if (seconds <= 0) return 'LIVE NOW';

        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);

        if (days > 0) {
            return `${days}d ${hours}h ${minutes}m`;
        } else if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else {
            return `${minutes}m`;
        }
    }
}
