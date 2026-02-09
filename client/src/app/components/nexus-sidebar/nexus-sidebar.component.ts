/**
 * Nexus Sidebar Component
 * Dynamic artifact display based on type
 */
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { JsonPipe } from '@angular/common';
import { Artifact } from '../../services/nexus.service';
import { TableArtifactComponent } from '../table-artifact/table-artifact.component';
import { BuildDashboardComponent } from '../build-dashboard/build-dashboard.component';
import { StepGuideComponent } from '../step-guide/step-guide.component';

@Component({
  selector: 'app-nexus-sidebar',
  standalone: true,
  imports: [JsonPipe, TableArtifactComponent, BuildDashboardComponent, StepGuideComponent],
  template: `
    <div class="sidebar-container">
      <!-- Header -->
      <div class="sidebar-header">
        <div class="sidebar-title">
          <span class="sidebar-icon">
            @switch (artifact.type) {
              @case ('table') { 📊 }
              @case ('build') { ⚔️ }
              @case ('guide') { 📖 }
              @default { 📄 }
            }
          </span>
          <span class="sidebar-label">
            @switch (artifact.type) {
              @case ('table') { Datos }
              @case ('build') { Build }
              @case ('guide') { Guía }
              @default { Artifact }
            }
          </span>
        </div>
        <button class="close-btn" (click)="close.emit()">✕</button>
      </div>
      
      <!-- Content -->
      <div class="sidebar-content">
        @switch (artifact.display) {
          @case ('table') {
            <app-table-artifact [data]="artifact" />
          }
          @case ('build_dashboard') {
            <app-build-dashboard [data]="artifact" />
          }
          @case ('step_guide') {
            <app-step-guide [data]="artifact" />
          }
          @case ('empty_state') {
            <div class="empty-state">
              <span class="empty-icon">🔍</span>
              <p>{{ artifact['message'] || 'Sin resultados' }}</p>
            </div>
          }
          @case ('error_state') {
            <div class="error-state">
              <span class="error-icon">❌</span>
              <p>{{ artifact['message'] || 'Error desconocido' }}</p>
            </div>
          }
          @default {
            <div class="raw-data">
              <pre>{{ artifact | json }}</pre>
            </div>
          }
        }
      </div>
      
      <!-- Footer -->
      <div class="sidebar-footer">
        <span class="timestamp">{{ formatTimestamp(artifact.timestamp) }}</span>
      </div>
    </div>
  `,
  styles: [`
    .sidebar-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: var(--glass-bg);
      backdrop-filter: var(--glass-blur);
      box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
    }
    
    .sidebar-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: var(--spacing-md) var(--spacing-lg);
      background: rgba(255, 255, 255, 0.03);
      border-bottom: 1px solid var(--glass-border);
    }
    
    .sidebar-title {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      
      .sidebar-icon {
        font-size: 1.25rem;
      }
      
      .sidebar-label {
        font-family: var(--font-display);
        font-size: 0.875rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--accent-primary);
      }
    }
    
    .close-btn {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: transparent;
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      color: var(--text-muted);
      cursor: pointer;
      transition: var(--transition-fast);
      
      &:hover {
        border-color: var(--accent-alert);
        color: var(--accent-alert);
      }
    }
    
    .sidebar-content {
      flex: 1;
      overflow-y: auto;
      padding: var(--spacing-md);
    }
    
    .sidebar-footer {
      padding: var(--spacing-sm) var(--spacing-md);
      background: var(--bg-tertiary);
      border-top: 1px solid var(--border-color);
      
      .timestamp {
        font-size: 0.75rem;
        color: var(--text-muted);
      }
    }
    
    .empty-state, .error-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 200px;
      text-align: center;
      color: var(--text-muted);
      
      .empty-icon, .error-icon {
        font-size: 3rem;
        margin-bottom: var(--spacing-md);
      }
    }
    
    .error-state {
      color: var(--accent-alert);
    }
    
    .raw-data {
      pre {
        font-size: 0.75rem;
        color: var(--text-secondary);
        white-space: pre-wrap;
        word-break: break-all;
      }
    }
  `]
})
export class NexusSidebarComponent {
  @Input({ required: true }) artifact!: Artifact;
  @Output() close = new EventEmitter<void>();

  formatTimestamp(timestamp: string): string {
    try {
      return new Date(timestamp).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return '';
    }
  }
}
