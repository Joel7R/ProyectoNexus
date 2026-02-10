/**
 * Event Hub Component
 * Displays upcoming gaming events with countdowns
 */
import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EventService, GameEvent, Rumor } from '../../services/event.service';

@Component({
    selector: 'app-event-hub',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="event-hub">
      <!-- Header -->
      <div class="hub-header">
        <h1 class="hub-title">
          <span class="icon">🎉</span>
          EVENT HUB
        </h1>
        <p class="hub-subtitle">Upcoming Gaming Events & Rumors</p>
      </div>

      <!-- Loading State -->
      @if (service.isLoading()) {
        <div class="loading-state">
          <div class="spinner"></div>
          <p>Scanning for events...</p>
        </div>
      }

      <!-- Error State -->
      @if (service.error()) {
        <div class="error-state">
          <p>⚠️ {{ service.error() }}</p>
        </div>
      }

      <!-- Events Grid -->
      @if (!service.isLoading() && service.events().length > 0) {
        <div class="events-grid">
          @for (event of service.events(); track event.id) {
            <div class="event-card glass-card" (click)="selectEvent(event)">
              <!-- Event Header -->
              <div class="event-header">
                <span class="event-icon">{{ getEventIcon(event.category) }}</span>
                <div class="event-info">
                  <h3 class="event-name">{{ event.name }}</h3>
                  <span class="event-category">{{ event.category }}</span>
                </div>
              </div>

              <!-- Countdown -->
              <div class="countdown-section">
                @if (event.is_live) {
                  <div class="live-badge">
                    <span class="live-dot"></span>
                    LIVE NOW
                  </div>
                } @else {
                  <div class="countdown">
                    <div class="countdown-label">STARTS IN</div>
                    <div class="countdown-time">{{ service.formatCountdown(event.countdown_seconds) }}</div>
                  </div>
                }
              </div>

              <!-- Date -->
              <div class="event-date">
                📅 {{ event.estimated_date }}
              </div>

              <!-- Rumors Badge -->
              @if (selectedEvent() === event.id && service.rumors().length > 0) {
                <div class="rumors-badge">
                  {{ service.rumors().length }} Rumors
                </div>
              }
            </div>
          }
        </div>
      }

      <!-- No Events -->
      @if (!service.isLoading() && service.events().length === 0 && !service.error()) {
        <div class="empty-state">
          <p>📭 No upcoming events found</p>
          <p class="empty-subtitle">Check back later for updates</p>
        </div>
      }

      <!-- Rumor Panel -->
      @if (selectedEvent() && service.rumors().length > 0) {
        <div class="rumor-panel glass-card">
          <div class="panel-header">
            <h2>🔮 Rumors & Leaks</h2>
            <button class="close-btn" (click)="closeRumors()">✕</button>
          </div>

          <div class="rumors-list">
            @for (rumor of service.rumors(); track rumor.title) {
              <div class="rumor-item" [class]="'confidence-' + rumor.confidence">
                <div class="rumor-header">
                  <span class="confidence-badge">{{ rumor.confidence.toUpperCase() }}</span>
                  <span class="rumor-source">{{ rumor.source }}</span>
                </div>
                <p class="rumor-title">{{ rumor.title }}</p>
                <a [href]="rumor.url" target="_blank" class="rumor-link">
                  Read More →
                </a>
              </div>
            }
          </div>
        </div>
      }
    </div>
  `,
    styles: [`
    .event-hub {
      padding: var(--spacing-xl);
      max-width: 1400px;
      margin: 0 auto;
    }

    .hub-header {
      text-align: center;
      margin-bottom: var(--spacing-xl);
    }

    .hub-title {
      font-family: var(--font-display);
      font-size: 3rem;
      color: var(--accent-primary);
      text-shadow: 0 0 20px var(--accent-primary);
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: var(--spacing-md);
    }

    .icon {
      font-size: 3.5rem;
      animation: bounce 2s ease-in-out infinite;
    }

    .hub-subtitle {
      color: var(--text-secondary);
      font-size: 1.1rem;
      margin-top: var(--spacing-sm);
    }

    /* Events Grid */
    .events-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: var(--spacing-lg);
      margin-bottom: var(--spacing-xl);
    }

    .event-card {
      padding: var(--spacing-lg);
      cursor: pointer;
      transition: all 0.3s ease;
      border: 1px solid var(--border-color);
    }

    .event-card:hover {
      transform: translateY(-5px);
      border-color: var(--accent-primary);
      box-shadow: 0 10px 30px rgba(0, 243, 255, 0.3);
    }

    .event-header {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-md);
    }

    .event-icon {
      font-size: 2.5rem;
    }

    .event-info {
      flex: 1;
    }

    .event-name {
      font-family: var(--font-display);
      font-size: 1.3rem;
      color: var(--text-primary);
      margin: 0 0 var(--spacing-xs) 0;
    }

    .event-category {
      display: inline-block;
      padding: 4px 12px;
      background: var(--accent-secondary);
      color: white;
      border-radius: 12px;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    /* Countdown */
    .countdown-section {
      margin: var(--spacing-lg) 0;
      text-align: center;
    }

    .countdown {
      padding: var(--spacing-md);
      background: rgba(0, 243, 255, 0.1);
      border: 2px solid var(--accent-primary);
      border-radius: 12px;
    }

    .countdown-label {
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-bottom: var(--spacing-xs);
      letter-spacing: 0.1em;
    }

    .countdown-time {
      font-family: var(--font-mono);
      font-size: 2rem;
      color: var(--accent-primary);
      font-weight: 700;
      text-shadow: 0 0 15px var(--accent-primary);
    }

    .live-badge {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: var(--spacing-sm);
      padding: var(--spacing-md);
      background: linear-gradient(135deg, #ff0000, #ff6b6b);
      border-radius: 12px;
      font-weight: 700;
      font-size: 1.2rem;
      color: white;
      animation: pulse 2s ease-in-out infinite;
    }

    .live-dot {
      width: 12px;
      height: 12px;
      background: white;
      border-radius: 50%;
      animation: blink 1s ease-in-out infinite;
    }

    .event-date {
      text-align: center;
      color: var(--text-secondary);
      font-size: 0.9rem;
      margin-top: var(--spacing-md);
    }

    .rumors-badge {
      margin-top: var(--spacing-md);
      padding: var(--spacing-sm);
      background: var(--accent-secondary);
      color: white;
      text-align: center;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 600;
    }

    /* Rumor Panel */
    .rumor-panel {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 90%;
      max-width: 700px;
      max-height: 80vh;
      overflow-y: auto;
      padding: var(--spacing-xl);
      z-index: 1000;
      border: 2px solid var(--accent-primary);
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--spacing-lg);
    }

    .panel-header h2 {
      font-family: var(--font-display);
      color: var(--accent-primary);
      margin: 0;
    }

    .close-btn {
      background: none;
      border: none;
      color: var(--text-primary);
      font-size: 1.5rem;
      cursor: pointer;
      padding: var(--spacing-sm);
      transition: color 0.3s ease;
    }

    .close-btn:hover {
      color: var(--accent-primary);
    }

    .rumors-list {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-md);
    }

    .rumor-item {
      padding: var(--spacing-md);
      border-left: 4px solid;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 8px;
    }

    .rumor-item.confidence-probable {
      border-color: #39ff14;
    }

    .rumor-item.confidence-possible {
      border-color: #ffcc00;
    }

    .rumor-item.confidence-dream {
      border-color: #bc13fe;
    }

    .rumor-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--spacing-sm);
    }

    .confidence-badge {
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.05em;
    }

    .confidence-probable .confidence-badge {
      background: #39ff14;
      color: black;
    }

    .confidence-possible .confidence-badge {
      background: #ffcc00;
      color: black;
    }

    .confidence-dream .confidence-badge {
      background: #bc13fe;
      color: white;
    }

    .rumor-source {
      font-size: 0.85rem;
      color: var(--text-secondary);
    }

    .rumor-title {
      color: var(--text-primary);
      margin: var(--spacing-sm) 0;
      line-height: 1.5;
    }

    .rumor-link {
      color: var(--accent-primary);
      text-decoration: none;
      font-size: 0.9rem;
      transition: color 0.3s ease;
    }

    .rumor-link:hover {
      color: var(--accent-secondary);
    }

    /* States */
    .loading-state,
    .error-state,
    .empty-state {
      text-align: center;
      padding: var(--spacing-xxl);
      color: var(--text-secondary);
    }

    .spinner {
      width: 50px;
      height: 50px;
      border: 4px solid rgba(0, 243, 255, 0.2);
      border-top-color: var(--accent-primary);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto var(--spacing-md);
    }

    .empty-subtitle {
      font-size: 0.9rem;
      margin-top: var(--spacing-sm);
    }

    /* Animations */
    @keyframes bounce {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.8; }
    }

    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.3; }
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `]
})
export class EventHubComponent implements OnInit {
    service = inject(EventService);
    selectedEvent = signal<string | null>(null);

    ngOnInit() {
        this.service.loadUpcomingEvents();
    }

    selectEvent(event: GameEvent) {
        this.selectedEvent.set(event.id);
        this.service.loadRumors(event.id);
    }

    closeRumors() {
        this.selectedEvent.set(null);
    }

    getEventIcon(category: string): string {
        const icons: Record<string, string> = {
            'direct': '🎮',
            'awards': '🏆',
            'trailer': '🎬',
            'conference': '📢'
        };
        return icons[category] || '🎉';
    }
}
