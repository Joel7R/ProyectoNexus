import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

export interface NewsItem {
    title: string;
    date: string;
    summary: string;
    url: string;
    image?: string;
}

export interface NewsResponse {
    summary: string;
    items: NewsItem[];
}

export interface CalendarResponse {
    summary: string;
    raw_data: any[];
}

@Injectable({
    providedIn: 'root'
})
export class ContentService {
    private http = inject(HttpClient);
    private apiUrl = 'http://localhost:8000/api'; // Adjust if needed

    getNews(category: string = 'general'): Observable<NewsResponse> {
        return this.http.post<NewsResponse>(`${this.apiUrl}/news`, { category }).pipe(
            catchError(err => {
                console.error('Error fetching news', err);
                return of({ summary: 'Failed to load news.', items: [] });
            })
        );
    }

    getCalendar(): Observable<CalendarResponse> {
        return this.http.get<CalendarResponse>(`${this.apiUrl}/calendar`).pipe(
            catchError(err => {
                console.error('Error fetching calendar', err);
                return of({ summary: 'Failed to load calendar.', raw_data: [] });
            })
        );
    }
}
