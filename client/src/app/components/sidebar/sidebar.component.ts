/**
 * Sidebar Navigation Component
 * Cyber-Dark vertical navigation for 5-tab system
 */
import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SettingsModalComponent } from '../settings-modal/settings-modal.component';

@Component({
    selector: 'app-sidebar',
    imports: [CommonModule, RouterLink, RouterLinkActive, SettingsModalComponent],
    template: `
    <nav class="sidebar">
      <div class="logo">
        <span class="logo-text">
          <span class="glow">GAMING</span> NEXUS
        </span>
        <div class="logo-subtitle">AI COMMAND CENTER</div>
      </div>

      <div class="nav-items">
        <a routerLink="/news" routerLinkActive="active" class="nav-item">
          <i class="icon">📰</i>
          <span class="nav-text">News & Tracker</span>
          <div class="nav-indicator"></div>
        </a>

        <a routerLink="/time2play" routerLinkActive="active" class="nav-item">
          <i class="icon">⏱️</i>
          <span class="nav-text">Time2Play</span>
          <div class="nav-indicator"></div>
        </a>

        <a routerLink="/price-hunter" routerLinkActive="active" class="nav-item">
          <i class="icon">💰</i>
          <span class="nav-text">Price Hunter</span>
          <div class="nav-indicator"></div>
        </a>

        <a routerLink="/lore-master" routerLinkActive="active" class="nav-item">
          <i class="icon">📖</i>
          <span class="nav-text">Lore Master</span>
          <div class="nav-indicator"></div>
        </a>

        <a routerLink="/event-hub" routerLinkActive="active" class="nav-item">
          <i class="icon">🎉</i>
          <span class="nav-text">Event Hub</span>
          <div class="nav-indicator"></div>
        </a>

        <a routerLink="/patch-analyst" routerLinkActive="active" class="nav-item">
          <i class="icon">📊</i>
          <span class="nav-text">Patch Analyst</span>
          <div class="nav-indicator"></div>
        </a>

        <a routerLink="/chat" routerLinkActive="active" class="nav-item">
          <i class="icon">💬</i>
          <span class="nav-text">AI Chat Hub</span>
          <div class="nav-indicator"></div>
        </a>
      </div>

      <div class="sidebar-footer">
        <button class="settings-btn" (click)="showSettings = true">
          <i class="icon">⚙️</i>
          <span>Settings</span>
        </button>
        
        <div class="status-indicator">
          <div class="status-dot"></div>
          <span>ONLINE</span>
        </div>
      </div>
    </nav>
    
    @if (showSettings) {
      <app-settings-modal (close)="showSettings = false" />
    }
  `,
    styles: [`
    .sidebar {
      width: 260px;
      height: 100vh;
      position: fixed;
      left: 0;
      top: 0;
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border-right: 1px solid var(--glass-border);
      padding: var(--spacing-lg);
      display: flex;
      flex-direction: column;
      z-index: 1000;
    }

    /* Logo */
    .logo {
      margin-bottom: var(--spacing-xl);
      padding-bottom: var(--spacing-lg);
      border-bottom: 1px solid var(--glass-border);
    }

    .logo-text {
      font-family: var(--font-display);
      font-size: 1.5rem;
      font-weight: 700;
      letter-spacing: 0.15em;
      display: block;
      margin-bottom: var(--spacing-xs);
    }

    .glow {
      color: var(--accent-primary);
      text-shadow: 0 0 20px rgba(0, 243, 255, 0.8);
      animation: pulse-neon 3s ease-in-out infinite;
    }

    .logo-subtitle {
      font-family: var(--font-mono);
      font-size: 0.65rem;
      color: var(--text-muted);
      letter-spacing: 0.2em;
      text-transform: uppercase;
    }

    /* Navigation Items */
    .nav-items {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: var(--spacing-sm);
    }

    .nav-item {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      padding: var(--spacing-md);
      border-radius: var(--radius-md);
      text-decoration: none;
      color: var(--text-secondary);
      font-family: var(--font-mono);
      font-size: 0.9rem;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 3px;
        background: var(--accent-primary);
        transform: scaleY(0);
        transition: transform 0.3s ease;
      }

      &:hover {
        background: rgba(0, 243, 255, 0.05);
        color: var(--accent-primary);
        padding-left: calc(var(--spacing-md) + 8px);

        .icon {
          transform: scale(1.2);
          filter: drop-shadow(0 0 8px var(--accent-primary));
        }
      }

      &.active {
        background: rgba(0, 243, 255, 0.1);
        color: var(--accent-primary);
        border-left: 3px solid var(--accent-primary);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);

        &::before {
          transform: scaleY(1);
        }

        .icon {
          filter: drop-shadow(0 0 10px var(--accent-primary));
        }

        .nav-indicator {
          opacity: 1;
          transform: translateX(0);
        }
      }
    }

    .icon {
      font-size: 1.25rem;
      font-style: normal;
      transition: all 0.3s ease;
    }

    .nav-text {
      flex: 1;
      font-weight: 500;
      letter-spacing: 0.05em;
    }

    .nav-indicator {
      width: 6px;
      height: 6px;
      background: var(--accent-primary);
      border-radius: 50%;
      opacity: 0;
      transform: translateX(-10px);
      transition: all 0.3s ease;
      box-shadow: 0 0 8px var(--accent-primary);
    }

    /* Footer */
    .sidebar-footer {
      padding-top: var(--spacing-lg);
      border-top: 1px solid var(--glass-border);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-md);
    }

    .settings-btn {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      padding: var(--spacing-sm) var(--spacing-md);
      background: transparent;
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
      color: var(--text-muted);
      cursor: pointer;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      transition: all 0.2s;
      width: 100%;
      text-align: left;
      
      &:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: var(--text-muted);
        color: var(--text-primary);
      }
      
      .icon {
        font-size: 1rem;
      }
    }

    .status-indicator {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--accent-success);
      letter-spacing: 0.1em;
      padding-left: var(--spacing-sm);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      background: var(--accent-success);
      border-radius: 50%;
      animation: pulse-dot 2s ease-in-out infinite;
      box-shadow: 0 0 10px var(--accent-success);
    }

    @keyframes pulse-dot {
      0%, 100% {
        opacity: 1;
        transform: scale(1);
      }
      50% {
        opacity: 0.6;
        transform: scale(0.9);
      }
    }

    /* Responsive */
    @media (max-width: 768px) {
      .sidebar {
        width: 80px;
        padding: var(--spacing-md);
      }

      .logo-text,
      .logo-subtitle,
      .nav-text,
      .sidebar-footer span:not(.status-dot) {
        display: none;
      }
      
      .settings-btn {
        justify-content: center;
        padding: var(--spacing-sm);
        
        span { display: none; }
      }

      .nav-item {
        justify-content: center;
        padding: var(--spacing-md);

        .icon {
          font-size: 1.5rem;
        }
      }
    }
  `]
})
export class SidebarComponent {
  showSettings = false;
}
