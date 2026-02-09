/**
 * Table Artifact Component
 * Displays news and comparisons in table format
 */
import { Component, Input } from '@angular/core';
import { UpperCasePipe } from '@angular/common';

@Component({
  selector: 'app-table-artifact',
  standalone: true,
  imports: [UpperCasePipe],
  template: `
    <div class="table-artifact">
      @if (data['rows'] && data['rows'].length > 0) {
        <div class="table-wrapper">
          <table class="nexus-table">
            <thead>
              <tr>
                @for (col of data['columns'] || []; track col.key) {
                  <th>{{ col.label }}</th>
                }
              </tr>
            </thead>
            <tbody>
              @for (row of data['rows']; track $index) {
                <tr (click)="onRowClick(row)">
                  @for (col of data['columns'] || []; track col.key) {
                    <td>
                      @if (col.key === 'url') {
                        <a [href]="row[col.key]" target="_blank" class="table-link">
                          Ver →
                        </a>
                      } @else if (col.key === 'importance') {
                        <span class="importance-badge" [class]="'importance--' + row[col.key]">
                          {{ row[col.key] | uppercase }}
                        </span>
                      } @else {
                        {{ row[col.key] }}
                      }
                    </td>
                  }
                </tr>
              }
            </tbody>
          </table>
        </div>
        
        @if (data['pagination']) {
          <div class="table-pagination">
            <span class="pagination-info">
              Mostrando {{ data['rows'].length }} resultados
            </span>
          </div>
        }
      } @else {
        <div class="no-data">
          <span>📭</span>
          <p>No hay datos disponibles</p>
        </div>
      }
    </div>
  `,
  styles: [`
    .table-artifact {
      width: 100%;
    }
    
    .table-wrapper {
      overflow-x: auto;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-md);
    }
    
    .nexus-table {
      width: 100%;
      border-collapse: collapse;
      
      th {
        padding: var(--spacing-sm) var(--spacing-md);
        text-align: left;
        font-family: var(--font-display);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--accent-primary);
        background: rgba(255, 255, 255, 0.05);
        border-bottom: 1px solid var(--glass-border);
        white-space: nowrap;
      }
      
      td {
        padding: var(--spacing-sm) var(--spacing-md);
        border-bottom: 1px solid var(--glass-border);
        font-size: 0.875rem;
        color: var(--text-secondary);
      }
      
      tr {
        transition: var(--transition-fast);
        cursor: pointer;
        
        &:hover td {
          background: var(--bg-hover);
          color: var(--text-primary);
        }
        
        &:last-child td {
          border-bottom: none;
        }
      }
    }
    
    .table-link {
      color: var(--accent-primary);
      font-size: 0.75rem;
      
      &:hover {
        text-decoration: underline;
      }
    }
    
    .importance-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      font-size: 0.65rem;
      font-weight: 600;
      letter-spacing: 0.05em;
      
      &.importance--high {
        background: rgba(255, 0, 85, 0.2);
        color: var(--accent-alert);
        border: 1px solid var(--accent-alert);
      }
      
      &.importance--medium {
        background: rgba(255, 204, 0, 0.2);
        color: var(--accent-warning);
        border: 1px solid var(--accent-warning);
      }
      
      &.importance--low {
        background: rgba(0, 255, 136, 0.2);
        color: var(--accent-success);
        border: 1px solid var(--accent-success);
      }
    }
    
    .table-pagination {
      display: flex;
      justify-content: center;
      padding: var(--spacing-md);
      
      .pagination-info {
        font-size: 0.75rem;
        color: var(--text-muted);
      }
    }
    
    .no-data {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: var(--spacing-xl);
      color: var(--text-muted);
      
      span {
        font-size: 2rem;
        margin-bottom: var(--spacing-sm);
      }
    }
  `]
})
export class TableArtifactComponent {
  @Input({ required: true }) data: any;

  onRowClick(row: any): void {
    if (row.url) {
      window.open(row.url, '_blank');
    }
  }
}
