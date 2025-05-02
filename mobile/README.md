# Mobile

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 18.0.5.

## Configuration

- Proxy `/api` to Python backend via `proxy.conf.json` (#file:mobile/proxy.conf.json)
- Environment files:
  - `src/environments/environment.ts` (#file:mobile/src/environments/environment.ts) for development
  - `src/environments/environment.prod.ts` (#file:mobile/src/environments/environment.prod.ts) for production

## Development

```bash
# Install dependencies
npm install

# Serve with proxy to Python backend
npm start -- --proxy-config proxy.conf.json
```

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Capacitor Mobile Build

```bash
# Install Capacitor CLI
npm install --save @capacitor/core @capacitor/cli

# Initialize Capacitor project
npm run cap:init

# Add Android and iOS platforms
npm run cap:add:android
npm run cap:add:ios

# Copy web assets to native projects
npm run cap:copy

# Open native IDEs
npm run cap:open:android
npm run cap:open:ios
```

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.
