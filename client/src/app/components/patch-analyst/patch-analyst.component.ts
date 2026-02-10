/**
 * Patch Analyst Component
 * Translates dry patch notes into tactical strategy
 */
import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PatchAnalystService, PatchChange } from '../../services/patch-analyst.service';

@Component({
    selector: 'app-patch-analyst',
    standalone: true,
    imports: [CommonModule, FormsModule],
    template: `
    <div class="patch-analyst">
      <!-- Header -->
      <div class="analyst-header">
        <h1 class="analyst-title">
          <span class="glow">META</span> ANALYST
        </h1>
        <p class="analyst-subtitle">From Numbers to Strategy</p>
      </div>

      <!-- Search & Filters -->
      <div class="search-section glass-card">
        <div class="search-inputs">
          <div class="input-group">
            <label>GAME</label>
            <select [(ngModel)]="selectedGame" class="cyber-select">
              <option value="League of Legends">League of Legends</option>
              <option value="Valorant">Valorant</option>
              <option value="Overwatch 2">Overwatch 2</option>
              <option value="Apex Legends">Apex Legends</option>
              <option value="Dota 2">Dota 2</option>
            </select>
          </div>
          
          <div class="input-group">
            <label>PATCH (OPTIONAL)</label>
            <input 
              type="text" 
              [(ngModel)]="patchVersion" 
              placeholder="e.g. 14.3" 
              class="cyber-input"
            />
          </div>

          <div class="input-group">
            <label>YOUR MAIN</label>
            <input 
              type="text" 
              [(ngModel)]="mainCharacter" 
              placeholder="e.g. Yasuo" 
              class="cyber-input main-filter"
            />
          </div>

          <button class="analyze-btn" (click)="analyze()" [disabled]="service.isLoading()">
            {{ service.isLoading() ? 'SCANNING...' : 'ANALYZE PATCH' }}
          </button>
        </div>
      </div>

      <!-- Analysis Results -->
      @if (service.analysis()) {
        <div class="results-layout">
          <!-- AI Verdict Section -->
          <div class="verdict-section glass-card">
            <div class="section-label">AI VERDICT</div>
            <div class="verdict-content">
              <div class="verdict-badge" [class]="service.analysis()!.verdict.direction">
                {{ service.analysis()!.verdict.direction.toUpperCase() }} PATCH
              </div>
              <h2 class="verdict-summary">{{ service.analysis()!.verdict.summary }}</h2>
              <p class="meta-shift">{{ service.analysis()!.verdict.meta_shift }}</p>
              
              <div class="meta-stats">
                <div class="stat-item">
                  <span class="stat-label">BUFFS</span>
                  <span class="stat-value buff">{{ service.analysis()!.verdict.buff_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">NERFS</span>
                  <span class="stat-value nerf">{{ service.analysis()!.verdict.nerf_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">PREDICTION</span>
                  <span class="stat-value highlight">{{ service.analysis()!.verdict.tier_prediction }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Balance Sheet Section -->
          <div class="balance-sheet">
            <div class="sheet-column buff-column">
              <h3 class="column-title buff">BUFFS</h3>
              <div class="changes-list">
                @for (change of service.getBuffs(); track change.stat) {
                  <div class="change-card buff-card" [class]="change.severity">
                    <div class="change-header">
                      <span class="character-name">{{ change.character }}</span>
                      <span class="severity-badge">{{ change.severity.toUpperCase() }}</span>
                    </div>
                    <div class="change-detail">
                      <span class="stat-name">{{ change.stat }}</span>
                      <div class="value-change">
                        <span class="before">{{ change.before }}</span>
                        <span class="arrow">↑</span>
                        <span class="after">{{ change.after }}</span>
                      </div>
                    </div>
                    <p class="tactical-advice">{{ change.impact }}</p>
                  </div>
                } @empty {
                  <p class="empty-note">No buffs detected</p>
                }
              </div>
            </div>

            <div class="sheet-column nerf-column">
              <h3 class="column-title nerf">NERFS</h3>
              <div class="changes-list">
                @for (change of service.getNerfs(); track change.stat) {
                  <div class="change-card nerf-card" [class]="change.severity">
                    <div class="change-header">
                      <span class="character-name">{{ change.character }}</span>
                      <span class="severity-badge">{{ change.severity.toUpperCase() }}</span>
                    </div>
                    <div class="change-detail">
                      <span class="stat-name">{{ change.stat }}</span>
                      <div class="value-change">
                        <span class="before">{{ change.before }}</span>
                        <span class="arrow">↓</span>
                        <span class="after">{{ change.after }}</span>
                      </div>
                    </div>
                    <p class="tactical-advice">{{ change.impact }}</p>
                  </div>
                } @empty {
                  <p class="empty-note">No nerfs detected</p>
                }
              </div>
            </div>
          </div>
        </div>
      } @else if (!service.isLoading() && !service.error()) {
        <div class="welcome-section">
          <div class="welcome-icon">⚡</div>
          <h2>Select a game to analyze the latest tactical shifts</h2>
          <p>We parse the dry numbers into actual gameplay consequences.</p>
        </div>
      }

      <!-- Error State -->
      @if (service.error()) {
        <div class="error-msg glass-card">
          <span class="error-icon">⚠️</span>
          <p>{{ service.error() }}</p>
        </div>
      }
    </div>
  `,
    styles: [`
    .patch-analyst {
      padding: var(--spacing-xl);
      max-width: 1200px;
      margin: 0 auto;
    }

    .analyst-header {
      text-align: center;
      margin-bottom: var(--spacing-xl);
    }

    .analyst-title {
      font-family: var(--font-display);
      font-size: 3.5rem;
      margin: 0;
      letter-spacing: 0.2em;
    }

    .analyst-subtitle {
      color: var(--text-secondary);
      font-size: 1.1rem;
      margin-top: var(--spacing-xs);
      letter-spacing: 0.1em;
    }

    /* Search Section */
    .search-section {
      padding: var(--spacing-xl);
      margin-bottom: var(--spacing-xxl);
      border: 1px solid var(--border-color);
    }

    .search-inputs {
      display: flex;
      gap: var(--spacing-lg);
      align-items: flex-end;
      flex-wrap: wrap;
    }

    .input-group {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);
      flex: 1;
      min-width: 200px;
    }

    .input-group label {
      font-size: 0.75rem;
      color: var(--text-secondary);
      letter-spacing: 0.1em;
      font-weight: 700;
    }

    .cyber-select, .cyber-input {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid var(--border-color);
      color: var(--text-primary);
      padding: 12px;
      border-radius: 4px;
      font-family: var(--font-mono);
      outline: none;
      transition: all 0.3s ease;
    }

    .cyber-select:focus, .cyber-input:focus {
      border-color: var(--accent-primary);
      box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
    }

    .analyze-btn {
      background: var(--accent-primary);
      color: #000;
      border: none;
      padding: 12px 30px;
      font-family: var(--font-display);
      font-weight: 700;
      border-radius: 4px;
      cursor: pointer;
      height: 48px;
      transition: all 0.3s ease;
    }

    .analyze-btn:hover:not(:disabled) {
      background: var(--text-primary);
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0, 243, 255, 0.4);
    }

    .analyze-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    /* Results Layout */
    .results-layout {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xl);
    }

    .verdict-section {
      padding: var(--spacing-xl);
      position: relative;
      border-left: 4px solid var(--accent-primary);
    }

    .section-label {
      position: absolute;
      top: -12px;
      left: 20px;
      background: var(--bg-primary);
      padding: 2px 10px;
      color: var(--accent-primary);
      font-family: var(--font-mono);
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.1em;
    }

    .verdict-badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 700;
      margin-bottom: var(--spacing-md);
    }

    .verdict-badge.buff-heavy { background: rgba(57, 255, 20, 0.2); color: #39ff14; }
    .verdict-badge.nerf-heavy { background: rgba(255, 0, 0, 0.2); color: #ff3333; }
    .verdict-badge.balanced { background: rgba(0, 243, 255, 0.2); color: var(--accent-primary); }

    .verdict-summary {
      font-family: var(--font-display);
      font-size: 1.8rem;
      margin: 0 0 var(--spacing-sm) 0;
    }

    .meta-shift {
      color: var(--text-secondary);
      font-size: 1.1rem;
      margin-bottom: var(--spacing-lg);
    }

    .meta-stats {
      display: flex;
      gap: var(--spacing-xxl);
      border-top: 1px solid var(--border-color);
      padding-top: var(--spacing-lg);
    }

    .stat-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .stat-label {
      font-size: 0.7rem;
      color: var(--text-secondary);
      letter-spacing: 0.1em;
    }

    .stat-value {
      font-family: var(--font-display);
      font-size: 1.5rem;
      font-weight: 700;
    }

    .stat-value.buff { color: #39ff14; }
    .stat-value.nerf { color: #ff3333; }
    .stat-value.highlight { color: var(--accent-primary); }

    /* Balance Sheet */
    .balance-sheet {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: var(--spacing-xl);
    }

    .column-title {
      font-family: var(--font-display);
      font-size: 1.5rem;
      padding-bottom: var(--spacing-md);
      border-bottom: 2px solid var(--border-color);
      margin-bottom: var(--spacing-lg);
    }

    .column-title.buff { color: #39ff14; border-color: rgba(57, 255, 20, 0.3); }
    .column-title.nerf { color: #ff3333; border-color: rgba(255, 0, 0, 0.3); }

    .changes-list {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-md);
    }

    .change-card {
      padding: var(--spacing-md);
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-color);
      border-radius: 8px;
    }

    .change-card.buff-card { border-left: 3px solid #39ff14; }
    .change-card.nerf-card { border-left: 3px solid #ff3333; }

    .change-card.major { background: rgba(255, 255, 255, 0.07); }

    .change-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--spacing-sm);
    }

    .character-name {
      font-weight: 700;
      color: var(--text-primary);
    }

    .severity-badge {
      font-size: 0.6rem;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: var(--font-mono);
    }

    .major .severity-badge { background: #bc13fe; color: white; }
    .moderate .severity-badge { background: rgba(255, 255, 255, 0.1); color: var(--text-secondary); }

    .change-detail {
      display: flex;
      flex-direction: column;
      gap: 4px;
      margin-bottom: var(--spacing-md);
    }

    .stat-name {
      font-size: 0.8rem;
      color: var(--text-secondary);
    }

    .value-change {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      font-family: var(--font-mono);
      font-size: 1.1rem;
    }

    .arrow { font-size: 1.3rem; font-weight: 700; }
    .buff-card .arrow { color: #39ff14; }
    .nerf-card .arrow { color: #ff3333; }

    .before { opacity: 0.5; }
    .after { color: var(--text-primary); font-weight: 700; }

    .tactical-advice {
      margin: 0;
      font-size: 0.9rem;
      color: var(--text-secondary);
      font-style: italic;
    }

    /* States */
    .welcome-section {
      text-align: center;
      padding: var(--spacing-xxl);
      opacity: 0.6;
    }

    .welcome-icon { font-size: 4rem; margin-bottom: var(--spacing-lg); }

    .error-msg {
      margin-top: var(--spacing-xl);
      padding: var(--spacing-lg);
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      color: #ff3333;
    }

    @media (max-width: 992px) {
      .balance-sheet { grid-template-columns: 1fr; }
    }
  `]
})
export class PatchAnalystComponent {
    service = inject(PatchAnalystService);

    selectedGame = 'League of Legends';
    patchVersion = '';
    mainCharacter = '';

    analyze() {
        this.service.analyzePatch(
            this.selectedGame,
            this.patchVersion || undefined,
            this.mainCharacter || undefined
        );
    }
}
