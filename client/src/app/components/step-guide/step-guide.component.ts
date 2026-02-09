/**
 * Step Guide Component
 * Progressive reveal guide with collapsible steps
 */
import { Component, Input, signal } from '@angular/core';

interface Step {
  number: number;
  title: string;
  content: string;
  tip?: string;
  warning?: string;
  spoiler_level: 'low' | 'medium' | 'high';
  collapsed: boolean;
  hidden: boolean;
}

@Component({
  selector: 'app-step-guide',
  standalone: true,
  template: `
    <div class="step-guide">
      <!-- Hint Header -->
      @if (data['hint']) {
        <div class="guide-hint">
          <span class="hint-icon">💡</span>
          <p class="hint-text">{{ data['hint'] }}</p>
        </div>
      }
      
      <!-- Difficulty & Time -->
      <div class="guide-meta">
        @if (data['difficulty']) {
          <div class="meta-item">
            <span class="meta-label">Dificultad:</span>
            <span 
              class="difficulty-badge" 
              [style.color]="data['difficulty_color']"
            >
              {{ getDifficultyLabel(data['difficulty']) }}
            </span>
          </div>
        }
        @if (data['estimated_time']) {
          <div class="meta-item">
            <span class="meta-label">⏱️</span>
            <span class="meta-value">{{ data['estimated_time'] }}</span>
          </div>
        }
      </div>
      
      <!-- Steps -->
      <div class="steps-container">
        @for (step of steps(); track step.number) {
          <div 
            class="step-card" 
            [class.step-card--collapsed]="step.collapsed"
            [class.step-card--hidden]="step.hidden"
            [class.step-card--spoiler]="step.spoiler_level === 'high'"
          >
            <div class="step-header" (click)="toggleStep(step)">
              <div class="step-number">{{ step.number }}</div>
              <div class="step-title">{{ step.title }}</div>
              <div class="step-toggle">
                {{ step.collapsed ? '▼' : '▲' }}
              </div>
            </div>
            
            @if (!step.collapsed) {
              <div class="step-body">
                @if (step.hidden && !revealedSteps().has(step.number)) {
                  <div class="spoiler-warning">
                    <span class="spoiler-icon">🔒</span>
                    <p>Este paso contiene spoilers</p>
                    <button class="reveal-btn" (click)="revealStep(step.number, $event)">
                      Revelar
                    </button>
                  </div>
                } @else {
                  <p class="step-content">{{ step.content }}</p>
                  
                  @if (step.tip) {
                    <div class="step-tip">
                      <span class="tip-icon">💡</span>
                      <span>{{ step.tip }}</span>
                    </div>
                  }
                  
                  @if (step.warning) {
                    <div class="step-warning">
                      <span class="warning-icon">⚠️</span>
                      <span>{{ step.warning }}</span>
                    </div>
                  }
                }
              </div>
            }
          </div>
        }
      </div>
      
      <!-- Collectibles -->
      @if (data['collectibles'] && data['collectibles'].length > 0) {
        <div class="collectibles-section">
          <h4 class="section-title">🏆 Coleccionables</h4>
          <div class="collectibles-list">
            @for (item of data['collectibles']; track item.name) {
              <div class="collectible-item">
                <span class="collectible-name">{{ item.name }}</span>
                <span class="collectible-location">{{ item.location }}</span>
              </div>
            }
          </div>
        </div>
      }
      
      <!-- Rewards -->
      @if (data['rewards'] && data['rewards'].length > 0) {
        <div class="rewards-section">
          <h4 class="section-title">🎁 Recompensas</h4>
          <div class="rewards-tags">
            @for (reward of data['rewards']; track reward) {
              <span class="reward-tag">{{ reward }}</span>
            }
          </div>
        </div>
      }
      
      <!-- Reveal All Button -->
      @if (hasHiddenSteps()) {
        <button class="reveal-all-btn" (click)="revealAllSteps()">
          🔓 Revelar todos los pasos
        </button>
      }
    </div>
  `,
  styles: [`
    .step-guide {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-lg);
    }
    
    .guide-hint {
      display: flex;
      gap: var(--spacing-md);
      padding: var(--spacing-md);
      background: linear-gradient(135deg, rgba(0, 243, 255, 0.1), transparent);
      border: 1px solid rgba(0, 243, 255, 0.3);
      border-radius: var(--radius-md);
      
      .hint-icon {
        font-size: 1.5rem;
      }
      
      .hint-text {
        color: var(--text-primary);
        font-size: 0.9375rem;
        line-height: 1.5;
      }
    }
    
    .guide-meta {
      display: flex;
      gap: var(--spacing-lg);
      
      .meta-item {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
      }
      
      .meta-label {
        font-size: 0.75rem;
        color: var(--text-muted);
      }
      
      .meta-value {
        font-size: 0.875rem;
        color: var(--text-secondary);
      }
      
      .difficulty-badge {
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
      }
    }
    
    .steps-container {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }
    
    .step-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      overflow: hidden;
      transition: var(--transition-fast);
      
      &:hover {
        border-color: var(--accent-primary);
      }
      
      &--spoiler {
        border-color: var(--accent-alert);
        
        .step-number {
          background: var(--accent-alert);
        }
      }
    }
    
    .step-header {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      padding: var(--spacing-md);
      cursor: pointer;
      user-select: none;
      
      &:hover {
        background: var(--bg-hover);
      }
    }
    
    .step-number {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--accent-primary);
      color: var(--bg-primary);
      font-family: var(--font-display);
      font-weight: 700;
      font-size: 0.875rem;
      border-radius: var(--radius-sm);
    }
    
    .step-title {
      flex: 1;
      font-weight: 500;
      color: var(--text-primary);
    }
    
    .step-toggle {
      color: var(--text-muted);
      font-size: 0.75rem;
    }
    
    .step-body {
      padding: 0 var(--spacing-md) var(--spacing-md);
      padding-left: calc(28px + var(--spacing-md) * 2);
    }
    
    .step-content {
      color: var(--text-secondary);
      font-size: 0.875rem;
      line-height: 1.6;
      margin-bottom: var(--spacing-md);
    }
    
    .step-tip, .step-warning {
      display: flex;
      align-items: flex-start;
      gap: var(--spacing-sm);
      padding: var(--spacing-sm);
      border-radius: var(--radius-sm);
      font-size: 0.8rem;
      margin-bottom: var(--spacing-sm);
    }
    
    .step-tip {
      background: rgba(0, 255, 136, 0.1);
      border: 1px solid rgba(0, 255, 136, 0.3);
      color: var(--accent-success);
    }
    
    .step-warning {
      background: rgba(255, 204, 0, 0.1);
      border: 1px solid rgba(255, 204, 0, 0.3);
      color: var(--accent-warning);
    }
    
    .spoiler-warning {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: var(--spacing-lg);
      text-align: center;
      
      .spoiler-icon {
        font-size: 2rem;
        margin-bottom: var(--spacing-sm);
      }
      
      p {
        color: var(--text-muted);
        margin-bottom: var(--spacing-md);
      }
      
      .reveal-btn {
        padding: var(--spacing-sm) var(--spacing-md);
        background: transparent;
        border: 1px solid var(--accent-primary);
        border-radius: var(--radius-sm);
        color: var(--accent-primary);
        font-family: var(--font-mono);
        cursor: pointer;
        transition: var(--transition-fast);
        
        &:hover {
          background: rgba(0, 243, 255, 0.1);
        }
      }
    }
    
    .section-title {
      font-family: var(--font-display);
      font-size: 0.875rem;
      letter-spacing: 0.05em;
      color: var(--accent-primary);
      margin-bottom: var(--spacing-md);
    }
    
    .collectibles-list {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }
    
    .collectible-item {
      display: flex;
      justify-content: space-between;
      padding: var(--spacing-sm) var(--spacing-md);
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-sm);
      
      .collectible-name {
        color: var(--text-primary);
        font-size: 0.875rem;
      }
      
      .collectible-location {
        color: var(--text-muted);
        font-size: 0.75rem;
      }
    }
    
    .rewards-tags {
      display: flex;
      flex-wrap: wrap;
      gap: var(--spacing-sm);
    }
    
    .reward-tag {
      padding: var(--spacing-xs) var(--spacing-sm);
      background: rgba(255, 204, 0, 0.15);
      border: 1px solid rgba(255, 204, 0, 0.3);
      border-radius: var(--radius-sm);
      color: var(--accent-warning);
      font-size: 0.75rem;
    }
    
    .reveal-all-btn {
      width: 100%;
      padding: var(--spacing-md);
      background: rgba(26, 26, 26, 0.4);
      border: 1px dashed var(--accent-alert);
      border-radius: var(--radius-md);
      color: var(--accent-alert);
      font-family: var(--font-mono);
      cursor: pointer;
      transition: var(--transition-fast);
      
      &:hover {
        background: rgba(255, 0, 85, 0.1);
      }
    }
  `]
})
export class StepGuideComponent {
  @Input({ required: true }) data: any;

  steps = signal<Step[]>([]);
  revealedSteps = signal<Set<number>>(new Set());

  ngOnChanges(): void {
    if (this.data['steps']) {
      this.steps.set(this.data['steps'].map((s: any) => ({
        ...s,
        collapsed: s.collapsed ?? false,
        hidden: s.hidden ?? false
      })));
    }
  }

  toggleStep(step: Step): void {
    this.steps.update(steps =>
      steps.map(s =>
        s.number === step.number
          ? { ...s, collapsed: !s.collapsed }
          : s
      )
    );
  }

  revealStep(stepNumber: number, event: Event): void {
    event.stopPropagation();
    this.revealedSteps.update(set => {
      const newSet = new Set(set);
      newSet.add(stepNumber);
      return newSet;
    });
  }

  revealAllSteps(): void {
    const allNumbers = this.steps().map(s => s.number);
    this.revealedSteps.set(new Set(allNumbers));
    this.steps.update(steps =>
      steps.map(s => ({ ...s, collapsed: false, hidden: false }))
    );
  }

  hasHiddenSteps(): boolean {
    return this.steps().some(s => s.hidden && !this.revealedSteps().has(s.number));
  }

  getDifficultyLabel(difficulty: string): string {
    const labels: Record<string, string> = {
      easy: '🟢 Fácil',
      medium: '🟡 Medio',
      hard: '🟠 Difícil',
      very_hard: '🔴 Muy Difícil'
    };
    return labels[difficulty] || difficulty;
  }
}
