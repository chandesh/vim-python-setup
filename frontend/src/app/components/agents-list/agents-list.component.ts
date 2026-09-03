import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { FavoritesService } from '../../services/favorites.service';
import { AuthService } from '../../services/auth.service';
import { Agent, Category } from '../../models/agent.model';
import { HeaderComponent } from '../header/header.component';
import { FooterComponent } from '../footer/footer.component';
import { FavoriteButtonComponent } from '../favorite-button/favorite-button.component';

@Component({
  selector: 'app-agents-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, HeaderComponent, FooterComponent, FavoriteButtonComponent],
  templateUrl: './agents-list.component.html',
  styleUrls: ['./agents-list.component.css']
})
export class AgentsListComponent implements OnInit {
  agents: Agent[] = [];
  categories: Category[] = [];
  loading = false;
  error: string | null = null;

  // Pagination
  currentPage = 1;
  totalPages = 1;
  totalAgents = 0;
  limit = 12;

  // Filters
  searchQuery = '';
  selectedCategory = '';
  selectedPricing = '';
  showFeaturedOnly = false;
  selectedDatePreset = '';
  customDateFrom = '';
  customDateTo = '';

  // Sorting
  selectedSort = 'created_at_desc';

  constructor(
    private apiService: ApiService,
    private favoritesService: FavoritesService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadCategories();
    this.loadAgents();
    this.favoritesService.refreshFavoritesState();
  }

  loadCategories(): void {
    this.apiService.getCategories().subscribe({
      next: (response) => {
        if (response.success && response.data) {
          this.categories = response.data.categories;
        }
      },
      error: (error) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  loadAgents(): void {
    this.loading = true;
    this.error = null;
    const dateRange = this.resolveDateRange();

    // Parse sort selection
    const [sortBy, sortOrder] = this.selectedSort.split('_');
    const actualSortBy = sortBy === 'created' ? 'created_at' : sortBy;
    const actualSortOrder = sortBy === 'created' ? sortOrder : sortOrder;

    if (this.searchQuery.trim()) {
      // Search mode
      this.apiService.searchAgents(this.searchQuery, this.currentPage, this.limit, actualSortBy, actualSortOrder, dateRange.date_from, dateRange.date_to).subscribe({
        next: (response) => {
          this.handleAgentsResponse(response);
        },
        error: (error) => {
          this.handleError(error);
        }
      });
    } else {
      // Regular listing with filters
      const filters: any = {};
      if (this.selectedCategory) filters.category_id = this.selectedCategory;
      if (this.selectedPricing) filters.pricing_model = this.selectedPricing;
      if (this.showFeaturedOnly) filters.featured = true;
      if (dateRange.date_from) filters.date_from = dateRange.date_from;
      if (dateRange.date_to) filters.date_to = dateRange.date_to;
      filters.sort_by = actualSortBy;
      filters.sort_order = actualSortOrder;

      this.apiService.getAgents(this.currentPage, this.limit, filters).subscribe({
        next: (response) => {
          this.handleAgentsResponse(response);
        },
        error: (error) => {
          this.handleError(error);
        }
      });
    }
  }

  handleAgentsResponse(response: any): void {
    this.loading = false;
    if (response.success && response.data) {
      this.agents = response.data.agents;
      this.totalAgents = response.data.total;
      this.totalPages = Math.ceil(this.totalAgents / this.limit);
    }
  }

  handleError(error: any): void {
    this.loading = false;
    this.error = 'Failed to load agents. Please try again.';
    console.error('Error loading agents:', error);
  }

  onSearch(): void {
    this.currentPage = 1;
    this.loadAgents();
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadAgents();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadAgents();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.selectedCategory = '';
    this.selectedPricing = '';
    this.showFeaturedOnly = false;
    this.selectedDatePreset = '';
    this.customDateFrom = '';
    this.customDateTo = '';
    this.selectedSort = 'created_at_desc';
    this.currentPage = 1;
    this.loadAgents();
  }

  /** Compute date_from/date_to from the preset or custom inputs. */
  resolveDateRange(): { date_from?: string; date_to?: string } {
    if (this.selectedDatePreset === 'custom') {
      if (!this.customDateFrom || !this.customDateTo) {
        return {};
      }
      return { date_from: this.customDateFrom, date_to: this.customDateTo };
    }
    if (!this.selectedDatePreset) {
      return {};
    }
    const days = parseInt(this.selectedDatePreset, 10);
    const from = new Date();
    from.setDate(from.getDate() - days);
    return { date_from: from.toISOString().slice(0, 10) };
  }

  getDateFilterLabel(): string {
    if (this.selectedDatePreset === 'custom') {
      return `Custom (${this.customDateFrom || '?'} → ${this.customDateTo || '?'})`;
    }
    return `Last ${this.selectedDatePreset} days`;
  }

  getPricingBadgeClass(pricing: string): string {
    switch (pricing) {
      case 'free': return 'pricing-free';
      case 'freemium': return 'pricing-freemium';
      case 'paid': return 'pricing-paid';
      default: return 'pricing-default';
    }
  }

  getCategoryName(categoryId: string): string {
    const category = this.categories.find(c => c.id === categoryId);
    return category ? category.name : '';
  }
}
