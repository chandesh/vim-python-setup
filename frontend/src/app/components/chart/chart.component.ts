import { Component, ElementRef, ViewChild, effect, inject, input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Chart, ChartData, ChartOptions, ChartType } from 'chart.js/auto';
import { ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-chart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.css']
})
export class ChartComponent {
  private themeService = inject(ThemeService);

  /** Chart.js chart type, e.g. 'bar' or 'line'. */
  type = input<ChartType>('bar');
  /** Chart.js data payload. */
  data = input<ChartData>({ labels: [], datasets: [] });
  /** Consumer-supplied Chart.js options (merged over the theme defaults). */
  options = input<ChartOptions>({});

  @ViewChild('canvas', { static: true }) private canvasRef!: ElementRef<HTMLCanvasElement>;

  private chart: Chart | null = null;
  private lastDataKey = '';

  /** Re-render when the theme or chart inputs change; skip re-animating on no-op changes. */
  private renderEffect = effect(() => {
    this.themeService.theme();
    const dataKey = JSON.stringify(this.data());
    const dataChanged = dataKey !== this.lastDataKey;
    this.lastDataKey = dataKey;
    this.renderOrUpdate(dataChanged);
  });

  ngOnDestroy(): void {
    this.chart?.destroy();
    this.chart = null;
  }

  private renderOrUpdate(animate: boolean): void {
    const ctx = this.canvasRef.nativeElement.getContext('2d');
    if (!ctx) {
      return;
    }
    const data = this.applyThemeColors();
    const options = { ...this.buildOptions(), ...this.options() } as ChartOptions;
    if (this.chart && (this.chart.config as any).type === this.type()) {
      this.chart.data = data;
      this.chart.options = options;
      this.chart.update(animate ? undefined : 'none');
    } else {
      this.chart?.destroy();
      this.chart = new Chart(ctx, { type: this.type(), data, options });
    }
  }

  /** Augment datasets with theme-aware rounded bars (gradient blue→cyan by default). */
  private applyThemeColors(): ChartData {
    const styles = getComputedStyle(document.documentElement);
    const blue = styles.getPropertyValue('--color-blue').trim() || '#268bd2';
    const cyan = styles.getPropertyValue('--color-cyan').trim() || '#2aa198';
    const data = this.data();
    return {
      ...data,
      datasets: (data.datasets ?? []).map(ds => ({
        ...ds,
        borderRadius: 6,
        backgroundColor: (ds as any).backgroundColor ?? ((context: any) => {
          const area = context.chart.chartArea;
          if (!area) {
            return blue;
          }
          const gradient = context.chart.ctx.createLinearGradient(area.left, 0, area.right, 0);
          gradient.addColorStop(0, blue);
          gradient.addColorStop(1, cyan);
          return gradient;
        })
      }))
    };
  }

  /** Theme-aware default options: label/grid colors come from CSS variables. */
  private buildOptions(): ChartOptions {
    const styles = getComputedStyle(document.documentElement);
    const text = styles.getPropertyValue('--text-secondary').trim() || '#586e75';
    const grid = styles.getPropertyValue('--border-color').trim() || '#dfd8c3';
    return {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { color: text }, grid: { color: grid } },
        y: { ticks: { color: text }, grid: { display: false } }
      }
    };
  }
}