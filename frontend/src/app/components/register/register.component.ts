import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AbstractControl, ReactiveFormsModule, FormBuilder, ValidationErrors, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { HeaderComponent } from '../header/header.component';
import { FooterComponent } from '../footer/footer.component';

/** Password strength: min 8 chars, at least one letter and one number. */
function passwordStrength(control: AbstractControl): ValidationErrors | null {
  const value: string = control.value || '';
  if (!value) {
    return null; // 'required' handles empties
  }
  const hasLetter = /[a-zA-Z]/.test(value);
  const hasNumber = /\d/.test(value);
  return hasLetter && hasNumber && value.length >= 8 ? null : { passwordStrength: true };
}

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  loading = signal(false);
  errorMessage = signal<string | null>(null);

  registerForm = this.fb.nonNullable.group({
    username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50), Validators.pattern(/^[a-zA-Z0-9_-]+$/)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, passwordStrength]]
  });

  get username() { return this.registerForm.controls.username; }
  get email() { return this.registerForm.controls.email; }
  get password() { return this.registerForm.controls.password; }

  onSubmit(): void {
    if (this.registerForm.invalid || this.loading()) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    const { email, username, password } = this.registerForm.getRawValue();

    // Register, then auto-login for a smooth onboarding flow
    this.authService.register(email, username, password).subscribe({
      next: (response) => {
        if (response.success) {
          this.authService.login(email, password).subscribe({
            next: () => {
              this.authService.loadCurrentUser().subscribe(() => {
                this.router.navigateByUrl('/');
              });
            },
            error: () => {
              // Account created but auto-login failed; send user to sign in manually
              this.router.navigate(['/login']);
            }
          });
        } else {
          this.loading.set(false);
          this.errorMessage.set('Registration failed. Please try again.');
        }
      },
      error: (error) => {
        this.loading.set(false);
        if (error.status === 400) {
          this.errorMessage.set(error.error?.detail || 'Email or username is already taken.');
        } else {
          this.errorMessage.set('Registration failed. Please check your connection and try again.');
        }
        console.error('Registration error:', error);
      }
    });
  }
}
