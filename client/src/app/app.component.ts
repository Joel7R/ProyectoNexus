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
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  protected nexusService = inject(NexusService);
  isMobileMenuOpen = false;

  toggleMobileMenu() {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }
}

