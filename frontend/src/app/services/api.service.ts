import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiResponse, Agent, AgentListResponse, Category, MCPServer, MCPServerListResponse } from '../models/agent.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8333/api/v1';

  constructor(private http: HttpClient) {}

  // Agents
  getAgents(page: number = 1, limit: number = 20, filters?: {
    category_id?: string;
    pricing_model?: string;
    featured?: boolean;
    sort_by?: string;
    sort_order?: string;
  }): Observable<ApiResponse<AgentListResponse>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());

    if (filters?.category_id) {
      params = params.set('category_id', filters.category_id);
    }
    if (filters?.pricing_model) {
      params = params.set('pricing_model', filters.pricing_model);
    }
    if (filters?.featured !== undefined) {
      params = params.set('featured', filters.featured.toString());
    }
    if (filters?.sort_by) {
      params = params.set('sort_by', filters.sort_by);
    }
    if (filters?.sort_order) {
      params = params.set('sort_order', filters.sort_order);
    }

    return this.http.get<ApiResponse<AgentListResponse>>(`${this.apiUrl}/agents`, { params });
  }

  searchAgents(query: string, page: number = 1, limit: number = 20, sort_by?: string, sort_order?: string): Observable<ApiResponse<AgentListResponse>> {
    let params = new HttpParams()
      .set('q', query)
      .set('page', page.toString())
      .set('limit', limit.toString());

    if (sort_by) {
      params = params.set('sort_by', sort_by);
    }
    if (sort_order) {
      params = params.set('sort_order', sort_order);
    }

    return this.http.get<ApiResponse<AgentListResponse>>(`${this.apiUrl}/agents/search`, { params });
  }

  getAgent(id: string): Observable<ApiResponse<Agent>> {
    return this.http.get<ApiResponse<Agent>>(`${this.apiUrl}/agents/${id}`);
  }

  // Categories
  getCategories(page: number = 1, limit: number = 100): Observable<ApiResponse<{ categories: Category[]; total: number; page: number; limit: number }>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());

    return this.http.get<ApiResponse<{ categories: Category[]; total: number; page: number; limit: number }>>(`${this.apiUrl}/categories`, { params });
  }

  // MCP Servers
  getMCPServers(page: number = 1, limit: number = 12, filters?: {
    category_id?: string;
    language?: string;
    scope?: string;
    featured?: boolean;
    sort_by?: string;
    sort_order?: string;
  }): Observable<ApiResponse<MCPServerListResponse>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());

    if (filters?.category_id) {
      params = params.set('category_id', filters.category_id);
    }
    if (filters?.language) {
      params = params.set('language', filters.language);
    }
    if (filters?.scope) {
      params = params.set('scope', filters.scope);
    }
    if (filters?.featured !== undefined) {
      params = params.set('featured', filters.featured.toString());
    }
    if (filters?.sort_by) {
      params = params.set('sort_by', filters.sort_by);
    }
    if (filters?.sort_order) {
      params = params.set('sort_order', filters.sort_order);
    }

    return this.http.get<ApiResponse<MCPServerListResponse>>('http://localhost:8333/api/mcp-servers', { params });
  }

  searchMCPServers(query: string, page: number = 1, limit: number = 12, sort_by?: string, sort_order?: string): Observable<ApiResponse<MCPServerListResponse>> {
    let params = new HttpParams()
      .set('query', query)
      .set('page', page.toString())
      .set('limit', limit.toString());

    if (sort_by) {
      params = params.set('sort_by', sort_by);
    }
    if (sort_order) {
      params = params.set('sort_order', sort_order);
    }

    return this.http.get<ApiResponse<MCPServerListResponse>>('http://localhost:8333/api/mcp-servers/search', { params });
  }

  getMCPServer(id: string): Observable<ApiResponse<{ mcp_server: MCPServer }>> {
    return this.http.get<ApiResponse<{ mcp_server: MCPServer }>>(`http://localhost:8333/api/mcp-servers/${id}`);
  }

  getLanguages(): Observable<ApiResponse<{ languages: string[] }>> {
    return this.http.get<ApiResponse<{ languages: string[] }>>('http://localhost:8333/api/mcp-servers/languages/list');
  }
}
