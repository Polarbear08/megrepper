/**
 * Application configuration loaded from environment variables
 * Environment variables are loaded from .env.local or .env files
 *
 * See env.d.ts for environment variable type definitions
 */

export const config = {
  // API endpoint for backend calls
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',

  // AWS Region
  awsRegion: import.meta.env.VITE_AWS_REGION || 'ap-northeast-1',

  // Application environment
  appEnv: import.meta.env.VITE_APP_ENV || 'development',

  // Derived values
  isDevelopment: (import.meta.env.VITE_APP_ENV || 'development') === 'development',
  isProduction: (import.meta.env.VITE_APP_ENV || 'development') === 'production',
} as const;

export type Config = typeof config;
