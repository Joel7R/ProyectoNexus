/**
 * Patch Analyst Service
 * Manages patch analysis data
 */
import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface PatchChange {
    character: string;
    stat: string;
    before: string;
    after: string;
    impact: string;
    type: 'buff' | 'nerf' | 'neutral';
    severity: 'minor' | 'moderate' | 'major';
}

export interface PatchVerdict {
    summary: string;
    meta_shift: string;
    direction: string;
    affected_characters: string[];
    tier_prediction: string;
    buff_count: number;
    nerf_count: number;
}

export interface PatchAnalysis {
    success: boolean;
    game: string;
    patch: string;
    changes: PatchChange[];
    verdict: PatchVerdict;
}

@Injectable({
    providedIn: 'root'
})
export class PatchAnalystService {
    private http = inject(HttpClient);
    private apiUrl = 'http://localhost:8000/api/patch';

    analysis = signal<PatchAnalysis | null>(null);
    isLoading = signal(false);
    error = signal<string | null>(null);

    async analyzePatch(game: string, patchVersion?: string, mainCharacter?: string) {
        this.isLoading.set(true);
        this.error.set(null);

        try {
            const response: any = await this.http.post(`${this.apiUrl}/analyze`, {
                game,
                patch_version: patchVersion,
                main_character: mainCharacter
            }).toPromise();

            if (response.success) {
                this.analysis.set(response);
            } else {
                this.error.set(response.message || 'Failed to analyze patch');
            }
        } catch (err: any) {
            this.error.set(err.message || 'Error analyzing patch');
        } finally {
            this.isLoading.set(false);
        }
    }

    getBuffs(): PatchChange[] {
        return this.analysis()?.changes.filter(c => c.type === 'buff') || [];
    }

    getNerfs(): PatchChange[] {
        return this.analysis()?.changes.filter(c => c.type === 'nerf') || [];
    }
}
