#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { MegrepperStack } from '../lib/megrepper-stack';

const app = new cdk.App();

new MegrepperStack(app, 'MegrepperStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'ap-northeast-1',
  },
  description: 'Megrepper - JSON/YAML Guessing Game',
});
