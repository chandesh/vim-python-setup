import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Agent, Category } from '../../models/agent.model';
import { HeaderComponent } from '../header/header.component';
import { FooterComponent } from '../footer/footer.component';

@Component({
  selector: 'app-agents-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, HeaderComponent, FooterComponent],
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
  
  // Sorting
  selectedSort = 'created_at_desc';

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadCategories();
    this.loadAgents();
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

    // Parse sort selection
    const [sortBy, sortOrder] = this.selectedSort.split('_');
    const actualSortBy = sortBy === 'created' ? 'created_at' : sortBy;
    const actualSortOrder = sortBy === 'created' ? sortOrder : sortOrder;

    if (this.searchQuery.trim()) {
      // Search mode
      this.apiService.searchAgents(this.searchQuery, this.currentPage, this.limit, actualSortBy, actualSortOrder).subscribe({
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
    this.selectedSort = 'created_at_desc';
    this.currentPage = 1;
    this.loadAgents();
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
