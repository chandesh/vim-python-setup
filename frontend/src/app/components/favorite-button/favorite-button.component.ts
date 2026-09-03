import { Component, computed, inject, input } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { FavoritesService } from '../../services/favorites.service';

@Component({
  selector: 'app-favorite-button',
  standalone: true,
  imports: [],
  templateUrl: './favorite-button.component.html',
  styleUrls: ['./favorite-button.component.css']
})
export class FavoriteButtonComponent {
  private authService = inject(AuthService);
  private favoritesService = inject(FavoritesService);
  private router = inject(Router);

  /** ID of the agent or MCP server this button toggles. */
  itemId = input.required<string>();

  /** Type of item this button toggles, so the favorite targets the right entity. */
  itemType = input<'agent' | 'mcp-server'>('agent');

  /** Visual style: compact heart icon or full labeled button. */
  variant = input<'icon' | 'button'>('icon');

  /** Whether the item is currently favorited by the signed-in user. */
  isFavorited = computed(() => {
    const id = this.itemId();
    return this.authService.isAuthenticated() && this.favoritesService.isFavorited(id);
  });

  onToggle(event: Event): void {
    event.preventDefault();
    event.stopPropagation();

    // Require sign-in before favoriting; return here afterwards
    if (!this.authService.isAuthenticated()) {
      this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
      return;
    }

    const id = this.itemId();
    const favoriteId = this.favoritesService.getFavoriteId(id);

    if (favoriteId) {
      this.favoritesService.removeFromFavorites(favoriteId).subscribe({
        error: (err) => console.error('Error removing favorite:', err)
      });
    } else {
      const request = this.itemType() === 'agent'
        ? this.favoritesService.addToFavorites(id)
        : this.favoritesService.addToFavorites(undefined, id);
      request.subscribe({
        error: (err) => console.error('Error adding favorite:', err)
      });
    }
  }
}
