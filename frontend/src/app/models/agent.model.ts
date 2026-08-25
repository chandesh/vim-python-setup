export interface Tag {
  id: string;
  name: string;
  slug: string;
}

export interface Agent {
  id: string;
  name: string;
  slug: string;
  description: string;
  short_description: string;
  website_url: string;
  category_id: string;
  pricing_model: 'free' | 'freemium' | 'paid';
  logo_url: string | null;
  featured: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
  category?: Category;
  tags?: Tag[];
}

export interface AgentListResponse {
  agents: Agent[];
  total: number;
  page: number;
  limit: number;
}

export interface AgentSummary {
  id: string;
  name: string;
  slug: string;
  short_description: string;
  logo_url: string | null;
  pricing_model: 'free' | 'freemium' | 'paid';
  featured: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentDetail extends Agent {
  related_agents: AgentSummary[];
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string;
  icon_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface MCPServer {
  id: string;
  name: string;
  slug: string;
  description: string;
  repository_url: string;
  language: string;
  scope: 'local' | 'cloud' | 'hybrid';
  category_id: string;
  logo_url: string | null;
  npm_package: string | null;
  pypi_package: string | null;
  star_count: number;
  created_at: string;
  updated_at: string;
  featured: boolean;
  view_count: number;
  category?: Category;
  tags?: Tag[];
}

export interface MCPServerListResponse {
  servers: MCPServer[];
  total: number;
  page: number;
  limit: number;
  total_pages?: number;
}

export interface MCPServerSummary {
  id: string;
  name: string;
  slug: string;
  description: string;
  language: string;
  logo_url: string | null;
  star_count: number;
  scope: 'local' | 'cloud' | 'hybrid';
  created_at: string;
  updated_at: string;
}

export interface MCPServerDetail {
  server: MCPServer;
  related_servers: MCPServerSummary[];
}
