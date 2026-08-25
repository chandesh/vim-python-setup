import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { FavoritesService, FavoriteItem } from '../../services/favorites.service';
import { HeaderComponent } from '../header/header.component';
import { FooterComponent } from '../footer/footer.component';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [CommonModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.css']
})
export class UserProfileComponent implements OnInit {
  private authService = inject(AuthService);
  private favoritesService = inject(FavoritesService);

  readonly user = this.authService.user;
  readonly authServiceRef = this.authService;

  favorites = signal<FavoriteItem[]>([]);
  totalFavorites = signal(0);
  loading = signal(true);
  error = signal<string | null>(null);

  ngOnInit(): void {
    if (!this.authService.isAuthenticated()) {
      // Guard normally prevents this; defensive fallback
      this.loading.set(false);
      return;
    }
    this.loadFavorites();
  }

  loadFavorites(): void {
    this.loading.set(true);
    this.error.set(null);

    this.favoritesService.getUserFavorites(1, 100).subscribe({
      next: (response) => {
        this.loading.set(false);
        if (response.success && response.data) {
          this.favorites.set(response.data.favorites);
          this.totalFavorites.set(response.data.total);
        }
      },
      error: (err) => {
        this.loading.set(false);
        this.error.set('Failed to load your favorites. Please try again.');
        console.error('Error loading favorites:', err);
      }
    });
  }

  removeFavorite(item: FavoriteItem): void {
    this.favoritesService.removeFromFavorites(item.id, true).subscribe({
      next: () => {
        this.favorites.update(list => list.filter(f => f.id !== item.id));
        this.totalFavorites.update(t => Math.max(0, t - 1));
      },
      error: (err) => console.error('Error removing favorite:', err)
    });
  }

  getItemName(item: FavoriteItem): string {
    return item.agent?.name ?? item.mcp_server?.name ?? 'Unknown item';
  }

  getItemRoute(item: FavoriteItem): string[] {
    return item.agent
      ? ['/agents', item.agent.id]
      : ['/mcp-servers', item.mcp_server!.id];
  }

  getItemTypeLabel(item: FavoriteItem): string {
    return item.agent ? 'AI Agent' : 'MCP Server';
  }

  getPricingBadgeClass(pricing: string): string {
    switch (pricing) {
      case 'free': return 'pricing-free';
      case 'freemium': return 'pricing-freemium';
      case 'paid': return 'pricing-paid';
      default: return 'pricing-default';
    }
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}
