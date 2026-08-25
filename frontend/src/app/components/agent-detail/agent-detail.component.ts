import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { FavoritesService } from '../../services/favorites.service';
import { AuthService } from '../../services/auth.service';
import { AgentDetail } from '../../models/agent.model';
import { HeaderComponent } from '../header/header.component';
import { FooterComponent } from '../footer/footer.component';
import { FavoriteButtonComponent } from '../favorite-button/favorite-button.component';

@Component({
  selector: 'app-agent-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, HeaderComponent, FooterComponent, FavoriteButtonComponent],
  templateUrl: './agent-detail.component.html',
  styleUrls: ['./agent-detail.component.css']
})
export class AgentDetailComponent implements OnInit {
  agent: AgentDetail | null = null;
  loading = false;
  error: string | null = null;
  notFound = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    private favoritesService: FavoritesService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.loadAgent(id);
      }
    });
  }

  loadAgent(id: string): void {
    this.loading = true;
    this.error = null;
    this.notFound = false;
    this.agent = null;

    this.apiService.getAgent(id).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success && response.data) {
          this.agent = response.data;
          this.favoritesService.refreshFavoritesState();
        } else {
          this.notFound = true;
        }
      },
      error: (error) => {
        this.loading = false;
        if (error.status === 404) {
          this.notFound = true;
        } else {
          this.error = 'Failed to load agent details. Please try again.';
        }
        console.error('Error loading agent:', error);
      }
    });
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

  goBack(): void {
    this.router.navigate(['/agents']);
  }
}
