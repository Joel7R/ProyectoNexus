/**
 * Price Hunter Component
 * Compare game prices across multiple stores
 */
import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PriceHunterService, type DealData } from '../../services/price-hunter.service';

@Component({
    selector: 'app-price-hunter',
    imports: [CommonModule, FormsModule],
    template: `
    <div class="price-hunter-container">
      <!-- Search Section -->
      <div class="search-section">
        <div class="search-icon">💰</div>
        <h1 class="search-title">PRICE HUNTER</h1>
        <p class="search-subtitle">FIND THE BEST GAMING DEALS</p>
        
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
            <span>{{ service.isLoading() ? 'SEARCHING...' : 'HUNT DEALS' }}</span>
          </button>
        </form>
      </div>

      <!-- Error Message -->
      @if (service.error()) {
        <div class="error-banner glass-card">
          ⚠️ {{ service.error() }}
        </div>
      }

      <!-- Results -->
      @if (service.currentDeals() && service.currentDeals()!.success) {
        <div class="results-container fade-in">
          <!-- Best Deal Highlight -->
          @if (service.currentDeals()!.best_deal) {
            <div class="best-deal-card glass-card">
              <div class="best-deal-header">
                <span class="trophy">🏆</span>
                <h2>BEST DEAL</h2>
              </div>
              
              <div class="best-deal-content">
                <div class="store-info">
                  <span class="store-icon">{{ service.currentDeals()!.best_deal!.icon }}</span>
                  <span class="store-name">{{ service.currentDeals()!.best_deal!.store }}</span>
                </div>
                
                <div class="price-display">
                  <span class="currency">$</span>
                  <span class="price">{{ service.currentDeals()!.best_deal!.price }}</span>
                </div>
                
                @if (service.currentDeals()!.savings > 0) {
                  <div class="savings-badge">
                    <span class="savings-amount">Save \${{ service.currentDeals()!.savings }}</span>
                    <span class="savings-percent">({{ service.currentDeals()!.savings_percent }}%)</span>
                  </div>
                }
                
                <a 
                  [href]="service.currentDeals()!.best_deal!.url" 
                  target="_blank" 
                  class="buy-btn"
                >
                  BUY NOW →
                </a>
              </div>
            </div>
          }

          <!-- Other Stores -->
          @if (service.currentDeals()!.deals.length > 1) {
            <div class="other-stores-section">
              <h3 class="section-title">OTHER STORES</h3>
              
              <div class="deals-grid">
                @for (deal of getOtherDeals(); track deal.store_id) {
                  <div class="deal-card glass-card">
                    <div class="deal-header">
                      <span class="store-icon">{{ deal.icon }}</span>
                      <span class="store-name">{{ deal.store }}</span>
                    </div>
                    
                    <div class="deal-price">
                      <span class="currency">$</span>
                      <span class="price">{{ deal.price }}</span>
                    </div>
                    
                    <a [href]="deal.url" target="_blank" class="deal-link">
                      VIEW DEAL →
                    </a>
                  </div>
                }
              </div>
            </div>
          }

          <!-- No Deals Found -->
          @if (service.currentDeals()!.deals.length === 0) {
            <div class="no-deals glass-card">
              <div class="no-deals-icon">🔍</div>
              <p>No deals found for "{{ service.currentDeals()!.game }}"</p>
              <p class="hint">Try a different game title or check back later</p>
            </div>
          }
        </div>
      }
    </div>
  `,
    styles: [`
    .price-hunter-container {
      max-width: 1200px;
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
      filter: drop-shadow(0 0 20px #ffcc00);
      animation: pulse-neon 3s ease-in-out infinite;
    }

    .search-title {
      font-family: var(--font-display);
      font-size: 3rem;
      letter-spacing: 0.2rem;
      color: #ffcc00;
      text-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
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
        border-color: #ffcc00;
        box-shadow: 0 0 20px rgba(255, 204, 0, 0.3);
      }

      &::placeholder {
        color: var(--text-muted);
      }
    }

    .search-btn {
      padding: var(--spacing-md) var(--spacing-xl);
      background: rgba(255, 204, 0, 0.1);
      border: 1px solid #ffcc00;
      color: #ffcc00;
      font-family: var(--font-display);
      font-size: 0.9rem;
      letter-spacing: 0.1em;
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all 0.3s;

      &:hover:not(:disabled) {
        background: #ffcc00;
        color: black;
        box-shadow: 0 0 20px rgba(255, 204, 0, 0.5);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    /* Best Deal Card */
    .best-deal-card {
      padding: var(--spacing-xl);
      margin-bottom: var(--spacing-xl);
      background: linear-gradient(135deg, rgba(57, 255, 20, 0.1), rgba(0, 243, 255, 0.05));
      border: 2px solid #39ff14;
      box-shadow: 0 0 30px rgba(57, 255, 20, 0.3);
    }

    .best-deal-header {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-lg);
      padding-bottom: var(--spacing-md);
      border-bottom: 1px solid rgba(57, 255, 20, 0.3);

      .trophy {
        font-size: 2rem;
        filter: drop-shadow(0 0 10px #ffcc00);
      }

      h2 {
        font-family: var(--font-display);
        font-size: 1.5rem;
        color: #39ff14;
        text-shadow: 0 0 15px rgba(57, 255, 20, 0.8);
        letter-spacing: 0.15em;
      }
    }

    .best-deal-content {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-lg);
    }

    .store-info {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);

      .store-icon {
        font-size: 2rem;
      }

      .store-name {
        font-family: var(--font-display);
        font-size: 1.25rem;
        color: var(--text-primary);
        letter-spacing: 0.05em;
      }
    }

    .price-display {
      display: flex;
      align-items: baseline;
      gap: var(--spacing-xs);

      .currency {
        font-family: var(--font-display);
        font-size: 2rem;
        color: #39ff14;
      }

      .price {
        font-family: 'Orbitron', monospace;
        font-size: 4rem;
        font-weight: 700;
        color: #39ff14;
        text-shadow: 0 0 20px rgba(57, 255, 20, 0.8);
        line-height: 1;
      }
    }

    .savings-badge {
      display: inline-flex;
      align-items: center;
      gap: var(--spacing-sm);
      padding: var(--spacing-sm) var(--spacing-md);
      background: rgba(57, 255, 20, 0.2);
      border: 1px solid #39ff14;
      border-radius: var(--radius-md);
      width: fit-content;

      .savings-amount {
        font-family: var(--font-display);
        font-size: 1.1rem;
        color: #39ff14;
        font-weight: 700;
      }

      .savings-percent {
        font-family: var(--font-mono);
        font-size: 0.9rem;
        color: var(--text-secondary);
      }
    }

    .buy-btn {
      padding: var(--spacing-md) var(--spacing-xl);
      background: #39ff14;
      color: black;
      font-family: var(--font-display);
      font-size: 1rem;
      font-weight: 700;
      letter-spacing: 0.1em;
      border-radius: var(--radius-md);
      text-decoration: none;
      text-align: center;
      transition: all 0.3s;
      box-shadow: 0 0 20px rgba(57, 255, 20, 0.5);

      &:hover {
        background: #2dd60f;
        box-shadow: 0 0 30px rgba(57, 255, 20, 0.8);
        transform: translateY(-2px);
      }
    }

    /* Other Stores */
    .other-stores-section {
      margin-top: var(--spacing-xl);
    }

    .section-title {
      font-family: var(--font-display);
      font-size: 1.25rem;
      color: var(--text-secondary);
      margin-bottom: var(--spacing-lg);
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }

    .deals-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      gap: var(--spacing-lg);
    }

    .deal-card {
      padding: var(--spacing-lg);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-md);
      transition: all 0.3s;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0, 243, 255, 0.2);
        border-color: var(--accent-primary);
      }
    }

    .deal-header {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      padding-bottom: var(--spacing-sm);
      border-bottom: 1px solid var(--glass-border);

      .store-icon {
        font-size: 1.5rem;
      }

      .store-name {
        font-family: var(--font-mono);
        font-size: 0.9rem;
        color: var(--text-primary);
      }
    }

    .deal-price {
      display: flex;
      align-items: baseline;
      gap: var(--spacing-xs);

      .currency {
        font-family: var(--font-display);
        font-size: 1.25rem;
        color: var(--accent-primary);
      }

      .price {
        font-family: 'Orbitron', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-primary);
        text-shadow: 0 0 10px var(--accent-primary);
      }
    }

    .deal-link {
      padding: var(--spacing-sm) var(--spacing-md);
      background: rgba(0, 243, 255, 0.1);
      border: 1px solid var(--accent-primary);
      color: var(--accent-primary);
      font-family: var(--font-mono);
      font-size: 0.8rem;
      letter-spacing: 0.05em;
      border-radius: var(--radius-sm);
      text-decoration: none;
      text-align: center;
      transition: all 0.3s;

      &:hover {
        background: var(--accent-primary);
        color: black;
      }
    }

    /* No Deals */
    .no-deals {
      padding: var(--spacing-xl);
      text-align: center;

      .no-deals-icon {
        font-size: 3rem;
        margin-bottom: var(--spacing-md);
        opacity: 0.5;
      }

      p {
        font-family: var(--font-mono);
        color: var(--text-secondary);
        margin-bottom: var(--spacing-sm);
      }

      .hint {
        font-size: 0.85rem;
        color: var(--text-muted);
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
export class PriceHunterComponent {
  service = inject(PriceHunterService);
  searchQuery = '';

  async onSearch(event: Event) {
    event.preventDefault();
    if (!this.searchQuery.trim()) return;

    try {
      await this.service.searchDeals(this.searchQuery);
    } catch (error) {
      console.error('Search error:', error);
    }
  }

  getOtherDeals(): DealData[] {
    const deals = this.service.currentDeals()?.deals || [];
    return deals.filter(deal => !deal.is_best);
  }
}
