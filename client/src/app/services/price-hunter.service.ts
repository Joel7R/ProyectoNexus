/**
 * Price Hunter Service
 * Handles deal search and price comparison API calls
 */
import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

export interface DealData {
    store: string;
    store_id: string;
    icon: string;
    price: number;
    currency: string;
    url: string;
    is_best: boolean;
}

export interface DealSearchResult {
    success: boolean;
    game: string;
    deals: DealData[];
    best_deal: DealData | null;
    savings: number;
    savings_percent: number;
    reasoning: string[];
    message?: string;
    artifact?: {
        display: string;
        data?: {
            deals?: DealData[];
            [key: string]: any;
        };
        [key: string]: any;
    };
}

@Injectable({
    providedIn: 'root'
})
export class PriceHunterService {
    private apiUrl = 'http://localhost:8000/api/deals';

    isLoading = signal(false);
    currentDeals = signal<DealSearchResult | null>(null);
    error = signal<string | null>(null);

    constructor(private http: HttpClient) { }

    async searchDeals(gameName: string): Promise<DealSearchResult> {
        this.isLoading.set(true);
        this.error.set(null);

        try {
            const result = await firstValueFrom(
                this.http.post<DealSearchResult>(`${this.apiUrl}/search`, { game_name: gameName })
            );

            // Ensure deals array exists - extract from artifact.data if needed
            if (!result.deals && result.artifact?.data?.deals) {
                result.deals = result.artifact.data.deals;
            }

            // Ensure deals is always an array
            if (!result.deals) {
                result.deals = [];
            }

            // Find best deal if not already set
            if (!result.best_deal && result.deals.length > 0) {
                result.best_deal = result.deals.find(d => d.is_best) || result.deals[0];
            }

            this.currentDeals.set(result);
            return result;
        } catch (err: any) {
            const errorMsg = err.error?.message || 'Failed to fetch deals';
            this.error.set(errorMsg);
            throw err;
        } finally {
            this.isLoading.set(false);
        }
    }

    async compareStores(gameName: string, storeIds: string[]): Promise<DealSearchResult> {
        this.isLoading.set(true);
        this.error.set(null);

        try {
            const result = await firstValueFrom(
                this.http.post<DealSearchResult>(`${this.apiUrl}/compare`, {
                    game_name: gameName,
                    store_ids: storeIds
                })
            );

            this.currentDeals.set(result);
            return result;
        } catch (err: any) {
            const errorMsg = err.error?.message || 'Failed to compare prices';
            this.error.set(errorMsg);
            throw err;
        } finally {
            this.isLoading.set(false);
        }
    }

    clearDeals() {
        this.currentDeals.set(null);
        this.error.set(null);
    }
}
