import { Injectable, signal } from '@angular/core';

export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error';
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  private nextId = 0;
  private readonly toastsSignal = signal<Toast[]>([]);

  readonly toasts = this.toastsSignal.asReadonly();

  show(message: string, type: 'success' | 'error' = 'success'): void {
    const toast: Toast = { id: ++this.nextId, message, type };
    this.toastsSignal.update(list => [...list, toast]);

    // Auto-dismiss after a short display window
    setTimeout(() => this.dismiss(toast.id), 2600);
  }

  success(message: string): void {
    this.show(message, 'success');
  }

  error(message: string): void {
    this.show(message, 'error');
  }

  dismiss(id: number): void {
    this.toastsSignal.update(list => list.filter(t => t.id !== id));
  }
}
