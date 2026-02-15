import { Component, inject, ElementRef, ViewChild, AfterViewChecked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NexusService, ChatMessage } from '../../services/nexus.service';
import { DatePipe, CommonModule } from '@angular/common';
import { TerminalLogComponent } from '../terminal-log/terminal-log.component';

@Component({
  selector: 'app-chat-stream',
  imports: [FormsModule, DatePipe, CommonModule, TerminalLogComponent],
  templateUrl: './chat-stream.component.html',
  styleUrls: ['./chat-stream.component.scss']
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

  onEnter(event: Event): void {
    // Handle Enter key for textarea
    if (this.inputMessage.trim()) {
      event.preventDefault();
      this.onSubmit(event);
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
