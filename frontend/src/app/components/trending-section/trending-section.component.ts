import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { Agent, MCPServer } from '../../models/agent.model';

@Component({
  selector: 'app-trending-section',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './trending-section.component.html',
  styleUrls: ['./trending-section.component.css']
})
export class TrendingSectionComponent implements OnInit {
  agents: Agent[] = [];
  servers: MCPServer[] = [];
  agentsLoading = true;
  serversLoading = true;
  agentsError: string | null = null;
  serversError: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadTrendingAgents();
    this.loadTrendingServers();
  }

  loadTrendingAgents(): void {
    this.agentsLoading = true;
    this.agentsError = null;
    this.apiService.getAgents(1, 5, { sort_by: 'view_count', sort_order: 'desc' }).subscribe({
      next: (response) => {
        this.agentsLoading = false;
        if (response.success && response.data) {
          this.agents = response.data.agents;
        } else {
          this.agentsError = 'Could not load trending agents.';
        }
      },
      error: () => {
        this.agentsLoading = false;
        this.agentsError = 'Could not load trending agents.';
      }
    });
  }

  loadTrendingServers(): void {
    this.serversLoading = true;
    this.serversError = null;
    this.apiService.getMCPServers(1, 5, { sort_by: 'star_count', sort_order: 'desc' }).subscribe({
      next: (response) => {
        this.serversLoading = false;
        if (response.success && response.data) {
          this.servers = response.data.servers;
        } else {
          this.serversError = 'Could not load trending MCP servers.';
        }
      },
      error: () => {
        this.serversLoading = false;
        this.serversError = 'Could not load trending MCP servers.';
      }
    });
  }

  formatCount(count: number): string {
    if (count >= 1000) {
      return (count / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }
    return count.toString();
  }
}
