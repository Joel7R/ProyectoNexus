/**
 * Lore Master Component
 * Game story and character relationships with spoiler control
 */
import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LoreMasterService } from '../../services/lore-master.service';

@Component({
    selector: 'app-lore-master',
    imports: [CommonModule, FormsModule],
    template: `
    <div class="lore-master-container">
      <!-- Search Section -->
      <div class="search-section">
        <div class="search-icon">📖</div>
        <h1 class="search-title">LORE MASTER</h1>
        <p class="search-subtitle">DISCOVER GAME STORIES & CHARACTERS</p>
        
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
          
          <select 
            [(ngModel)]="spoilerLevel" 
            name="spoilerLevel" 
            class="spoiler-select"
            [disabled]="service.isLoading()"
          >
            <option value="none">No Spoilers</option>
            <option value="light">Light Spoilers</option>
            <option value="full">Full Story</option>
          </select>
          
          <button 
            type="submit" 
            class="search-btn"
            [disabled]="!searchQuery.trim() || service.isLoading()"
          >
            <span>{{ service.isLoading() ? 'LOADING...' : 'EXPLORE' }}</span>
          </button>
        </form>
      </div>

      <!-- Error Message -->
      @if (service.error()) {
        <div class="error-banner glass-card">
          ⚠️ {{ service.error() }}
        </div>
      }

      <!-- Lore Content -->
      @if (service.currentLore() && service.currentLore()!.success) {
        <div class="lore-content fade-in">
          <!-- Spoiler Warning -->
          <div class="spoiler-warning glass-card" [class]="getSpoilerClass()">
            <div class="warning-icon">⚠️</div>
            <div class="warning-content">
              @for (warning of service.currentLore()!.spoiler_warnings; track warning) {
                <p>{{ warning }}</p>
              }
            </div>
            <button class="toggle-blur-btn" (click)="toggleBlur()">
              {{ showContent() ? '🔒 HIDE' : '👁️ REVEAL' }}
            </button>
          </div>

          <!-- Story Summary -->
          <div class="story-card glass-card" [class.blurred]="!showContent()">
            <h2 class="story-title">{{ service.currentLore()!.game }}</h2>
            
            <div class="story-summary">
              <p>{{ service.currentLore()!.summary }}</p>
            </div>

            @if (service.currentLore()!.key_events.length > 0) {
              <div class="key-events">
                <h3>Key Events</h3>
                <ul>
                  @for (event of service.currentLore()!.key_events; track event) {
                    <li>{{ event }}</li>
                  }
                </ul>
              </div>
            }

            @if (service.currentLore()!.sources && service.currentLore()!.sources!.length > 0) {
              <div class="sources">
                <h4>Sources:</h4>
                <div class="source-links">
                  @for (source of service.currentLore()!.sources; track source.url) {
                    <a [href]="source.url" target="_blank" class="source-link">
                      {{ source.title }}
                    </a>
                  }
                </div>
              </div>
            }
          </div>

          <!-- Character Map Button -->
          <div class="character-map-section">
            <button 
              class="load-characters-btn"
              (click)="loadCharacterMap()"
              [disabled]="service.isLoading()"
            >
              {{ service.characterMap() ? '🔄 RELOAD' : '🗺️ LOAD' }} CHARACTER MAP
            </button>
          </div>

          <!-- Character Map -->
          @if (service.characterMap() && service.characterMap()!.success) {
            <div class="character-map-card glass-card fade-in">
              <h3 class="map-title">CHARACTER RELATIONSHIPS</h3>
              
              @if (service.characterMap()!.characters.length > 0) {
                <div class="characters-list">
                  @for (char of service.characterMap()!.characters; track char.name) {
                    <div class="character-item">
                      <span class="char-name">{{ char.name }}</span>
                      <span class="char-role">{{ char.role }}</span>
                    </div>
                  }
                </div>
              }

              <!-- Mermaid Graph -->
              @if (service.characterMap()!.mermaid_graph) {
                <div class="mermaid-container">
                  <h4>Relationship Graph</h4>
                  <pre class="mermaid-code">{{ service.characterMap()!.mermaid_graph }}</pre>
                  <p class="mermaid-hint">
                    💡 Copy this Mermaid code to visualize at 
                    <a href="https://mermaid.live" target="_blank">mermaid.live</a>
                  </p>
                </div>
              }
            </div>
          }
        </div>
      }
    </div>
  `,
    styles: [`
    .lore-master-container {
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
      filter: drop-shadow(0 0 20px var(--accent-secondary));
      animation: pulse-neon 3s ease-in-out infinite;
    }

    .search-title {
      font-family: var(--font-display);
      font-size: 3rem;
      letter-spacing: 0.2rem;
      color: var(--accent-secondary);
      text-shadow: 0 0 20px rgba(188, 19, 254, 0.5);
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
      max-width: 800px;
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
        border-color: var(--accent-secondary);
        box-shadow: 0 0 20px rgba(188, 19, 254, 0.3);
      }
    }

    .spoiler-select {
      padding: var(--spacing-md);
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      color: var(--text-primary);
      font-family: var(--font-mono);
      font-size: 0.9rem;
      cursor: pointer;
      transition: all 0.3s;

      &:focus {
        outline: none;
        border-color: var(--accent-secondary);
      }
    }

    .search-btn {
      padding: var(--spacing-md) var(--spacing-xl);
      background: rgba(188, 19, 254, 0.1);
      border: 1px solid var(--accent-secondary);
      color: var(--accent-secondary);
      font-family: var(--font-display);
      font-size: 0.9rem;
      letter-spacing: 0.1em;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.3s;

      &:hover:not(:disabled) {
        background: var(--accent-secondary);
        color: black;
        box-shadow: 0 0 20px rgba(188, 19, 254, 0.5);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    /* Spoiler Warning */
    .spoiler-warning {
      padding: var(--spacing-lg);
      margin-bottom: var(--spacing-lg);
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      border-left: 4px solid var(--accent-warning);

      &.none {
        border-left-color: var(--accent-success);
      }

      &.light {
        border-left-color: var(--accent-warning);
      }

      &.full {
        border-left-color: var(--accent-alert);
      }
    }

    .warning-icon {
      font-size: 2rem;
    }

    .warning-content {
      flex: 1;
      font-family: var(--font-mono);
      font-size: 0.9rem;
      color: var(--text-secondary);

      p {
        margin: 0;
      }
    }

    .toggle-blur-btn {
      padding: var(--spacing-sm) var(--spacing-md);
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--glass-border);
      color: var(--text-primary);
      font-family: var(--font-mono);
      font-size: 0.85rem;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: var(--accent-primary);
      }
    }

    /* Story Card */
    .story-card {
      padding: var(--spacing-xl);
      margin-bottom: var(--spacing-lg);
      transition: all 0.3s;

      &.blurred {
        filter: blur(10px);
        user-select: none;
        pointer-events: none;
      }
    }

    .story-title {
      font-family: var(--font-display);
      font-size: 2rem;
      color: var(--accent-secondary);
      margin-bottom: var(--spacing-lg);
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }

    .story-summary {
      font-family: var(--font-mono);
      font-size: 1rem;
      line-height: 1.8;
      color: var(--text-primary);
      margin-bottom: var(--spacing-lg);

      p {
        margin-bottom: var(--spacing-md);
      }
    }

    .key-events {
      margin-top: var(--spacing-lg);
      padding-top: var(--spacing-lg);
      border-top: 1px solid var(--glass-border);

      h3 {
        font-family: var(--font-display);
        font-size: 1.25rem;
        color: var(--accent-primary);
        margin-bottom: var(--spacing-md);
        letter-spacing: 0.05em;
      }

      ul {
        list-style: none;
        padding: 0;

        li {
          padding: var(--spacing-sm) 0;
          padding-left: var(--spacing-lg);
          position: relative;
          font-family: var(--font-mono);
          font-size: 0.9rem;
          color: var(--text-secondary);

          &::before {
            content: '▸';
            position: absolute;
            left: 0;
            color: var(--accent-primary);
          }
        }
      }
    }

    .sources {
      margin-top: var(--spacing-lg);
      padding-top: var(--spacing-md);
      border-top: 1px solid var(--glass-border);

      h4 {
        font-family: var(--font-mono);
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-bottom: var(--spacing-sm);
        text-transform: uppercase;
      }
    }

    .source-links {
      display: flex;
      flex-wrap: wrap;
      gap: var(--spacing-sm);
    }

    .source-link {
      padding: var(--spacing-xs) var(--spacing-sm);
      background: rgba(0, 243, 255, 0.05);
      border: 1px solid rgba(0, 243, 255, 0.3);
      color: var(--accent-primary);
      font-family: var(--font-mono);
      font-size: 0.75rem;
      border-radius: var(--radius-sm);
      text-decoration: none;
      transition: all 0.2s;

      &:hover {
        background: rgba(0, 243, 255, 0.1);
        border-color: var(--accent-primary);
      }
    }

    /* Character Map */
    .character-map-section {
      margin-bottom: var(--spacing-lg);
      text-align: center;
    }

    .load-characters-btn {
      padding: var(--spacing-md) var(--spacing-xl);
      background: rgba(188, 19, 254, 0.1);
      border: 1px solid var(--accent-secondary);
      color: var(--accent-secondary);
      font-family: var(--font-display);
      font-size: 0.9rem;
      letter-spacing: 0.1em;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.3s;

      &:hover:not(:disabled) {
        background: var(--accent-secondary);
        color: black;
        box-shadow: 0 0 20px rgba(188, 19, 254, 0.5);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    .character-map-card {
      padding: var(--spacing-xl);
    }

    .map-title {
      font-family: var(--font-display);
      font-size: 1.5rem;
      color: var(--accent-secondary);
      margin-bottom: var(--spacing-lg);
      letter-spacing: 0.1em;
    }

    .characters-list {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-xl);
    }

    .character-item {
      padding: var(--spacing-md);
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-sm);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);

      .char-name {
        font-family: var(--font-display);
        font-size: 1rem;
        color: var(--text-primary);
      }

      .char-role {
        font-family: var(--font-mono);
        font-size: 0.75rem;
        color: var(--text-muted);
        text-transform: uppercase;
      }
    }

    .mermaid-container {
      margin-top: var(--spacing-lg);
      padding-top: var(--spacing-lg);
      border-top: 1px solid var(--glass-border);

      h4 {
        font-family: var(--font-display);
        font-size: 1rem;
        color: var(--accent-primary);
        margin-bottom: var(--spacing-md);
      }
    }

    .mermaid-code {
      padding: var(--spacing-md);
      background: rgba(0, 0, 0, 0.5);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-sm);
      font-family: var(--font-mono);
      font-size: 0.85rem;
      color: var(--accent-success);
      overflow-x: auto;
      white-space: pre;
    }

    .mermaid-hint {
      margin-top: var(--spacing-md);
      font-family: var(--font-mono);
      font-size: 0.85rem;
      color: var(--text-muted);

      a {
        color: var(--accent-primary);
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
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
export class LoreMasterComponent {
    service = inject(LoreMasterService);

    searchQuery = '';
    spoilerLevel = 'light';
    showContent = signal(true);

    async onSearch(event: Event) {
        event.preventDefault();
        if (!this.searchQuery.trim()) return;

        try {
            await this.service.getLore(this.searchQuery, this.spoilerLevel);
            // Reset blur state based on spoiler level
            this.showContent.set(this.spoilerLevel !== 'none');
        } catch (error) {
            console.error('Search error:', error);
        }
    }

    async loadCharacterMap() {
        if (!this.service.currentLore()) return;

        try {
            await this.service.getCharacterMap(this.service.currentLore()!.game);
        } catch (error) {
            console.error('Character map error:', error);
        }
    }

    toggleBlur() {
        this.showContent.update(v => !v);
    }

    getSpoilerClass(): string {
        return this.service.currentLore()?.spoiler_level || 'light';
    }
}
