import { Component } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'BenBox';

  urlSafe: SafeResourceUrl | null = null;
  buttonsVisible = true;
  baseUrl = 'http://212.227.102.172:8501/?embed=true&angular=true';

  loadQuery(query: number): void {
    const url = `${this.baseUrl}&query=${query}`;
    this.urlSafe = this.sanitizer.bypassSecurityTrustResourceUrl(url);
    this.buttonsVisible = false;
  }

  constructor(private sanitizer: DomSanitizer) {
    // defer iframe loading until user clicks a button
  }
}