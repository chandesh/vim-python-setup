import { Component, input } from '@angular/core';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-dashboard-greeting',
  standalone: true,
  templateUrl: './dashboard-greeting.component.html',
  styleUrls: ['./dashboard-greeting.component.css']
})
export class DashboardGreetingComponent {
  user = input<User | null>(null);

  get greeting(): string {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }

  get today(): string {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric'
    });
  }
}
