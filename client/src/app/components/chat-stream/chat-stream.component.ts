import { Component, inject, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NexusService, ChatMessage } from '../../services/nexus.service';
import { DatePipe, CommonModule } from '@angular/common';
import { TerminalLogComponent } from '../terminal-log/terminal-log.component';

@Component({
    selector: 'app-chat-stream',
    imports: [FormsModule, DatePipe, CommonModule, TerminalLogComponent],
    template: `
    <div class="chat-container">
      <!-- Messages Area -->
      <div class="chat-messages" #messagesContainer>
        @if (nexusService.messages().length === 0) {
          <div class="chat-welcome">
            <div class="chat-welcome__icon">🎮</div>
            <h2 class="chat-welcome__title">GAMING NEXUS</h2>
            <p class="chat-welcome__text">
              OPERATING SYSTEM ONLINE.
              SELECT MISSION PARAMETERS.
            </p>
            <div class="chat-welcome__examples">
              <button class="example-btn glass-card" (click)="sendExample('¿Cuál es el mejor build para Jinx en LoL?')">
                🎯 JINX BUILD_
              </button>
              <button class="example-btn glass-card" (click)="sendExample('Últimas noticias de Elden Ring')">
                📰 ELDEN RING NEWS_
              </button>
              <button class="example-btn glass-card" (click)="sendExample('¿Cómo derrotar a Malenia en Elden Ring?')">
                ⚔️ GUIDE DATABASE_
              </button>
            </div>
          </div>
        }
        
        @for (message of nexusService.messages(); track message.id) {
          <div class="chat-message" [class]="'chat-message--' + message.role">
            <div class="chat-message__avatar" [class.glow]="message.role === 'assistant'">
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
                  {{ message.role === 'user' ? 'USER_ID::COMMANDER' : message.role === 'thinking' ? 'PROCESSING...' : 'NEXUS_AI::RESPONSE' }}
                </span>
                <span class="chat-message__time">
                    [{{ message.timestamp | date:'HH:mm:ss' }}]
                </span>
              </div>
              <div class="chat-message__text" [innerHTML]="formatMessage(message.content)"></div>
              
              @if (message.sources && message.sources.length > 0) {
                <div class="chat-message__sources glass-card">
                  <span class="sources-label">> SOURCE_DATA_LINKED:</span>
                  @for (source of message.sources; track source.url) {
                    <a [href]="source.url" target="_blank" class="source-link">
                      [{{ source.title }}]
                    </a>
                  }
                </div>
              }
            </div>
          </div>
        }
        
        <!-- Thinking Indicator -->
        @if (nexusService.isLoading()) {
          <div class="chat-message chat-message--thinking glass-card">
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
                <span class="thinking-text">> ANALYZING DATA STREAMS... [{{ nexusService.thinkingStatus() || 'WAIT' }}]</span>
              </div>
            </div>
          </div>
        }
      </div>
      
      <!-- Terminal Log (Only visible if there are logs or loading) -->
      @if (nexusService.isLoading() || mockLogs.length > 0) {
          <app-terminal-log 
            [logs]="mockLogs" 
            [isThinking]="nexusService.isLoading()">
          </app-terminal-log>
      }

      <!-- Input Area -->
      <div class="chat-input-container glass-card">
        <form (submit)="onSubmit($event)" class="chat-input-form">
            <div class="input-prefix">></div>
          <input
            type="text"
            [(ngModel)]="inputMessage"
            name="message"
            class="chat-input"
            placeholder="ENTER COMMAND..."
            [disabled]="nexusService.isLoading()"
            autocomplete="off"
          />
          <button 
            type="submit" 
            class="chat-submit-btn"
            [disabled]="!inputMessage.trim() || nexusService.isLoading()"
          >
            <span class="btn-icon">SEND_</span>
          </button>
        </form>
      </div>
    </div>
  `,
    styles: [`
    .chat-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: transparent;
      padding: var(--spacing-md);
      max-width: 1200px;
      margin: 0 auto;
    }
    
    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding-bottom: var(--spacing-md);
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
        animation: pulse-neon 3s ease-in-out infinite;
      }
      
      &__title {
        font-family: var(--font-display);
        font-size: 3rem;
        letter-spacing: 0.2rem;
        color: var(--accent-primary);
        text-shadow: 0 0 20px rgba(0, 243, 255, 0.5);
        margin-bottom: var(--spacing-md);
      }
      
      &__text {
        color: var(--text-secondary);
        font-family: var(--font-mono);
        font-size: 0.9rem;
        max-width: 500px;
        margin-bottom: var(--spacing-xl);
      }
      
      &__examples {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-md);
        justify-content: center;
      }
    }
    
    .example-btn {
      padding: var(--spacing-md);
      color: var(--accent-primary);
      font-family: var(--font-display);
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s;
      border: 1px solid transparent;
      
      &:hover {
        border-color: var(--accent-primary);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
        transform: translateY(-2px);
      }
    }
    
    /* Messages */
    .chat-message {
      display: flex;
      gap: var(--spacing-md);
      padding: var(--spacing-md);
      border-radius: var(--radius-lg);
      margin-bottom: var(--spacing-sm);
      animation: fade-in-up 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      
      &--user {
        border-right: 2px solid var(--accent-secondary);
        background: linear-gradient(90deg, transparent, rgba(188, 19, 254, 0.1));
        align-self: flex-end;
        max-width: 85%;
        text-align: right;
        flex-direction: row-reverse;
      }
      
      &--assistant {
        border-left: 2px solid var(--accent-primary);
        background: linear-gradient(90deg, rgba(0, 243, 255, 0.05), transparent);
        max-width: 90%;
      }
      
      &__avatar {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        border-radius: 50%;
        background: rgba(0,0,0,0.5);
        border: 1px solid var(--border-color);
        flex-shrink: 0;
        
        &.glow {
            box-shadow: 0 0 10px var(--accent-primary);
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
        font-family: var(--font-mono);
        font-size: 0.7rem;
        color: var(--text-muted);
      }
      
      &__role {
        font-weight: bold;
        color: var(--accent-primary);
      }

      .chat-message--user .chat-message__role {
          color: var(--accent-secondary);
      }
      
      &__text {
        color: var(--text-primary);
        line-height: 1.6;
        
        :global(a) {
          color: var(--accent-primary);
          text-decoration: none;
          border-bottom: 1px dotted var(--accent-primary);
        }
      }
      
      &__sources {
        margin-top: var(--spacing-md);
        padding: var(--spacing-sm);
        
        .sources-label {
          display: block;
          font-family: var(--font-mono);
          font-size: 0.7rem;
          color: var(--accent-primary);
          margin-bottom: 4px;
        }
        
        .source-link {
          font-size: 0.75rem;
          color: var(--text-secondary);
          margin-right: 8px;
          
          &:hover {
            color: var(--accent-primary);
          }
        }
      }
    }
    
    /* Input Area */
    .chat-input-container {
      padding: var(--spacing-sm) var(--spacing-lg);
      display: flex;
      align-items: center;
      margin-top: var(--spacing-md);
    }
    
    .chat-input-form {
      display: flex;
      gap: var(--spacing-sm);
      width: 100%;
      align-items: center;
    }

    .input-prefix {
        color: var(--accent-primary);
        font-family: var(--font-mono);
        font-weight: bold;
    }
    
    .chat-input {
      flex: 1;
      padding: var(--spacing-md);
      background: transparent;
      border: none;
      color: var(--text-primary);
      font-family: var(--font-mono);
      font-size: 1rem;
      caret-color: var(--accent-primary);
      
      &:focus {
        outline: none;
      }
    }
    
    .chat-submit-btn {
      padding: 0 var(--spacing-md);
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid var(--accent-primary);
      background: rgba(0, 243, 255, 0.1);
      color: var(--accent-primary);
      font-family: var(--font-display);
      font-size: 0.8rem;
      cursor: pointer;
      transition: all 0.2s;
      
      &:hover:not(:disabled) {
        background: var(--accent-primary);
        color: black;
        box-shadow: 0 0 10px var(--accent-primary);
      }
      
      &:disabled {
        opacity: 0.3;
        cursor: not-allowed;
        border-color: var(--text-muted);
      }
    }
  `]
})
export class ChatStreamComponent implements AfterViewChecked {
  protected nexusService = inject(NexusService);

  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  inputMessage = '';
  private shouldScroll = false;

  // Mock logs for demonstration - in real app would come from service
  mockLogs: string[] = [
    "Initializing connection to Nexus Core...",
    "Secure channel established.",
    "Waiting for user input..."
  ];

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
      this.mockLogs.push(`PROCESSING INPUT: "${this.inputMessage}"`);
      this.mockLogs.push("ROUTING TO ORCHESTRATOR...");
      this.inputMessage = '';
      this.shouldScroll = true;
    }
  }

  sendExample(message: string): void {
    this.nexusService.sendMessage(message);
    this.mockLogs.push(`EXECUTING MACRO: "${message}"`);
    this.shouldScroll = true;
  }

  formatMessage(content: string): string {
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
