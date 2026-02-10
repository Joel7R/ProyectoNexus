import { Routes } from '@angular/router';
import { NewsComponent } from './components/news/news.component';
import { CalendarComponent } from './components/calendar/calendar.component';
import { ChatStreamComponent } from './components/chat-stream/chat-stream.component';

export const routes: Routes = [
    { path: 'news', component: NewsComponent },
    { path: 'calendar', component: CalendarComponent },
    { path: 'time2play', loadComponent: () => import('./components/time2play/time2play.component').then(m => m.Time2PlayComponent) },
    { path: 'price-hunter', loadComponent: () => import('./components/price-hunter/price-hunter.component').then(m => m.PriceHunterComponent) },
    { path: 'lore-master', loadComponent: () => import('./components/lore-master/lore-master.component').then(m => m.LoreMasterComponent) },
    { path: 'chat', component: ChatStreamComponent },
    { path: '', redirectTo: 'news', pathMatch: 'full' },
    { path: '**', redirectTo: 'news' } // Wildcard route
];
