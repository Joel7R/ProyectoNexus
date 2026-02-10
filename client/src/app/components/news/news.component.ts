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
            <span class="date">{{item.date}}</span>
            <h3 class="card__title">{{item.title}}</h3>
            <p class="card-summary">{{item.summary}}</p>
            <a [href]="item.url" target="_blank" class="btn btn--primary read-more">READ_LOG ></a>
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
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 2rem;
    }

    .news-card {
      display: flex;
      flex-direction: column;
      height: 100%;
      overflow: hidden;
      padding: 0; 
    }

    .card-image-placeholder {
      height: 200px;
      width: 100%;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border-color);
    }
    
    .image-gradient {
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, var(--bg-secondary), var(--bg-tertiary));
    }

    .card-content {
      padding: 1.5rem;
      flex-grow: 1;
      display: flex;
      flex-direction: column;
    }

    .date {
      color: var(--accent-secondary);
      font-size: 0.75rem;
      font-family: var(--font-mono);
      margin-bottom: 0.5rem;
    }

    .card__title {
      margin-bottom: 1rem;
      line-height: 1.4;
      font-size: 1.1rem;
    }

    .card-summary {
      color: var(--text-secondary);
      margin-bottom: 1.5rem;
      flex-grow: 1;
      font-size: 0.9rem;
    }
    
    .news-auth-status {
        text-align: center;
        padding: 4rem;
    }

    .read-more {
      align-self: flex-start;
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
