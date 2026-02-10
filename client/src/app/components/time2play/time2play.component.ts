/**
 * Time2Play Component
 * HowLongToBeat-inspired game time estimation with Cyber-Dark aesthetics
 */
import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Time2PlayService, type GameTimeData } from '../../services/time2play.service';

@Component({
    selector: 'app-time2play',
    standalone: true,
    imports: [CommonModule, FormsModule],
    template: `
    <div class="time2play-container">
      <!-- Search Interface -->
      <div class="search-section">
        <div class="search-icon">⏱️</div>
        <h1 class="search-title">TIME2PLAY</h1>
        <p class="search-subtitle">GAME COMPLETION TIME ESTIMATOR</p>
        
        <form (submit)="onSearch($event)" class="search-form">
          <input
            type="text"
            [(ngModel)]="searchQuery"
            name="search"
            class="search-input"
            placeholder="ENTER GAME TITLE..."
            [disabled]="service.isLoading()"
            autocomplete="off"
          />
          <button 
            type="submit" 
            class="search-btn"
            [disabled]="!searchQuery.trim() || service.isLoading()"
          >
            <span>{{ service.isLoading() ? 'SEARCHING...' : 'ANALYZE' }}</span>
          </button>
        </form>
      </div>

      <!-- Error Message -->
      @if (service.error()) {
        <div class="error-banner glass-card">
          ⚠️ {{ service.error() }}
        </div>
      }

      <!-- Game Card -->
      @if (service.currentGame() && service.currentGame()!.success) {
        <div class="game-card glass-card fade-in">
          <div class="game-header">
            <h2 class="game-title">{{ service.currentGame()!.game }}</h2>
            @if (service.currentGame()!.worth) {
              <div class="worth-badge" [class]="getWorthClass(service.currentGame()!.worth!.verdict)">
                <span class="worth-emoji">{{ service.currentGame()!.worth!.emoji }}</span>
                <span class="worth-text">{{ service.currentGame()!.worth!.verdict }}</span>
              </div>
            }
          </div>

          <!-- Time Bars -->
          <div class="time-bars">
            @if (service.currentGame()!.times!.main_story) {
              <div class="time-bar">
                <div class="time-label">
                  <span class="label-text">MAIN STORY</span>
                  <span class="time-value">{{ service.currentGame()!.times!.main_story }}h</span>
                </div>
                <div class="progress-track">
                  <div 
                    class="progress-fill progress-fill--cyan"
                    [style.width.%]="getBarWidth(service.currentGame()!.times!.main_story!, 'main')"
                  ></div>
                </div>
              </div>
            }

            @if (service.currentGame()!.times!.main_extras) {
              <div class="time-bar">
                <div class="time-label">
                  <span class="label-text">MAIN + EXTRAS</span>
                  <span class="time-value">{{ service.currentGame()!.times!.main_extras }}h</span>
                </div>
                <div class="progress-track">
                  <div 
                    class="progress-fill progress-fill--purple"
                    [style.width.%]="getBarWidth(service.currentGame()!.times!.main_extras!, 'extras')"
                  ></div>
                </div>
              </div>
            }

            @if (service.currentGame()!.times!.completionist) {
              <div class="time-bar">
                <div class="time-label">
                  <span class="label-text">COMPLETIONIST</span>
                  <span class="time-value">{{ service.currentGame()!.times!.completionist }}h</span>
                </div>
                <div class="progress-track">
                  <div 
                    class="progress-fill"
                    [style.width.%]="100"
                    [style.background]="getCompletionistGradient(service.currentGame()!.times!.completionist!)"
                  ></div>
                </div>
              </div>
            }
          </div>

          <!-- Worth Analysis -->
          @if (service.currentGame()!.worth) {
            <div class="worth-analysis">
              <div class="worth-detail">
                💰 {{ service.currentGame()!.worth!.reason }}
              </div>
            </div>
          }

          <!-- Marathon Mode Toggle -->
          <div class="marathon-toggle">
            <button 
              class="toggle-btn"
              (click)="toggleMarathonMode()"
            >
              {{ showMarathonMode() ? '▼' : '▶' }} MARATHON MODE
            </button>
          </div>

          <!-- Marathon Mode Calculator -->
          @if (showMarathonMode()) {
            <div class="marathon-section glass-card fade-in">
              <h3 class="marathon-title">MARATHON MODE CALCULATOR</h3>
              <div class="marathon-input">
                <label>Hours per day:</label>
                <input
                  type="number"
                  [(ngModel)]="hoursPerDay"
                  min="0.5"
                  max="24"
                  step="0.5"
                  class="hours-input"
                  (change)="calculateMarathon()"
                />
              </div>

              @if (service.marathonData() && service.marathonData()!.success) {
                <div class="marathon-results">
                  @if (service.marathonData()!.estimates.main_story_days) {
                    <div class="marathon-item">
                      <span class="marathon-label">MAIN STORY:</span>
                      <span class="marathon-days">{{ service.marathonData()!.estimates.main_story_days }} days</span>
                    </div>
                  }
                  @if (service.marathonData()!.estimates.main_extras_days) {
                    <div class="marathon-item">
                      <span class="marathon-label">MAIN+EXTRAS:</span>
                      <span class="marathon-days">{{ service.marathonData()!.estimates.main_extras_days }} days</span>
                    </div>
                  }
                  @if (service.marathonData()!.estimates.completionist_days) {
                    <div class="marathon-item">
                      <span class="marathon-label">COMPLETIONIST:</span>
                      <span class="marathon-days">{{ service.marathonData()!.estimates.completionist_days }} days</span>
                    </div>
                  }
                </div>
              }
            </div>
          }
        </div>
      }

      <!-- Backlog Section -->
      <div class="backlog-section">
        <h3 class="section-title">YOUR BACKLOG</h3>
        <div class="backlog-input">
          <input
            type="text"
            [(ngModel)]="backlogInput"
            placeholder="Add game (press Enter)"
            class="backlog-field"
            (keyup.enter)="addToBacklog()"
          />
        </div>

        @if (backlogGames().length > 0) {
          <div class="backlog-list glass-card">
            @for (game of backlogGames(); track game; let i = $index) {
              <div class="backlog-item">
                <span class="backlog-number">{{ i + 1 }}.</span>
                <span class="backlog-name">{{ game }}</span>
                <button class="remove-btn" (click)="removeFromBacklog(i)">✕</button>
              </div>
            }

            <button class="calculate-btn" (click)="calculateBacklog()">
              CALCULATE TOTAL TIME
            </button>

            @if (service.backlogData() && service.backlogData()!.success) {
              <div class="backlog-totals">
                <div class="total-item">
                  <span class="total-label">TOTAL HOURS:</span>
                  <span class="total-value">{{ service.backlogData()!.totals.completionist }}h</span>
                </div>
                @if (service.backlogData()!.time_estimates.casual_2h_per_day) {
                  <div class="total-item">
                    <span class="total-label">@ 2h/day:</span>
                    <span class="total-value">{{ service.backlogData()!.time_estimates.casual_2h_per_day }} days</span>
                  </div>
                }
                @if (service.backlogData()!.time_estimates.moderate_4h_per_day) {
                  <div class="total-item">
                    <span class="total-label">@ 4h/day:</span>
                    <span class="total-value">{{ service.backlogData()!.time_estimates.moderate_4h_per_day }} days</span>
                  </div>
                }
              </div>
            }
          </div>
        }
      </div>
    </div>
  `,
    styles: [`
    .time2play-container {
      max-width: 1000px;
      margin: 0 auto;
      padding: var(--spacing-lg);
    }

    /* Search Section */
    .search-section {
      text-align: center;
      margin-bottom: var(--spacing-xl);
    }

    .search-icon {
      font-size: 4rem;
      margin-bottom: var(--spacing-md);
      filter: drop-shadow(0 0 20px var(--accent-primary));
      animation: pulse-neon 3s ease-in-out infinite;
    }

    .search-title {
      font-family: var(--font-display);
      font-size: 3rem;
      letter-spacing: 0.2rem;
      color: var(--accent-primary);
      text-shadow: 0 0 20px rgba(0, 243, 255, 0.5);
      margin-bottom: var(--spacing-sm);
    }

    .search-subtitle {
      color: var(--text-secondary);
      font-family: var(--font-mono);
      font-size: 0.9rem;
      margin-bottom: var(--spacing-xl);
      letter-spacing: 0.1em;
    }

    .search-form {
      display: flex;
      gap: var(--spacing-md);
      max-width: 600px;
      margin: 0 auto;
    }

    .search-input {
      flex: 1;
      padding: var(--spacing-md);
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      color: var(--text-primary);
      font-family: var(--font-display);
      font-size: 1rem;
      letter-spacing: 0.05em;
      transition: all 0.3s;

      &:focus {
        outline: none;
        border-color: var(--accent-primary);
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
      }

      &::placeholder {
        color: var(--text-muted);
      }
    }

    .search-btn {
      padding: var(--spacing-md) var(--spacing-xl);
      background: rgba(0, 243, 255, 0.1);
      border: 1px solid var(--accent-primary);
      color: var(--accent-primary);
      font-family: var(--font-display);
      font-size: 0.9rem;
      letter-spacing: 0.1em;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.3s;

      &:hover:not(:disabled) {
        background: var(--accent-primary);
        color: black;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.5);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    /* Game Card */
    .game-card {
      margin-bottom: var(--spacing-xl);
      padding: var(--spacing-lg);
    }

    .game-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--spacing-lg);
      padding-bottom: var(--spacing-md);
      border-bottom: 1px solid var(--glass-border);
    }

    .game-title {
      font-family: var(--font-display);
      font-size: 1.5rem;
      color: var(--accent-primary);
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }

    .worth-badge {
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
      padding: var(--spacing-xs) var(--spacing-md);
      border-radius: var(--radius-md);
      font-family: var(--font-display);
      font-size: 0.8rem;
      letter-spacing: 0.05em;

      &.excellent {
        background: rgba(0, 255, 136, 0.2);
        border: 1px solid var(--accent-success);
        color: var(--accent-success);
      }

      &.good {
        background: rgba(0, 243, 255, 0.2);
        border: 1px solid var(--accent-primary);
        color: var(--accent-primary);
      }

      &.fair {
        background: rgba(255, 204, 0, 0.2);
        border: 1px solid var(--accent-warning);
        color: var(--accent-warning);
      }

      &.expensive {
        background: rgba(255, 0, 85, 0.2);
        border: 1px solid var(--accent-alert);
        color: var(--accent-alert);
      }
    }

    /* Time Bars */
    .time-bars {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-lg);
    }

    .time-bar {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
    }

    .time-label {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .label-text {
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .time-value {
      font-family: 'Orbitron', monospace;
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--accent-primary);
      text-shadow: 0 0 10px currentColor;
      letter-spacing: 0.1em;
    }

    .progress-track {
      height: 12px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: var(--radius-sm);
      overflow: hidden;
      position: relative;
    }

    .progress-fill {
      height: 100%;
      border-radius: var(--radius-sm);
      transition: width 0.5s ease;
      position: relative;

      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
      }

      &--cyan {
        background: linear-gradient(90deg, var(--accent-primary), rgba(0, 243, 255, 0.5));
        box-shadow: 0 0 10px var(--accent-primary);
      }

      &--purple {
        background: linear-gradient(90deg, var(--accent-secondary), rgba(188, 19, 254, 0.5));
        box-shadow: 0 0 10px var(--accent-secondary);
      }
    }

    @keyframes shimmer {
      0% { transform: translateX(-100%); }
      100% { transform: translateX(100%); }
    }

    /* Worth Analysis */
    .worth-analysis {
      padding: var(--spacing-md);
      background: rgba(0, 0, 0, 0.3);
      border-radius: var(--radius-md);
      margin-bottom: var(--spacing-md);
    }

    .worth-detail {
      font-family: var(--font-mono);
      font-size: 0.9rem;
      color: var(--text-secondary);
    }

    /* Marathon Mode */
    .marathon-toggle {
      margin-bottom: var(--spacing-md);
    }

    .toggle-btn {
      width: 100%;
      padding: var(--spacing-md);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--glass-border);
      color: var(--accent-primary);
      font-family: var(--font-display);
      font-size: 0.9rem;
      letter-spacing: 0.1em;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: rgba(0, 243, 255, 0.1);
        border-color: var(--accent-primary);
      }
    }

    .marathon-section {
      padding: var(--spacing-lg);
      margin-top: var(--spacing-md);
    }

    .marathon-title {
      font-family: var(--font-display);
      font-size: 1rem;
      color: var(--accent-secondary);
      margin-bottom: var(--spacing-md);
      letter-spacing: 0.1em;
    }

    .marathon-input {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-lg);

      label {
        font-family: var(--font-mono);
        font-size: 0.9rem;
        color: var(--text-secondary);
      }

      .hours-input {
        width: 100px;
        padding: var(--spacing-sm);
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid var(--glass-border);
        color: var(--text-primary);
        font-family: 'Orbitron', monospace;
        font-size: 1rem;
        border-radius: var(--radius-sm);
        text-align: center;

        &:focus {
          outline: none;
          border-color: var(--accent-primary);
        }
      }
    }

    .marathon-results {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }

    .marathon-item {
      display: flex;
      justify-content: space-between;
      padding: var(--spacing-sm);
      background: rgba(255, 255, 255, 0.03);
      border-radius: var(--radius-sm);
    }

    .marathon-label {
      font-family: var(--font-mono);
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .marathon-days {
      font-family: 'Orbitron', monospace;
      font-size: 1rem;
      color: var(--accent-primary);
      font-weight: 700;
    }

    /* Backlog Section */
    .backlog-section {
      margin-top: var(--spacing-xl);
    }

    .section-title {
      font-family: var(--font-display);
      font-size: 1.25rem;
      color: var(--accent-secondary);
      margin-bottom: var(--spacing-md);
      letter-spacing: 0.1em;
    }

    .backlog-input {
      margin-bottom: var(--spacing-md);
    }

    .backlog-field {
      width: 100%;
      padding: var(--spacing-md);
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      color: var(--text-primary);
      font-family: var(--font-mono);
      font-size: 0.9rem;

      &:focus {
        outline: none;
        border-color: var(--accent-secondary);
        box-shadow: 0 0 15px rgba(188, 19, 254, 0.3);
      }
    }

    .backlog-list {
      padding: var(--spacing-lg);
    }

    .backlog-item {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      padding: var(--spacing-sm);
      margin-bottom: var(--spacing-sm);
      background: rgba(255, 255, 255, 0.03);
      border-radius: var(--radius-sm);
      transition: all 0.2s;

      &:hover {
        background: rgba(255, 255, 255, 0.05);
      }
    }

    .backlog-number {
      font-family: var(--font-mono);
      color: var(--text-muted);
      font-size: 0.8rem;
    }

    .backlog-name {
      flex: 1;
      font-family: var(--font-mono);
      color: var(--text-primary);
    }

    .remove-btn {
      padding: 2px 8px;
      background: rgba(255, 0, 85, 0.2);
      border: 1px solid var(--accent-alert);
      color: var(--accent-alert);
      border-radius: var(--radius-sm);
      cursor: pointer;
      font-size: 0.8rem;
      transition: all 0.2s;

      &:hover {
        background: var(--accent-alert);
        color: black;
      }
    }

    .calculate-btn {
      width: 100%;
      padding: var(--spacing-md);
      margin-top: var(--spacing-md);
      background: rgba(188, 19, 254, 0.1);
      border: 1px solid var(--accent-secondary);
      color: var(--accent-secondary);
      font-family: var(--font-display);
      font-size: 0.9rem;
      letter-spacing: 0.1em;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: var(--accent-secondary);
        color: black;
        box-shadow: 0 0 20px rgba(188, 19, 254, 0.5);
      }
    }

    .backlog-totals {
      margin-top: var(--spacing-lg);
      padding-top: var(--spacing-lg);
      border-top: 1px solid var(--glass-border);
    }

    .total-item {
      display: flex;
      justify-content: space-between;
      padding: var(--spacing-sm);
      margin-bottom: var(--spacing-xs);
    }

    .total-label {
      font-family: var(--font-mono);
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }

    .total-value {
      font-family: 'Orbitron', monospace;
      font-size: 1.1rem;
      color: var(--accent-primary);
      font-weight: 700;
    }

    .error-banner {
      padding: var(--spacing-md);
      margin-bottom: var(--spacing-lg);
      background: rgba(255, 0, 85, 0.1);
      border: 1px solid var(--accent-alert);
      border-left: 4px solid var(--accent-alert);
      color: var(--accent-alert);
      font-family: var(--font-mono);
    }

    .fade-in {
      animation: fade-in-up 0.5s ease-out;
    }
  `]
})
export class Time2PlayComponent {
    service = inject(Time2PlayService);

    searchQuery = '';
    backlogInput = '';
    backlogGames = signal<string[]>([]);
    showMarathonMode = signal(false);
    hoursPerDay = 2.5;

    async onSearch(event: Event) {
        event.preventDefault();
        if (!this.searchQuery.trim()) return;

        try {
            await this.service.searchGame(this.searchQuery);
            this.showMarathonMode.set(false); // Reset marathon mode on new search
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    toggleMarathonMode() {
        this.showMarathonMode.update(v => !v);
        if (this.showMarathonMode() && this.service.currentGame()) {
            this.calculateMarathon();
        }
    }

    async calculateMarathon() {
        if (!this.service.currentGame()) return;

        try {
            await this.service.calculateMarathon(
                this.service.currentGame()!.game,
                this.hoursPerDay
            );
        } catch (error) {
            console.error('Marathon calculation error:', error);
        }
    }

    addToBacklog() {
        if (!this.backlogInput.trim()) return;

        this.backlogGames.update(games => [...games, this.backlogInput.trim()]);
        this.backlogInput = '';
    }

    removeFromBacklog(index: number) {
        this.backlogGames.update(games => games.filter((_, i) => i !== index));
    }

    async calculateBacklog() {
        if (this.backlogGames().length === 0) return;

        try {
            await this.service.calculateBacklog(this.backlogGames());
        } catch (error) {
            console.error('Backlog calculation error:', error);
        }
    }

    getBarWidth(hours: number, type: 'main' | 'extras'): number {
        const maxHours = this.service.currentGame()?.times?.completionist || 100;
        return Math.min((hours / maxHours) * 100, 100);
    }

    getCompletionistGradient(hours: number): string {
        if (hours < 20) {
            return 'linear-gradient(90deg, #ffcc00, rgba(255, 204, 0, 0.5))';
        } else if (hours < 50) {
            return 'linear-gradient(90deg, #ff9900, rgba(255, 153, 0, 0.5))';
        } else if (hours < 100) {
            return 'linear-gradient(90deg, #ff6600, rgba(255, 102, 0, 0.5))';
        } else {
            return 'linear-gradient(90deg, #ff0055, rgba(255, 0, 85, 0.5))';
        }
    }

    getWorthClass(verdict: string): string {
        const normalized = verdict.toLowerCase().replace(/\s+/g, '-');
        return normalized;
    }
}
