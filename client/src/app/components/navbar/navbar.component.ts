import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
    selector: 'app-navbar',
    imports: [RouterLink, RouterLinkActive],
    template: `
    <nav class="navbar glass-panel">
      <div class="logo">
        <span class="text-primary">NEXUS</span> COMMAND
      </div>
      <div class="nav-links">
        <a routerLink="/news" routerLinkActive="active" class="nav-item">
          <i class="icon">📰</i> NEWS
        </a>
        <a routerLink="/calendar" routerLinkActive="active" class="nav-item">
          <i class="icon">📅</i> CALENDAR
        </a>
        <a routerLink="/time2play" routerLinkActive="active" class="nav-item">
          <i class="icon">⏱️</i> TIME2PLAY
        </a>
        <a routerLink="/chat" routerLinkActive="active" class="nav-item">
          <i class="icon">💬</i> CHAT
        </a>
      </div>
    </nav>
  `,
    styles: [`
    .navbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem 2rem;
      position: sticky;
      top: 0;
      z-index: 100;
      border-bottom: 1px solid var(--glass-border);
      backdrop-filter: blur(10px);
      background: rgba(5, 5, 5, 0.8);
    }

    .logo {
      font-family: var(--font-display);
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text-primary);
      letter-spacing: 0.1em;
    }

    .nav-links {
      display: flex;
      gap: 2rem;
    }

    .nav-item {
      color: var(--text-muted);
      text-decoration: none;
      font-family: var(--font-mono);
      font-size: 0.9rem;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      transition: all 0.3s ease;
      padding: 0.5rem 1rem;
      border-radius: 4px;
    }

    .nav-item:hover, .nav-item.active {
      color: var(--accent-primary);
      text-shadow: var(--glow-primary);
      background: rgba(0, 243, 255, 0.05);
    }
    
    .icon {
      font-style: normal;
    }
  `]
})
export class NavbarComponent { }
