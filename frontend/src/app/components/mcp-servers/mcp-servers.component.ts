import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { FavoritesService } from '../../services/favorites.service';
import { MCPServer, Category } from '../../models/agent.model';
import { HeaderComponent } from '../header/header.component';
import { FooterComponent } from '../footer/footer.component';
import { FavoriteButtonComponent } from '../favorite-button/favorite-button.component';

@Component({
  selector: 'app-mcp-servers',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, HeaderComponent, FooterComponent, FavoriteButtonComponent],
  templateUrl: './mcp-servers.component.html',
  styleUrls: ['./mcp-servers.component.css']
})
export class McpServersComponent implements OnInit {
  servers: MCPServer[] = [];
  categories: Category[] = [];
  languages: string[] = [];
  loading = false;
  error: string | null = null;
  
  // Pagination
  currentPage = 1;
  totalPages = 1;
  totalServers = 0;
  limit = 12;
  
  // Filters
  searchQuery = '';
  selectedCategory = '';
  selectedLanguage = '';
  selectedScope = '';
  showFeaturedOnly = false;
  
  // Sorting
  selectedSort = 'star_count_desc';

  constructor(
    private apiService: ApiService,
    private favoritesService: FavoritesService
  ) {}

  ngOnInit(): void {
    this.loadCategories();
    this.loadLanguages();
    this.loadServers();
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

  loadLanguages(): void {
    this.apiService.getLanguages().subscribe({
      next: (response) => {
        if (response.success && response.data) {
          this.languages = response.data.languages;
        }
      },
      error: (error) => {
        console.error('Error loading languages:', error);
      }
    });
  }

  loadServers(): void {
    this.loading = true;
    this.error = null;

    // Parse sort selection
    const parts = this.selectedSort.split('_');
    let sortBy, sortOrder;
    
    if (parts.length === 3) {
      // Handle cases like 'star_count_desc' or 'view_count_desc'
      sortBy = `${parts[0]}_${parts[1]}`;
      sortOrder = parts[2];
    } else {
      // Handle cases like 'name_desc' or 'name_asc'
      sortBy = parts[0];
      sortOrder = parts[1];
    }

    if (this.searchQuery.trim()) {
      // Search mode
      this.apiService.searchMCPServers(this.searchQuery, this.currentPage, this.limit, sortBy, sortOrder).subscribe({
        next: (response) => {
          this.handleServersResponse(response);
        },
        error: (error) => {
          this.handleError(error);
        }
      });
    } else {
      // Regular listing with filters
      const filters: any = {};
      if (this.selectedCategory) filters.category_id = this.selectedCategory;
      if (this.selectedLanguage) filters.language = this.selectedLanguage;
      if (this.selectedScope) filters.scope = this.selectedScope;
      if (this.showFeaturedOnly) filters.featured = true;
      filters.sort_by = sortBy;
      filters.sort_order = sortOrder;

      this.apiService.getMCPServers(this.currentPage, this.limit, filters).subscribe({
        next: (response) => {
          this.handleServersResponse(response);
        },
        error: (error) => {
          this.handleError(error);
        }
      });
    }
  }

  handleServersResponse(response: any): void {
    this.loading = false;
    if (response.success && response.data) {
      this.servers = response.data.servers;
      this.totalServers = response.data.total;
      this.totalPages = Math.ceil(this.totalServers / this.limit);
    }
  }

  handleError(error: any): void {
    this.loading = false;
    this.error = 'Failed to load MCP servers. Please try again.';
    console.error('Error loading servers:', error);
  }

  onSearch(): void {
    this.currentPage = 1;
    this.loadServers();
  }

  onFilterChange(): void {
    this.currentPage = 1;
    this.loadServers();
  }

  onPageChange(page: number): void {
    this.currentPage = page;
    this.loadServers();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  clearFilters(): void {
    this.searchQuery = '';
    this.selectedCategory = '';
    this.selectedLanguage = '';
    this.selectedScope = '';
    this.showFeaturedOnly = false;
    this.selectedSort = 'star_count_desc';
    this.currentPage = 1;
    this.loadServers();
  }

  getScopeBadgeClass(scope: string): string {
    switch (scope) {
      case 'local': return 'scope-local';
      case 'cloud': return 'scope-cloud';
      case 'hybrid': return 'scope-hybrid';
      default: return 'scope-default';
    }
  }

  getCategoryName(categoryId: string): string {
    const category = this.categories.find(c => c.id === categoryId);
    return category ? category.name : '';
  }

  formatStars(stars: number): string {
    if (stars >= 1000) {
      return `${(stars / 1000).toFixed(1)}k`;
    }
    return stars.toString();
  }

  getPageNumbers(): number[] {
    return Array.from({ length: this.totalPages }, (_, i) => i + 1);
  }
}
