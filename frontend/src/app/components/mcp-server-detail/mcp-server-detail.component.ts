import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { FavoritesService } from '../../services/favorites.service';
import { MCPServer } from '../../models/agent.model';
import { HeaderComponent } from '../header/header.component';
import { FooterComponent } from '../footer/footer.component';
import { FavoriteButtonComponent } from '../favorite-button/favorite-button.component';
import { LoginWallComponent } from '../login-wall/login-wall.component';

@Component({
  selector: 'app-mcp-server-detail',
  standalone: true,
  imports: [CommonModule, RouterLink, HeaderComponent, FooterComponent, FavoriteButtonComponent, LoginWallComponent],
  templateUrl: './mcp-server-detail.component.html',
  styleUrls: ['./mcp-server-detail.component.css']
})
export class McpServerDetailComponent implements OnInit {
  server: MCPServer | null = null;
  relatedServers: any[] = [];
  loading = false;
  error: string | null = null;
  notFound = false;
  restricted = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    private favoritesService: FavoritesService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        this.loadServer(id);
      }
    });
  }

  loadServer(id: string): void {
    this.loading = true;
    this.error = null;
    this.notFound = false;
    this.restricted = false;
    this.server = null;
    this.relatedServers = [];

    this.apiService.getMCPServer(id).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success && response.data) {
          const data: any = response.data;
          this.restricted = !!data?.restricted;
          if (this.restricted) {
            const t = data.server;
            this.server = {
              ...t,
              description: t.short_description,
              repository_url: '',
              category_id: t.category?.id ?? '',
              updated_at: t.created_at,
              npm_package: null,
              pypi_package: null,
              featured: false,
              tags: [],
            };
            this.relatedServers = [];
          } else {
            this.server = data.server;
            this.relatedServers = data.related_servers || [];
            this.favoritesService.refreshFavoritesState();
          }
        } else {
          this.notFound = true;
        }
      },
      error: (error) => {
        this.loading = false;
        if (error.status === 404) {
          this.notFound = true;
        } else {
          this.error = 'Failed to load server details. Please try again.';
        }
        console.error('Error loading MCP server:', error);
      }
    });
  }

  getScopeBadgeClass(scope: string): string {
    switch (scope) {
      case 'local': return 'scope-local';
      case 'cloud': return 'scope-cloud';
      case 'hybrid': return 'scope-hybrid';
      default: return 'scope-default';
    }
  }

  formatStars(count: number): string {
    if (count >= 1000) {
      return (count / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }
    return count.toString();
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  goBack(): void {
    this.router.navigate(['/mcp-servers']);
  }
}
