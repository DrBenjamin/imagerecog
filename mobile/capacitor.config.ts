import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'org.benbox.BenBox',
  appName: 'BenBox',
  webDir: 'dist/mobile/browser',
  server: {
    androidScheme: 'https'
  }
};

export default config;
