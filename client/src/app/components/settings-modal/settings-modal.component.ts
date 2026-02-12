import { Component, EventEmitter, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LlmSettingsService } from '../../services/llm-settings.service';

@Component({
    selector: 'app-settings-modal',
    imports: [CommonModule, FormsModule],
    template: `
    <div class="modal-overlay" (click)="close.emit()">
      <div class="modal-content" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <h3>⚙️ AI Configuration</h3>
          <button class="close-btn" (click)="close.emit()">✕</button>
        </div>

        <div class="modal-body">
          <div class="setting-group">
            <label>AI Provider</label>
            <div class="provider-selector">
              <button 
                [class.active]="settingsService.settings().provider === 'ollama'"
                (click)="selectProvider('ollama')"
                class="provider-btn">
                🦙 Ollama (Local)
              </button>
              <button 
                [class.active]="settingsService.settings().provider === 'gemini'"
                (click)="selectProvider('gemini')"
                class="provider-btn">
                ✨ Gemini (Cloud)
              </button>
            </div>
            <p class="helper-text">
              @if (selectedProvider === 'ollama') {
                Runs locally on your machine. Private, free, but requires hardware resources.
              } @else {
                Runs on Google's cloud. Faster, smarter, but requires an API Key.
              }
            </p>
          </div>

          @if (selectedProvider === 'gemini') {
            <div class="setting-group">
              <label>Gemini API Key</label>
              <div class="input-wrapper">
                <input 
                  type="password" 
                  [(ngModel)]="apiKey" 
                  placeholder="Enter your Google Gemini API Key"
                  class="api-input">
                @if (settingsService.settings().has_key && !apiKey) {
                  <span class="key-status">✅ Key saved</span>
                }
              </div>
              <p class="helper-text">
                <a href="https://aistudio.google.com/app/apikey" target="_blank">Get your API Key here</a>
              </p>
            </div>
          }
        </div>

        <div class="modal-footer">
          <button class="cancel-btn" (click)="close.emit()">Cancel</button>
          <button 
            class="save-btn" 
            [disabled]="settingsService.loading() || (selectedProvider === 'gemini' && !apiKey && !settingsService.settings().has_key)"
            (click)="save()">
            {{ settingsService.loading() ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>
  `,
    styles: [`
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(5px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 2000;
      animation: fadeIn 0.2s ease-out;
    }

    .modal-content {
      background: var(--bg-secondary);
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-lg);
      width: 90%;
      max-width: 500px;
      box-shadow: 0 0 40px rgba(0, 0, 0, 0.5);
      animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .modal-header {
      padding: var(--spacing-lg);
      border-bottom: 1px solid var(--glass-border);
      display: flex;
      justify-content: space-between;
      align-items: center;

      h3 {
        margin: 0;
        font-family: var(--font-display);
        color: var(--text-primary);
      }
    }

    .close-btn {
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 1.2rem;
      &:hover { color: var(--text-primary); }
    }

    .modal-body {
      padding: var(--spacing-lg);
    }

    .setting-group {
      margin-bottom: var(--spacing-lg);

      label {
        display: block;
        margin-bottom: var(--spacing-sm);
        color: var(--text-secondary);
        font-size: 0.9rem;
      }
    }

    .provider-selector {
      display: flex;
      gap: var(--spacing-md);
      margin-bottom: var(--spacing-xs);
    }

    .provider-btn {
      flex: 1;
      padding: var(--spacing-md);
      background: var(--bg-tertiary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.2s;
      font-weight: 500;

      &:hover {
        border-color: var(--accent-primary);
        background: rgba(0, 243, 255, 0.05);
      }

      &.active {
        background: rgba(0, 243, 255, 0.1);
        border-color: var(--accent-primary);
        color: var(--accent-primary);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.1);
      }
    }

    .helper-text {
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: var(--spacing-xs);

      a {
        color: var(--accent-primary);
        text-decoration: none;
        &:hover { text-decoration: underline; }
      }
    }

    .input-wrapper {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
    }

    .api-input {
      width: 100%;
      padding: var(--spacing-md);
      background: var(--bg-tertiary);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      color: var(--text-primary);
      font-family: var(--font-mono);

      &:focus {
        outline: none;
        border-color: var(--accent-primary);
      }
    }

    .key-status {
      font-size: 0.8rem;
      color: var(--accent-success);
      white-space: nowrap;
    }

    .modal-footer {
      padding: var(--spacing-md) var(--spacing-lg);
      border-top: 1px solid var(--glass-border);
      display: flex;
      justify-content: flex-end;
      gap: var(--spacing-md);
      background: rgba(0, 0, 0, 0.2);
      border-radius: 0 0 var(--radius-lg) var(--radius-lg);
    }

    .cancel-btn {
      background: none;
      border: 1px solid transparent;
      color: var(--text-secondary);
      padding: var(--spacing-sm) var(--spacing-lg);
      cursor: pointer;
      border-radius: var(--radius-md);
      
      &:hover {
        background: rgba(255, 255, 255, 0.05);
      }
    }

    .save-btn {
      background: var(--accent-primary);
      color: #000;
      border: none;
      padding: var(--spacing-sm) var(--spacing-lg);
      border-radius: var(--radius-md);
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;

      &:hover:not(:disabled) {
        box-shadow: 0 0 15px var(--accent-primary);
        transform: translateY(-1px);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes slideIn {
      from { transform: translateY(20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
  `]
})
export class SettingsModalComponent {
    @Output() close = new EventEmitter<void>();

    settingsService = inject(LlmSettingsService);

    selectedProvider: 'ollama' | 'gemini' = 'ollama';
    apiKey = '';

    constructor() {
        // Initialize state from existing settings
        const current = this.settingsService.settings();
        this.selectedProvider = current.provider;
    }

    selectProvider(provider: 'ollama' | 'gemini') {
        this.selectedProvider = provider;
    }

    save() {
        this.settingsService.updateSettings(
            this.selectedProvider,
            this.apiKey || undefined
        ).subscribe({
            next: () => this.close.emit(),
            error: (err) => console.error('Error saving settings', err)
        });
    }
}
