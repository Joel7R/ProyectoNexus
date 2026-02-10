import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContentService } from '../../services/content.service';

@Component({
  selector: 'app-calendar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="container fade-in">
      <header class="section-header">
        <h1 class="text-primary glow-primary">UPCOMING DROPS</h1>
        <p class="text-muted">Launch schedule for anticipated titles</p>
      </header>

      <div class="status-container" *ngIf="loading">
        <div class="loading-dots">
            <span></span><span></span><span></span>
        </div>
        <p class="text-muted">Syncing timeline...</p>
      </div>

      <div class="timeline" *ngIf="!loading">
        <!-- If we have parsed items, iterate them. For now we might just have raw data if backend didn't parse well -->
        <!-- Fallback display if structure is not perfect -->
        <div class="timeline-item" *ngFor="let game of games">
          <div class="timeline-date">
             <!-- Hacky date display since we rely on scraping -->
            <span class="month">UPCOMING</span>
          </div>
          <div class="timeline-content card">
            <h3 class="game-title">{{game.title}}</h3>
            
            <p class="game-desc" *ngIf="game.date">{{game.date}}</p>
            
             <a [href]="game.url" target="_blank" class="btn btn--sm">VIEW_DETAILS</a>
          </div>
        </div>
        
        <div *ngIf="games.length === 0 && !loading" class="text-muted text-center">
            No upcoming releases found in this sector.
        </div>
      </div>
    </div>
  `,
  styles: [`
    .container {
      padding: 2rem;
      max-width: 800px;
      margin: 0 auto;
    }

    .section-header {
      margin-bottom: 3rem;
      text-align: center;
    }
    
    .status-container {
        text-align: center;
        padding: 4rem;
    }

    .timeline {
      position: relative;
      padding-left: 2rem;
      border-left: 2px solid var(--border-color);
    }

    .timeline-item {
      position: relative;
      margin-bottom: 3rem;
      padding-left: 2rem;
    }

    .timeline-item::before {
      content: '';
      position: absolute;
      left: -2.6rem; /* Adjust based on border and padding */
      top: 0;
      width: 1rem;
      height: 1rem;
      background: var(--bg-primary);
      border: 2px solid var(--accent-primary);
      border-radius: 50%;
      box-shadow: var(--glow-primary);
      z-index: 1;
    }

    .timeline-date {
      position: absolute;
      left: -8rem;
      top: -0.5rem;
      text-align: right;
      width: 5rem;
      color: var(--accent-secondary);
      font-family: var(--font-display);
    }
    
    .month {
        display: block;
        font-size: 0.8rem;
        font-weight: 700;
    }
    
    .day {
        font-size: 1.5rem;
        font-weight: 700;
    }

    .timeline-content.card {
      transition: transform 0.3s ease;
      cursor: pointer;
    }

    .timeline-content:hover {
      transform: translateX(10px);
    }

    .game-title {
      color: var(--text-primary);
      margin-bottom: 0.5rem;
      font-size: 1.25rem;
    }

    .platforms {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }

    .badge {
      background: rgba(255, 255, 255, 0.1);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.7rem;
      font-family: var(--font-mono);
      border: 1px solid var(--border-color);
    }

    .game-desc {
      color: var(--text-muted);
      font-size: 0.9rem;
      margin-bottom: 1rem;
    }
    
    .btn--sm {
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .loading-dots {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }

    .loading-dots span {
        width: 0.75rem;
        height: 0.75rem;
        background-color: var(--accent-primary);
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }

    .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
    .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
    .loading-dots span:nth-child(3) { animation-delay: 0s; }

    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    @media (max-width: 600px) {
        .timeline-date {
            position: relative;
            left: 0;
            top: 0;
            text-align: left;
            margin-bottom: 0.5rem;
            display: flex;
            gap: 0.5rem;
            align-items: baseline;
        }
        
        .timeline {
            padding-left: 1rem;
        }
        
        .timeline-item {
            padding-left: 0;
        }
        
        .timeline-item::before {
            left: -1.6rem;
        }
    }
  `]
})
export class CalendarComponent implements OnInit {
  private contentService = inject(ContentService);

  games: any[] = [];
  loading = true;

  ngOnInit() {
    this.contentService.getCalendar().subscribe(response => {
      // Adapt raw data (sources) to display format
      // Backend returns "raw_data" which is a list of {title, url}
      this.games = response.raw_data.map((item: any) => ({
        title: item.title,
        url: item.url,
        date: 'Coming Soon', // We don't have date parsing in this MVP yet
        platforms: []
      }));
      this.loading = false;
    });
  }
}
