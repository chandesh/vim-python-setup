import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FavoritesService, FavoriteItem } from '../../services/favorites.service';

@Component({
  selector: 'app-favorites-section',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './favorites-section.component.html',
  styleUrls: ['./favorites-section.component.css']
})
export class FavoritesSectionComponent implements OnInit {
  favorites: FavoriteItem[] = [];
  loading = true;
  error: string | null = null;

  constructor(private favoritesService: FavoritesService) {}

  ngOnInit(): void {
    this.loadFavorites();
  }

  loadFavorites(): void {
    this.loading = true;
    this.error = null;
    this.favoritesService.getUserFavorites(1, 6).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success && response.data) {
          this.favorites = response.data.favorites;
        } else {
          this.error = 'Could not load your favorites.';
        }
      },
      error: () => {
        this.loading = false;
        this.error = 'Could not load your favorites.';
      }
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
}
