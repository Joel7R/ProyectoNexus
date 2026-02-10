import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContentService, NewsItem } from '../../services/content.service';

@Component({
  selector: 'app-news',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container fade-in">
      <header class="section-header">
        <h1 class="text-primary glow-primary">LATEST TRANSMISSIONS</h1>
        <p class="text-muted">Updates from the gaming multiverse</p>
      </header>

      <div class="categories">
        <button 
          *ngFor="let cat of categories" 
          class="btn btn--sm" 
          [class.active]="currentCategory === cat.id"
          (click)="loadNews(cat.id)"
        >
          {{ cat.label }}
        </button>
      </div>

      <div class="news-auth-status" *ngIf="loading">
        <div class="loading-dots">
            <span></span><span></span><span></span>
        </div>
        <p class="text-muted">Scanning frequency...</p>
      </div>

      <div class="news-grid" *ngIf="!loading">
        <article *ngFor="let item of news" class="card news-card">
          <div class="card-image-placeholder">
             <!-- Placeholder for image, using a gradient for now -->
             <div class="image-gradient"></div>
          </div>
          <div class="card-content">
            <span class="date">
                {{item.date}}
                <span *ngIf="item.source_lang" class="lang-badge" [class.es]="item.source_lang === 'es'" [class.en]="item.source_lang === 'en'">
                    [{{item.source_lang | uppercase}}]
                </span>
            </span>
            <h3 class="card__title">{{item.title}}</h3>
            <p class="card-summary">{{item.summary}}</p>
            <div class="card-actions">
                <a [href]="item.url" target="_blank" class="btn btn--primary read-more">READ_LOG ></a>
                <a *ngIf="item.url" [href]="item.url" target="_blank" class="btn btn--text see-original">See Original_</a>
            </div>
          </div>
        </article>
      </div>
    </div>
  `,
  styles: [`
    .container {
      padding: 2rem;
      max-width: 1200px;
      margin: 0 auto;
    }

    .section-header {
      margin-bottom: 2rem;
      text-align: center;
    }
    
    .categories {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 3rem;
    }
    
    .categories .btn.active {
        background: var(--accent-primary);
        color: var(--bg-primary);
    }

    .news-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem;
      padding: var(--spacing-md);
    }

    .news-card {
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
      padding: 0;
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      transition: all 0.3s ease;
      position: relative;
      
      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
        opacity: 0;
        transition: opacity 0.3s;
      }
      
      &:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
        transform: translateY(-4px);
        
        &::before {
          opacity: 1;
        }
      }
    }

    .card-image-placeholder {
      height: 180px;
      width: 100%;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
      position: relative;
      overflow: hidden;
    }
    
    .image-gradient {
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, 
          rgba(0, 243, 255, 0.1) 0%, 
          rgba(188, 19, 254, 0.1) 100%
        );
        position: relative;
        
        &::after {
          content: '📰';
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 3rem;
          opacity: 0.3;
        }
    }

    .card-content {
      padding: 1.25rem;
      flex-grow: 1;
      display: flex;
      flex-direction: column;
    }

    .date {
      color: var(--text-muted);
      font-size: 0.7rem;
      font-family: var(--font-mono);
      margin-bottom: 0.5rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .card__title {
      margin-bottom: 0.75rem;
      line-height: 1.3;
      font-size: 1rem;
      font-family: var(--font-display);
      color: var(--accent-primary);
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }

    .card-summary {
      color: var(--text-secondary);
      margin-bottom: 1rem;
      flex-grow: 1;
      font-size: 0.85rem;
      line-height: 1.5;
    }
    
    .news-auth-status {
        text-align: center;
        padding: 4rem;
        color: var(--text-muted);
        font-family: var(--font-mono);
    }

    .read-more {
      align-self: flex-start;
      padding: 0.5rem 1rem;
      background: rgba(0, 243, 255, 0.1);
      border: 1px solid var(--accent-primary);
      color: var(--accent-primary);
      font-family: var(--font-display);
      font-size: 0.75rem;
      letter-spacing: 0.1em;
      transition: all 0.2s;
      
      &:hover {
        background: var(--accent-primary);
        color: black;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.5);
        transform: translateX(4px);
      }
    }

    .card-actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: auto;
        padding-top: 0.75rem;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }

    .see-original {
        font-size: 0.7rem;
        color: var(--text-muted);
        text-decoration: none;
        font-family: var(--font-mono);
        opacity: 0.7;
        transition: all 0.2s;
        border-bottom: 1px dotted transparent;
        
        &:hover {
          opacity: 1;
          color: var(--accent-secondary);
          border-bottom-color: var(--accent-secondary);
        }
    }
    
    .lang-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 2px 6px;
        font-size: 0.65rem;
        font-weight: bold;
        font-family: var(--font-display);
        border-radius: 2px;
        background: rgba(0, 0, 0, 0.5);
        border: 1px solid;
        letter-spacing: 0.05em;
        transition: all 0.2s;
    }
    
    .lang-badge.es {
        color: var(--accent-warning);
        border-color: var(--accent-warning);
        box-shadow: 0 0 5px rgba(255, 204, 0, 0.3);
        
        &:hover {
          box-shadow: 0 0 10px rgba(255, 204, 0, 0.6);
        }
    }
    
    .lang-badge.en {
        color: var(--accent-primary);
        border-color: var(--accent-primary);
        box-shadow: 0 0 5px rgba(0, 243, 255, 0.3);
        
        &:hover {
          box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
        }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

  `]
})
export class NewsComponent implements OnInit {
  private contentService = inject(ContentService);

  news: NewsItem[] = [];
  loading = true;
  currentCategory = 'general';

  categories = [
    { id: 'general', label: 'ALL_CHANNELS' },
    { id: 'patches', label: 'PATCH_NOTES' },
    { id: 'releases', label: 'NEW_DROPS' },
    { id: 'esports', label: 'E_SPORTS' }
  ];

  ngOnInit() {
    this.loadNews(this.currentCategory);
  }

  loadNews(category: string) {
    this.loading = true;
    this.currentCategory = category;
    this.contentService.getNews(category).subscribe(response => {
      this.news = response.items;
      this.loading = false;
    });
  }
}
