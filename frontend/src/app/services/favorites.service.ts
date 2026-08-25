import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { ApiResponse } from '../models/agent.model';
import { AuthService } from './auth.service';
import { ToastService } from './toast.service';

export interface FavoriteItem {
  id: string;
  created_at: string;
  agent: {
    id: string;
    name: string;
    slug: string;
    short_description: string;
    logo_url: string | null;
    pricing_model: 'free' | 'freemium' | 'paid';
    featured: boolean;
  } | null;
  mcp_server: {
    id: string;
    name: string;
    slug: string;
    description: string;
    language: string;
    logo_url: string | null;
    star_count: number;
    scope: 'local' | 'cloud' | 'hybrid';
  } | null;
}

export interface FavoriteListResponse {
  favorites: FavoriteItem[];
  total: number;
  page: number;
  limit: number;
}

@Injectable({
  providedIn: 'root'
})
export class FavoritesService {
  private http = inject(HttpClient);
  private authService = inject(AuthService);
  private toastService = inject(ToastService);
  private favoritesUrl = 'http://localhost:8333/api/v1/favorites';

  /** itemId -> favoriteId for the signed-in user. */
  private readonly favoriteMap = signal<Map<string, string>>(new Map());

  /** IDs of all favorited items for the signed-in user. */
  readonly favoriteItemIds = computed(() => new Set(this.favoriteMap().keys()));

  isFavorited(itemId: string): boolean {
    return this.favoriteMap().has(itemId);
  }

  getFavoriteId(itemId: string): string | undefined {
    return this.favoriteMap().get(itemId);
  }

  addToFavorites(agentId?: string, mcpServerId?: string): Observable<ApiResponse<FavoriteItem>> {
    const body = agentId ? { agent_id: agentId } : { mcp_server_id: mcpServerId };
    return this.http.post<ApiResponse<FavoriteItem>>(this.favoritesUrl, body).pipe(
      tap({
        next: () => this.toastService.success('Added to favorites'),
        error: () => this.toastService.error('Could not add to favorites')
      }),
      tap(() => this.refreshFavoritesState())
    );
  }

  removeFromFavorites(favoriteId: string, silent: boolean = false): Observable<void> {
    return this.http.delete<void>(`${this.favoritesUrl}/${favoriteId}`).pipe(
      tap(() => {
        if (!silent) {
          this.toastService.success('Removed from favorites');
        }
        this.refreshFavoritesState();
      })
    );
  }

  getUserFavorites(page: number = 1, limit: number = 20): Observable<ApiResponse<FavoriteListResponse>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());
    return this.http.get<ApiResponse<FavoriteListResponse>>(this.favoritesUrl, { params });
  }

  checkIsFavorited(agentId?: string, mcpServerId?: string): Observable<ApiResponse<{ is_favorited: boolean; favorite_id?: string }>> {
    let params = new HttpParams();
    if (agentId) params = params.set('agent_id', agentId);
    if (mcpServerId) params = params.set('mcp_server_id', mcpServerId);
    return this.http.get<ApiResponse<{ is_favorited: boolean; favorite_id?: string }>>(`${this.favoritesUrl}/check`, { params });
  }

  /**
   * Load all of the user's favorites into local state so listing pages can
   * render favorite icon states without one request per card.
   */
  refreshFavoritesState(): void {
    if (!this.authService.isAuthenticated()) {
      this.favoriteMap.set(new Map());
      return;
    }
    this.getUserFavorites(1, 100).subscribe({
      next: (response) => {
        const map = new Map<string, string>();
        if (response.success && response.data) {
          for (const item of response.data.favorites) {
            const targetId = item.agent?.id ?? item.mcp_server?.id;
            if (targetId) {
              map.set(targetId, item.id);
            }
          }
        }
        this.favoriteMap.set(map);
      },
      error: (error) => console.error('Error loading favorites state:', error)
    });
  }
}
