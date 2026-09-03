import { Component, input } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

@Component({
  selector: 'app-login-wall',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './login-wall.component.html',
  styleUrls: ['./login-wall.component.css']
})
export class LoginWallComponent {
  /** 'card' fits into listing grids; 'overlay' floats over blurred content */
  variant = input<'card' | 'overlay'>('card');
  /** Item type shown in copy, e.g. 'AI agents', 'MCP servers' */
  itemType = input<string>('items');
  /** Total count for "sign in to see all N" copy */
  totalCount = input<number | null>(null);
  /** When set, wall copy echoes the guest's search query */
  searchQuery = input<string | null>(null);

  constructor(private router: Router) {}

  get currentUrl(): string {
    return this.router.url;
  }
}