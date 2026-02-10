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
      padding: var(--spacing-md);
      max-width: 900px;
      margin: 0 auto;
    }
    
    .build-header {
      padding: var(--spacing-lg);
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      position: relative;
      overflow: hidden;
      
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, 
          var(--accent-primary), 
          var(--accent-secondary), 
          var(--accent-primary)
        );
        animation: pulse-neon 2s ease-in-out infinite;
      }
      
      .character-info {
        display: flex;
        align-items: center;
        gap: var(--spacing-md);
        margin-bottom: var(--spacing-sm);
      }
      
      .character-name {
        font-family: var(--font-display);
        font-size: 1.5rem;
        color: var(--accent-primary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
      }
      
      .tier-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        font-family: var(--font-display);
        font-weight: 900;
        font-size: 1.25rem;
        border: 2px solid;
        border-radius: var(--radius-sm);
        transition: all 0.3s;
        cursor: pointer;
        
        &:hover {
          transform: scale(1.1) rotate(5deg);
          box-shadow: 0 0 20px currentColor;
        }
      }
      
      .playstyle {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-family: var(--font-mono);
        padding-left: var(--spacing-sm);
        border-left: 2px solid var(--accent-secondary);
      }
    }
    
    .section-title {
      font-family: var(--font-display);
      font-size: 0.9rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--accent-primary);
      margin-bottom: var(--spacing-md);
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
      
      &--alert { 
        color: var(--accent-alert); 
        text-shadow: 0 0 5px var(--accent-alert);
      }
      &--success { 
        color: var(--accent-success);
        text-shadow: 0 0 5px var(--accent-success);
      }
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--spacing-md);
    }
    
    .stat-card {
      padding: var(--spacing-md);
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      transition: all 0.3s;
      
      &:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
        transform: translateY(-2px);
      }
      
      .stat-label {
        display: block;
        font-size: 0.7rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: var(--spacing-xs);
        font-family: var(--font-mono);
      }
      
      .stat-value {
        display: block;
        font-family: var(--font-display);
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: var(--spacing-sm);
        color: var(--text-primary);
        
        &--primary {
          color: var(--accent-primary);
          text-shadow: 0 0 10px rgba(0, 243, 255, 0.5);
        }
      }
    }
    
    .progress {
      height: 6px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: var(--radius-sm);
      overflow: hidden;
      position: relative;
      
      &__bar {
        height: 100%;
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
        border-radius: var(--radius-sm);
        transition: width 0.5s ease;
        box-shadow: 0 0 10px var(--accent-primary);
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
      }
    }
    
    @keyframes shimmer {
      0% { transform: translateX(-100%); }
      100% { transform: translateX(100%); }
    }
    
    .items-list, .skills-list {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }
    
    .item-card, .skill-card {
      padding: var(--spacing-md);
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      transition: all 0.3s;
      position: relative;
      
      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: var(--accent-primary);
        opacity: 0;
        transition: opacity 0.3s;
      }
      
      &:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
        transform: translateX(4px);
        
        &::before {
          opacity: 1;
        }
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
      color: var(--accent-primary);
      font-family: var(--font-display);
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    
    .item-slot {
      font-size: 0.65rem;
      color: var(--text-muted);
      padding: 2px 6px;
      background: rgba(0, 0, 0, 0.5);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      font-family: var(--font-mono);
      text-transform: uppercase;
    }
    
    .item-stats, .skill-desc {
      font-size: 0.8rem;
      color: var(--text-secondary);
      margin-bottom: var(--spacing-sm);
      line-height: 1.5;
    }
    
    .item-priority {
      .priority-label {
        display: block;
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-bottom: var(--spacing-xs);
        font-family: var(--font-mono);
        text-transform: uppercase;
      }
    }
    
    .skill-card--max-first {
      border-color: var(--accent-success);
      background: linear-gradient(135deg, rgba(0, 255, 136, 0.05), transparent);
      box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
    }
    
    .max-first-badge {
      font-size: 0.65rem;
      font-weight: 700;
      padding: 3px 8px;
      background: var(--accent-success);
      color: black;
      border-radius: var(--radius-sm);
      font-family: var(--font-display);
      letter-spacing: 0.05em;
      box-shadow: 0 0 10px var(--accent-success);
      animation: pulse-neon 2s ease-in-out infinite;
    }
    
    .matchups-section {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: var(--spacing-md);
    }
    
    .matchup-group {
      padding: var(--spacing-md);
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
    }
    
    .matchup-tags {
      display: flex;
      flex-wrap: wrap;
      gap: var(--spacing-xs);
    }
    
    .tag {
      padding: 4px 10px;
      font-size: 0.75rem;
      border-radius: var(--radius-sm);
      font-family: var(--font-mono);
      transition: all 0.2s;
      cursor: pointer;
      
      &--alert {
        background: rgba(255, 0, 85, 0.15);
        color: var(--accent-alert);
        border: 1px solid rgba(255, 0, 85, 0.3);
        
        &:hover {
          background: rgba(255, 0, 85, 0.25);
          box-shadow: 0 0 10px rgba(255, 0, 85, 0.4);
        }
      }
      
      &--success {
        background: rgba(0, 255, 136, 0.15);
        color: var(--accent-success);
        border: 1px solid rgba(0, 255, 136, 0.3);
        
        &:hover {
          background: rgba(0, 255, 136, 0.25);
          box-shadow: 0 0 10px rgba(0, 255, 136, 0.4);
        }
      }
    }
    
    .warning-banner {
      padding: var(--spacing-md);
      background: rgba(255, 204, 0, 0.1);
      border: 1px solid var(--accent-warning);
      border-left: 4px solid var(--accent-warning);
      border-radius: var(--radius-md);
      color: var(--accent-warning);
      font-size: 0.875rem;
      font-family: var(--font-mono);
      box-shadow: 0 0 15px rgba(255, 204, 0, 0.2);
    }
  `]
})
export class BuildDashboardComponent {
  @Input({ required: true }) data: any;
}
