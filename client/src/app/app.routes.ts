import { Routes } from '@angular/router';
import { NewsComponent } from './components/news/news.component';
import { CalendarComponent } from './components/calendar/calendar.component';
import { ChatStreamComponent } from './components/chat-stream/chat-stream.component';

export const routes: Routes = [
    { path: 'news', component: NewsComponent },
    { path: 'calendar', component: CalendarComponent },
    { path: 'chat', component: ChatStreamComponent },
    { path: '', redirectTo: 'news', pathMatch: 'full' },
    { path: '**', redirectTo: 'news' } // Wildcard route
];
