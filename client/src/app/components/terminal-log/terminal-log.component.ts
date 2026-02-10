import { Component, Input, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-terminal-log',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="terminal-window glass-card">
      <div class="terminal-header">
        <span class="terminal-title">> NEXUS_CORE_LOGS</span>
        <div class="terminal-controls">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
        </div>
      </div>
      <div class="terminal-body" #scrollContainer>
        <div *ngFor="let log of logs" class="log-entry">
          <span class="timestamp">[{{ getCurrentTime() }}]</span>
          <span class="arrow">></span>
          <span class="content">{{ log }}</span>
        </div>
        <div *ngIf="isThinking" class="log-entry typing">
          <span class="content">_</span>
        </div>
      </div>
    </div>
  `,
    styles: [`
    .terminal-window {
      display: flex;
      flex-direction: column;
      height: 150px;
      margin-top: var(--spacing-md);
      overflow: hidden;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.75rem;
      border: 1px solid var(--border-color);
    }

    .terminal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 4px 8px;
      background: rgba(0, 0, 0, 0.5);
      border-bottom: 1px solid var(--border-color);
    }

    .terminal-title {
      color: var(--text-muted);
      font-weight: bold;
    }

    .terminal-controls {
      display: flex;
      gap: 4px;
    }

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }
    .red { background: #ff5f56; }
    .yellow { background: #ffbd2e; }
    .green { background: #27c93f; }

    .terminal-body {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
      background: rgba(0, 20, 0, 0.2);
    }

    .log-entry {
      margin-bottom: 2px;
      color: #00ff88; /* Matrix Green */
      line-height: 1.4;
      opacity: 0;
      animation: fade-in 0.2s forwards;
    }

    .timestamp {
      color: var(--text-muted);
      margin-right: 8px;
    }

    .arrow {
      color: var(--accent-primary);
      margin-right: 8px;
    }

    .typing {
      animation: blink 1s infinite;
      opacity: 1;
    }

    @keyframes blink {
      0%, 100% { opacity: 0; }
      50% { opacity: 1; }
    }

    @keyframes fade-in {
      to { opacity: 1; }
    }
  `]
})
export class TerminalLogComponent implements AfterViewChecked {
    @Input() logs: string[] = [];
    @Input() isThinking: boolean = false;
    @ViewChild('scrollContainer') private scrollContainer!: ElementRef;

    ngAfterViewChecked() {
        this.scrollToBottom();
    }

    getCurrentTime(): string {
        const now = new Date();
        return now.toISOString().split('T')[1].split('.')[0];
    }

    private scrollToBottom(): void {
        try {
            this.scrollContainer.nativeElement.scrollTop = this.scrollContainer.nativeElement.scrollHeight;
        } catch (err) { }
    }
}
