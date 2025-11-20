/**
 * Infrastructure configuration loaded from environment variables.
 * Used by CDK to configure AWS resources.
 */

import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables from .env.local or .env files
const envPath = path.resolve(__dirname, '../.env.local');
dotenv.config({ path: envPath });

export interface InfrastructureConfig {
  // AWS Configuration
  awsAccountId: string;
  awsRegion: string;
  awsAccessKeyId?: string;
  awsSecretAccessKey?: string;

  // Application Configuration
  appEnv: string;
  appName: string;

  // Infrastructure Configuration
  environment: string;
  enableCors: boolean;
  logLevel: string;

  // Build Configuration
  buildDockerImage: boolean;
  dockerRegistryUrl?: string;
}

export function loadConfig(): InfrastructureConfig {
  const config: InfrastructureConfig = {
    // AWS Configuration
    awsAccountId: process.env.AWS_ACCOUNT_ID || '123456789012',
    awsRegion: process.env.AWS_REGION || 'ap-northeast-1',
    awsAccessKeyId: process.env.AWS_ACCESS_KEY_ID,
    awsSecretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,

    // Application Configuration
    appEnv: process.env.APP_ENV || 'development',
    appName: process.env.APP_NAME || 'megrepper',

    // Infrastructure Configuration
    environment: process.env.ENVIRONMENT || 'dev',
    enableCors: process.env.ENABLE_CORS === 'true',
    logLevel: process.env.LOG_LEVEL || 'info',

    // Build Configuration
    buildDockerImage: process.env.BUILD_DOCKER_IMAGE === 'true',
    dockerRegistryUrl: process.env.DOCKER_REGISTRY_URL,
  };

  // Validate required fields
  if (!config.awsAccountId || config.awsAccountId === '123456789012') {
    console.warn('⚠️  AWS_ACCOUNT_ID is not set. Please configure it in .env.local');
  }

  return config;
}

export const config = loadConfig();
