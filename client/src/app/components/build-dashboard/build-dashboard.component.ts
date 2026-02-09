/**
 * Build Dashboard Component
 * Displays character builds with stats, items, and skills
 */
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-build-dashboard',
  standalone: true,
  template: `
    <div class="build-dashboard">
      <!-- Character Header -->
      @if (data['character']) {
        <div class="build-header">
          <div class="character-info">
            <h3 class="character-name">{{ data['character'].name }}</h3>
            @if (data['character'].tier) {
              <div 
                class="tier-badge" 
                [style.color]="data['character'].tier_color"
                [style.borderColor]="data['character'].tier_color"
              >
                {{ data['character'].tier }}
              </div>
            }
          </div>
          
          @if (data['playstyle']) {
            <p class="playstyle">{{ data['playstyle'] }}</p>
          }
        </div>
      }
      
      <!-- Stats -->
      @if (data['stats']) {
        <div class="stats-section">
          <h4 class="section-title">📈 Estadísticas</h4>
          <div class="stats-grid">
            @if (data['stats'].win_rate) {
              <div class="stat-card">
                <span class="stat-label">Win Rate</span>
                <span class="stat-value stat-value--primary">{{ data['stats'].win_rate }}</span>
                <div class="progress">
                  <div 
                    class="progress__bar" 
                    [style.width]="data['stats'].win_rate"
                  ></div>
                </div>
              </div>
            }
            @if (data['stats'].pick_rate) {
              <div class="stat-card">
                <span class="stat-label">Pick Rate</span>
                <span class="stat-value">{{ data['stats'].pick_rate }}</span>
                <div class="progress">
                  <div 
                    class="progress__bar" 
                    [style.width]="data['stats'].pick_rate"
                  ></div>
                </div>
              </div>
            }
          </div>
        </div>
      }
      
      <!-- Items -->
      @if (data['items'] && data['items'].length > 0) {
        <div class="items-section">
          <h4 class="section-title">🎒 Items</h4>
          <div class="items-list">
            @for (item of data['items']; track item.name) {
              <div class="item-card">
                <div class="item-header">
                  <span class="item-name">{{ item.name }}</span>
                  @if (item.slot) {
                    <span class="item-slot">{{ item.slot }}</span>
                  }
                </div>
                @if (item.stats) {
                  <p class="item-stats">{{ item.stats }}</p>
                }
                @if (item.priority_bar) {
                  <div class="item-priority">
                    <span class="priority-label">Prioridad</span>
                    <div class="progress">
                      <div 
                        class="progress__bar" 
                        [style.width.%]="item.priority_bar"
                      ></div>
                    </div>
                  </div>
                }
              </div>
            }
          </div>
        </div>
      }
      
      <!-- Skills -->
      @if (data['skills'] && data['skills'].length > 0) {
        <div class="skills-section">
          <h4 class="section-title">⚡ Habilidades</h4>
          <div class="skills-list">
            @for (skill of data['skills']; track skill.name) {
              <div class="skill-card" [class.skill-card--max-first]="skill.max_first">
                <div class="skill-header">
                  <span class="skill-name">{{ skill.name }}</span>
                  @if (skill.max_first) {
                    <span class="max-first-badge">MAX FIRST</span>
                  }
                </div>
                @if (skill.description) {
                  <p class="skill-desc">{{ skill.description }}</p>
                }
              </div>
            }
          </div>
        </div>
      }
      
      <!-- Counters & Synergies -->
      <div class="matchups-section">
        @if (data['counters'] && data['counters'].length > 0) {
          <div class="matchup-group">
            <h4 class="section-title section-title--alert">⚠️ Counters</h4>
            <div class="matchup-tags">
              @for (counter of data['counters']; track counter) {
                <span class="tag tag--alert">{{ counter }}</span>
              }
            </div>
          </div>
        }
        
        @if (data['synergies'] && data['synergies'].length > 0) {
          <div class="matchup-group">
            <h4 class="section-title section-title--success">✅ Sinergias</h4>
            <div class="matchup-tags">
              @for (synergy of data['synergies']; track synergy) {
                <span class="tag tag--success">{{ synergy }}</span>
              }
            </div>
          </div>
        }
      </div>
      
      <!-- Warning -->
      @if (data['source_warning']) {
        <div class="warning-banner">
          ⚠️ {{ data['source_warning'] }}
        </div>
      }
    </div>
  `,
  styles: [`
    .build-dashboard {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-lg);
    }
    
    .build-header {
      padding: var(--spacing-md);
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      
      .character-info {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        margin-bottom: var(--spacing-sm);
      }
      
      .character-name {
        font-family: var(--font-display);
        font-size: 1.25rem;
        color: var(--text-primary);
      }
      
      .tier-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        font-family: var(--font-display);
        font-weight: 700;
        border: 2px solid;
        border-radius: var(--radius-sm);
      }
      
      .playstyle {
        font-size: 0.875rem;
        color: var(--text-secondary);
      }
    }
    
    .section-title {
      font-family: var(--font-display);
      font-size: 0.875rem;
      letter-spacing: 0.05em;
      color: var(--accent-primary);
      margin-bottom: var(--spacing-md);
      
      &--alert { color: var(--accent-alert); }
      &--success { color: var(--accent-success); }
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--spacing-md);
    }
    
    .stat-card {
      padding: var(--spacing-md);
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      
      .stat-label {
        display: block;
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-bottom: var(--spacing-xs);
      }
      
      .stat-value {
        display: block;
        font-family: var(--font-display);
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: var(--spacing-sm);
        
        &--primary {
          color: var(--accent-primary);
        }
      }
    }
    
    .items-list, .skills-list {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }
    
    .item-card, .skill-card {
      padding: var(--spacing-md);
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      transition: var(--transition-fast);
      
      &:hover {
        border-color: var(--accent-primary);
      }
    }
    
    .item-header, .skill-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: var(--spacing-xs);
    }
    
    .item-name, .skill-name {
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .item-slot {
      font-size: 0.75rem;
      color: var(--text-muted);
      padding: 2px 6px;
      background: var(--bg-secondary);
      border-radius: var(--radius-sm);
    }
    
    .item-stats, .skill-desc {
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-bottom: var(--spacing-sm);
    }
    
    .item-priority {
      .priority-label {
        display: block;
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-bottom: var(--spacing-xs);
      }
    }
    
    .skill-card--max-first {
      border-color: var(--accent-success);
      background: rgba(0, 255, 136, 0.05);
    }
    
    .max-first-badge {
      font-size: 0.65rem;
      font-weight: 700;
      padding: 2px 6px;
      background: var(--accent-success);
      color: var(--bg-primary);
      border-radius: var(--radius-sm);
    }
    
    .matchups-section {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-md);
    }
    
    .matchup-tags {
      display: flex;
      flex-wrap: wrap;
      gap: var(--spacing-xs);
    }
    
    .tag {
      padding: var(--spacing-xs) var(--spacing-sm);
      font-size: 0.75rem;
      border-radius: var(--radius-sm);
      
      &--alert {
        background: rgba(255, 0, 85, 0.15);
        color: var(--accent-alert);
        border: 1px solid rgba(255, 0, 85, 0.3);
      }
      
      &--success {
        background: rgba(0, 255, 136, 0.15);
        color: var(--accent-success);
        border: 1px solid rgba(0, 255, 136, 0.3);
      }
    }
    
    .warning-banner {
      padding: var(--spacing-md);
      background: rgba(255, 204, 0, 0.1);
      border: 1px solid var(--accent-warning);
      border-radius: var(--radius-md);
      color: var(--accent-warning);
      font-size: 0.875rem;
    }
  `]
})
export class BuildDashboardComponent {
  @Input({ required: true }) data: any;
}
