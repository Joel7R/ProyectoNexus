/**
 * Gaming Nexus - Main App Component
 * Layout with Navbar and Router Outlet
 */
import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { HypeBarComponent } from './components/hype-bar/hype-bar.component';
import { NexusSidebarComponent } from './components/nexus-sidebar/nexus-sidebar.component';
import { NexusService } from './services/nexus.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, SidebarComponent, HypeBarComponent, NexusSidebarComponent],
  template: `
    <div class="nexus-container">
      <!-- Top Navigation Bar -->
      

      <!-- Ambient Hype Bar (Notifications) -->
      <app-hype-bar></app-hype-bar>

      <!-- Star Background & Scanlines -->
      <div class="cyber-grid"></div>
      <div class="scanline-overlay"></div>
    
      <!-- Sidebar Navigation -->
      <app-sidebar></app-sidebar>

      <!-- Main Content -->
      <main class="nexus-main">
        <router-outlet></router-outlet>
        
        <!-- Artifact Sidebar (Global Overlay) -->
        @if (nexusService.hasArtifact()) {
          <app-nexus-sidebar 
            class="nexus-sidebar"
            [artifact]="nexusService.currentArtifact()!" 
            (close)="nexusService.closeArtifact()"
          />
        }
      </main>
    </div>
  `,
  styles: [`
    .nexus-container {
      display: flex;
      flex-direction: row;
      height: 100vh;
      background: var(--bg-primary);
      position: relative;
      overflow: hidden;
    }

    .nexus-main {
      flex: 1;
      margin-left: 260px; /* Sidebar width */
      overflow-y: auto;
      position: relative;
      display: flex;
      flex-direction: row;
    }
    
    /* Ensure router outlet content takes available space */
    .nexus-main > *:not(app-nexus-sidebar) {
        flex: 1;
        width: 100%;
    }

    .nexus-sidebar {
      width: 420px;
      flex-shrink: 0;
      border-left: 1px solid var(--border-color);
      background: var(--bg-secondary);
      animation: slide-in 0.3s ease;
      position: absolute;
      right: 0;
      top: 0;
      bottom: 0;
      z-index: 50;
    }

    @keyframes slide-in {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    /* Responsive */
    @media (max-width: 768px) {
      .nexus-main {
        margin-left: 80px; /* Collapsed sidebar */
      }
    }
  `]
})
export class AppComponent {
  protected nexusService = inject(NexusService);
}
