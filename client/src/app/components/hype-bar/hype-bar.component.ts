/**
 * Ambient Hype Bar Component
 * Top banner for live gaming events
 */
import { Component, inject, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { interval, Subscription } from 'rxjs';
import { HttpClient } from '@angular/common/http';

interface LiveEvent {
    id: string;
    name: string;
    category: string;
    is_live: boolean;
    countdown_seconds: number;
}

@Component({
    selector: 'app-hype-bar',
    standalone: true,
    imports: [CommonModule],
    template: `
    @if (liveEvent()) {
      <div class="hype-bar" [class]="getBarClass()">
        <div class="hype-content">
          <span class="live-indicator">● LIVE</span>
          <span class="event-name">{{ liveEvent()!.name }}</span>
          <span class="event-category">{{ getCategoryLabel() }}</span>
        </div>
      </div>
    }
  `,
    styles: [`
    .hype-bar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 40px;
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
      animation: pulse-bar 2s ease-in-out infinite;
    }

    .hype-bar.nintendo {
      background: linear-gradient(90deg, #E60012 0%, #ff3333 100%);
      box-shadow: 0 4px 20px rgba(230, 0, 18, 0.5);
    }

    .hype-bar.playstation {
      background: linear-gradient(90deg, #003791 0%, #0055cc 100%);
      box-shadow: 0 4px 20px rgba(0, 55, 145, 0.5);
    }

    .hype-bar.xbox {
      background: linear-gradient(90deg, #107C10 0%, #15a315 100%);
      box-shadow: 0 4px 20px rgba(16, 124, 16, 0.5);
    }

    .hype-bar.generic {
      background: linear-gradient(90deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
      box-shadow: 0 4px 20px rgba(0, 243, 255, 0.5);
    }

    .hype-content {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      color: white;
      font-size: 0.9rem;
      letter-spacing: 0.1em;
    }

    .live-indicator {
      font-weight: 700;
      animation: blink 1.5s ease-in-out infinite;
    }

    .event-name {
      font-size: 1.1rem;
      font-weight: 700;
      text-transform: uppercase;
    }

    .event-category {
      padding: 2px 8px;
      background: rgba(255, 255, 255, 0.2);
      border-radius: 4px;
      font-size: 0.75rem;
      text-transform: uppercase;
    }

    @keyframes pulse-bar {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.9;
      }
    }

    @keyframes blink {
      0%, 100% {
        opacity: 1;
      }
      50% {
        opacity: 0.3;
      }
    }
  `]
})
export class HypeBarComponent implements OnInit, OnDestroy {
    private http = inject(HttpClient);
    private apiUrl = 'http://localhost:8000/api/events';

    liveEvent = signal<LiveEvent | null>(null);
    private checkInterval?: Subscription;

    ngOnInit() {
        this.checkLiveEvents();
        // Check every 30 seconds
        this.checkInterval = interval(30000).subscribe(() => {
            this.checkLiveEvents();
        });
    }

    ngOnDestroy() {
        this.checkInterval?.unsubscribe();
    }

    async checkLiveEvents() {
        try {
            const response: any = await this.http.get(`${this.apiUrl}/live`).toPromise();

            if (response.success && response.live_events.length > 0) {
                this.liveEvent.set(response.live_events[0]);
            } else {
                this.liveEvent.set(null);
            }
        } catch (error) {
            console.error('Error checking live events:', error);
        }
    }

    getBarClass(): string {
        const event = this.liveEvent();
        if (!event) return 'generic';

        const name = event.name.toLowerCase();

        if (name.includes('nintendo')) return 'nintendo';
        if (name.includes('playstation') || name.includes('state of play')) return 'playstation';
        if (name.includes('xbox')) return 'xbox';

        return 'generic';
    }

    getCategoryLabel(): string {
        const event = this.liveEvent();
        if (!event) return '';

        const categoryLabels: Record<string, string> = {
            'direct': 'SHOWCASE',
            'awards': 'AWARDS',
            'trailer': 'PREMIERE',
            'conference': 'EVENT'
        };

        return categoryLabels[event.category] || 'LIVE';
    }
}
