/**
 * Gaming Nexus - Main App Component
 * Layout with chat stream and artifact sidebar
 */
import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ChatStreamComponent } from './components/chat-stream/chat-stream.component';
import { NexusSidebarComponent } from './components/nexus-sidebar/nexus-sidebar.component';
import { NexusService } from './services/nexus.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ChatStreamComponent, NexusSidebarComponent],
  template: `
    <div class="nexus-container">
      <!-- Header -->
      <header class="nexus-header">
        <div class="nexus-logo">
          <span class="nexus-logo__icon">🎮</span>
          <h1 class="nexus-logo__text">GAMING NEXUS</h1>
        </div>
        <div class="nexus-header__status">
          <span class="status-dot"></span>
          <span class="status-text">LIVE</span>
        </div>
      </header>
      
      <!-- Main Content -->
      <main class="nexus-main" [class.has-sidebar]="nexusService.hasArtifact()">
        <!-- Chat Stream -->
        <app-chat-stream class="nexus-chat" />
        
        <!-- Artifact Sidebar -->
        @if (nexusService.hasArtifact()) {
          <app-nexus-sidebar 
            class="nexus-sidebar"
            [artifact]="nexusService.currentArtifact()!" 
            (close)="nexusService.closeArtifact()"
          />
        }
      </main>
      
      <!-- Scanline overlay effect -->
      <div class="scanline-overlay"></div>
      
      <!-- Cyber Grid Background -->
      <div class="cyber-grid"></div>
    </div>
  `,
  styles: [`
    .nexus-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
      background: var(--bg-primary);
    }
    
    .nexus-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 60px;
      padding: 0 var(--spacing-lg);
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      border-bottom: 1px solid var(--glass-border);
      box-shadow: var(--glass-shadow);
      z-index: 10;
    }
    
    .nexus-logo {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      
      &__icon {
        font-size: 1.5rem;
      }
      
      &__text {
        font-family: var(--font-display);
        font-size: 1.25rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        color: var(--accent-primary);
        text-shadow: var(--glow-primary);
      }
    }
    
    .nexus-header__status {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      
      .status-dot {
        width: 8px;
        height: 8px;
        background: var(--accent-success);
        border-radius: 50%;
        animation: pulse-glow 2s ease-in-out infinite;
      }
      
      .status-text {
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        color: var(--accent-success);
      }
    }
    
    .nexus-main {
      display: flex;
      flex: 1;
      overflow: hidden;
    }
    
    .nexus-chat {
      flex: 1;
      min-width: 0;
    }
    
    .nexus-sidebar {
      width: 420px;
      flex-shrink: 0;
      border-left: 1px solid var(--border-color);
      animation: slide-in 0.3s ease;
    }
    
    @keyframes slide-in {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    
    .has-sidebar .nexus-chat {
      flex: 1;
    }
  `]
})
export class AppComponent {
  protected nexusService = inject(NexusService);
}
