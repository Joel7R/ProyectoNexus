/**
 * Chat Stream Component
 * Real-time message visualization with thinking indicators
 */
import { Component, inject, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NexusService, ChatMessage } from '../../services/nexus.service';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-chat-stream',
  standalone: true,
  imports: [FormsModule, DatePipe],
  template: `
    <div class="chat-container">
      <!-- Messages Area -->
      <div class="chat-messages" #messagesContainer>
        @if (nexusService.messages().length === 0) {
          <div class="chat-welcome">
            <div class="chat-welcome__icon">🎮</div>
            <h2 class="chat-welcome__title">Bienvenido a Gaming Nexus</h2>
            <p class="chat-welcome__text">
              Tu asistente de gaming con información en tiempo real.
              Pregunta sobre builds, noticias, guías y más.
            </p>
            <div class="chat-welcome__examples">
              <button class="example-btn" (click)="sendExample('¿Cuál es el mejor build para Jinx en LoL?')">
                🎯 Build de Jinx en LoL
              </button>
              <button class="example-btn" (click)="sendExample('Últimas noticias de Elden Ring')">
                📰 Noticias de Elden Ring
              </button>
              <button class="example-btn" (click)="sendExample('¿Cómo derrotar a Malenia en Elden Ring?')">
                ⚔️ Guía para Malenia
              </button>
            </div>
          </div>
        }
        
        @for (message of nexusService.messages(); track message.id) {
          <div class="chat-message" [class]="'chat-message--' + message.role">
            <div class="chat-message__avatar">
              @if (message.role === 'user') {
                <span>👤</span>
              } @else if (message.role === 'thinking') {
                <span class="thinking-icon">⚡</span>
              } @else {
                <span>🤖</span>
              }
            </div>
            <div class="chat-message__content">
              <div class="chat-message__header">
                <span class="chat-message__role">
                  {{ message.role === 'user' ? 'Tú' : message.role === 'thinking' ? 'Procesando' : 'Nexus' }}
                </span>
                <span class="chat-message__time">{{ message.timestamp | date:'HH:mm' }}</span>
              </div>
              <div class="chat-message__text" [innerHTML]="formatMessage(message.content)"></div>
              
              @if (message.sources && message.sources.length > 0) {
                <div class="chat-message__sources">
                  <span class="sources-label">📚 Fuentes:</span>
                  @for (source of message.sources; track source.url) {
                    <a [href]="source.url" target="_blank" class="source-link">
                      {{ source.title }}
                    </a>
                  }
                </div>
              }
            </div>
          </div>
        }
        
        <!-- Thinking Indicator -->
        @if (nexusService.isLoading()) {
          <div class="chat-message chat-message--thinking">
            <div class="chat-message__avatar">
              <span class="thinking-icon">⚡</span>
            </div>
            <div class="chat-message__content">
              <div class="thinking-status">
                <div class="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span class="thinking-text">{{ nexusService.thinkingStatus() || 'Procesando...' }}</span>
              </div>
              @if (nexusService.elapsedTime() > 5) {
                <div class="thinking-elapsed">
                  <span class="elapsed-badge">{{ formatElapsedTime(nexusService.elapsedTime()) }}</span>
                  <button class="cancel-btn" (click)="nexusService.cancelRequest()">
                    ✕ Cancelar
                  </button>
                </div>
              }
            </div>
          </div>
        }
      </div>
      
      <!-- Input Area -->
      <div class="chat-input-container">
        <form (submit)="onSubmit($event)" class="chat-input-form">
          <input
            type="text"
            [(ngModel)]="inputMessage"
            name="message"
            class="chat-input"
            placeholder="Pregunta sobre builds, noticias, guías..."
            [disabled]="nexusService.isLoading()"
            autocomplete="off"
          />
          <button 
            type="submit" 
            class="chat-submit-btn"
            [disabled]="!inputMessage.trim() || nexusService.isLoading()"
          >
            <span class="btn-icon">➤</span>
          </button>
        </form>
        <div class="chat-input-footer">
          <span class="footer-text">Powered by Ollama + LangGraph</span>
          <button class="clear-btn" (click)="nexusService.clearHistory()">
            🗑️ Limpiar
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chat-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: transparent;
    }
    
    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: var(--spacing-lg);
      display: flex;
      flex-direction: column;
      gap: var(--spacing-md);
    }
    
    /* Welcome Screen */
    .chat-welcome {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      text-align: center;
      padding: var(--spacing-xl);
      
      &__icon {
        font-size: 5rem;
        margin-bottom: var(--spacing-lg);
        filter: drop-shadow(0 0 20px var(--accent-primary));
        animation: pulse-glow 3s ease-in-out infinite;
      }
      
      &__title {
        font-family: var(--font-display);
        font-size: 2.5rem;
        background: linear-gradient(to right, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(0, 243, 255, 0.3);
        margin-bottom: var(--spacing-md);
      }
      
      &__text {
        color: var(--text-secondary);
        font-size: 1.1rem;
        max-width: 500px;
        margin-bottom: var(--spacing-xl);
      }
      
      &__examples {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-sm);
        justify-content: center;
      }
    }
    
    .example-btn {
      padding: var(--spacing-sm) var(--spacing-md);
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      color: var(--text-secondary);
      font-family: var(--font-mono);
      font-size: 0.875rem;
      cursor: pointer;
      transition: var(--transition-normal);
      
      &:hover {
        border-color: var(--accent-primary);
        color: var(--accent-primary);
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
      }
    }
    
    /* Messages */
    .chat-message {
      display: flex;
      gap: var(--spacing-md);
      padding: var(--spacing-md);
      border-radius: var(--radius-lg);
      margin-bottom: var(--spacing-sm);
      backdrop-filter: var(--glass-blur);
      animation: fade-in 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      
      &--user {
        background: rgba(26, 26, 26, 0.4);
        border: 1px solid var(--glass-border);
        align-self: flex-end;
        max-width: 85%;
      }
      
      &--assistant {
        background: var(--glass-bg);
        border: 1px solid rgba(0, 243, 255, 0.1);
        box-shadow: var(--glass-shadow);
        max-width: 90%;
      }
      
      &--thinking {
        background: rgba(0, 243, 255, 0.05);
        border: 1px dashed rgba(0, 243, 255, 0.3);
      }
      
      &__avatar {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        border-radius: var(--radius-sm);
        background: var(--bg-secondary);
        flex-shrink: 0;
        
        .thinking-icon {
          animation: pulse-glow 1s ease-in-out infinite;
        }
      }
      
      &__content {
        flex: 1;
        min-width: 0;
      }
      
      &__header {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-xs);
      }
      
      &__role {
        font-weight: 600;
        font-size: 0.875rem;
        color: var(--accent-primary);
      }
      
      &__time {
        font-size: 0.75rem;
        color: var(--text-muted);
      }
      
      &__text {
        color: var(--text-primary);
        line-height: 1.6;
        word-wrap: break-word;
        
        :global(a) {
          color: var(--accent-primary);
          text-decoration: underline;
        }
      }
      
      &__sources {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-sm);
        margin-top: var(--spacing-md);
        padding-top: var(--spacing-sm);
        border-top: 1px solid var(--border-color);
        
        .sources-label {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        
        .source-link {
          font-size: 0.75rem;
          color: var(--accent-secondary);
          text-decoration: none;
          
          &:hover {
            color: var(--accent-primary);
            text-decoration: underline;
          }
        }
      }
    }
    
    .thinking-status {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      
      .thinking-text {
        color: var(--accent-primary);
        font-size: 0.875rem;
      }
    }

    .thinking-elapsed {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      margin-top: var(--spacing-sm);
      padding-top: var(--spacing-sm);
      border-top: 1px solid rgba(0, 243, 255, 0.1);
    }

    .elapsed-badge {
      font-size: 0.7rem;
      font-family: var(--font-mono);
      color: var(--text-muted);
      background: var(--bg-tertiary);
      padding: 2px 6px;
      border-radius: var(--radius-sm);
    }

    .cancel-btn {
      font-size: 0.75rem;
      color: var(--accent-alert);
      background: transparent;
      border: 1px solid rgba(255, 0, 85, 0.3);
      padding: 2px 8px;
      border-radius: var(--radius-sm);
      cursor: pointer;
      transition: var(--transition-fast);

      &:hover {
        background: rgba(255, 0, 85, 0.1);
        border-color: var(--accent-alert);
        box-shadow: 0 0 10px rgba(255, 0, 85, 0.2);
      }
    }
    
    /* Input Area */
    .chat-input-container {
      padding: var(--spacing-md) var(--spacing-lg);
      background: var(--bg-secondary);
      border-top: 1px solid var(--border-color);
    }
    
    .chat-input-form {
      display: flex;
      gap: var(--spacing-sm);
    }
    
    .chat-input {
      flex: 1;
      padding: var(--spacing-md);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      background: var(--bg-primary);
      color: var(--text-primary);
      font-family: var(--font-mono);
      font-size: 0.875rem;
      transition: var(--transition-fast);
      
      &:focus {
        outline: none;
        border-color: var(--accent-primary);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
      }
      
      &::placeholder {
        color: var(--text-muted);
      }
      
      &:disabled {
        opacity: 0.5;
      }
    }
    
    .chat-submit-btn {
      width: 48px;
      height: 48px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--accent-primary);
      border-radius: var(--radius-md);
      background: transparent;
      color: var(--accent-primary);
      font-size: 1.25rem;
      cursor: pointer;
      transition: var(--transition-normal);
      
      &:hover:not(:disabled) {
        background: var(--accent-primary);
        color: var(--bg-primary);
        box-shadow: var(--glow-primary);
      }
      
      &:disabled {
        opacity: 0.3;
        cursor: not-allowed;
      }
    }
    
    .chat-input-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: var(--spacing-sm);
      
      .footer-text {
        font-size: 0.75rem;
        color: var(--text-muted);
      }
      
      .clear-btn {
        padding: var(--spacing-xs) var(--spacing-sm);
        background: transparent;
        border: none;
        color: var(--text-muted);
        font-family: var(--font-mono);
        font-size: 0.75rem;
        cursor: pointer;
        transition: var(--transition-fast);
        
        &:hover {
          color: var(--accent-alert);
        }
      }
    }
    
    @keyframes fade-in {
      from { 
        opacity: 0; 
        transform: translateY(10px); 
      }
      to { 
        opacity: 1; 
        transform: translateY(0); 
      }
    }
  `]
})
export class ChatStreamComponent implements AfterViewChecked {
  protected nexusService = inject(NexusService);

  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  inputMessage = '';
  private shouldScroll = false;

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  onSubmit(event: Event): void {
    event.preventDefault();
    if (this.inputMessage.trim()) {
      this.nexusService.sendMessage(this.inputMessage);
      this.inputMessage = '';
      this.shouldScroll = true;
    }
  }

  sendExample(message: string): void {
    this.nexusService.sendMessage(message);
    this.shouldScroll = true;
  }

  formatElapsedTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  }

  formatMessage(content: string): string {
    // Convert markdown links to HTML
    return content.replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" target="_blank">$1</a>'
    );
  }

  private scrollToBottom(): void {
    try {
      const container = this.messagesContainer.nativeElement;
      container.scrollTop = container.scrollHeight;
    } catch (err) { }
  }
}
