#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { NetworkStack } from '../lib/network-stack';
import { DatabaseStack } from '../lib/database-stack';
import { AuthStack } from '../lib/auth-stack';
import { StorageStack } from '../lib/storage-stack';
import { ComputeStack } from '../lib/compute-stack';
import { ApiStack } from '../lib/api-stack';
import { MLStack } from '../lib/ml-stack';
import { MonitoringStack } from '../lib/monitoring-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.AWS_REGION || 'ap-south-1',
};

const envName = process.env.ENVIRONMENT || 'dev';

// Network infrastructure
const networkStack = new NetworkStack(app, `SamaanSathi-Network-${envName}`, {
  env,
  description: 'VPC and networking resources for Samaan Sathi AI',
});

// Authentication
const authStack = new AuthStack(app, `SamaanSathi-Auth-${envName}`, {
  env,
  description: 'Cognito user pools and authentication',
});

// Storage layer
const storageStack = new StorageStack(app, `SamaanSathi-Storage-${envName}`, {
  env,
  description: 'S3 buckets for data storage',
});

// Database layer
const databaseStack = new DatabaseStack(app, `SamaanSathi-Database-${envName}`, {
  env,
  vpc: networkStack.vpc,
  description: 'RDS PostgreSQL and DynamoDB tables',
});

// ML infrastructure
const mlStack = new MLStack(app, `SamaanSathi-ML-${envName}`, {
  env,
  vpc: networkStack.vpc,
  dataBucket: storageStack.dataBucket,
  description: 'SageMaker and ML model infrastructure',
});

// Compute layer (Lambda functions)
const computeStack = new ComputeStack(app, `SamaanSathi-Compute-${envName}`, {
  env,
  vpc: networkStack.vpc,
  database: databaseStack.database,
  dynamoTable: databaseStack.dynamoTable,
  udhaarTable: databaseStack.udhaarTable,
  dataBucket: storageStack.dataBucket,
  userPool: authStack.userPool,
  userPoolClientId: authStack.userPoolClientId,
  description: 'Lambda functions for business logic',
});

// API Gateway
const apiStack = new ApiStack(app, `SamaanSathi-API-${envName}`, {
  env,
  userPool: authStack.userPool,
  lambdaFunctions: computeStack.functions,
  description: 'API Gateway and REST endpoints',
});

// Monitoring and logging
const monitoringStack = new MonitoringStack(app, `SamaanSathi-Monitoring-${envName}`, {
  env,
  api: apiStack.api,
  lambdaFunctions: computeStack.functions,
  database: databaseStack.database,
  description: 'CloudWatch dashboards and alarms',
});

// Add tags to all resources
cdk.Tags.of(app).add('Project', 'SamaanSathi');
cdk.Tags.of(app).add('Environment', envName);
cdk.Tags.of(app).add('ManagedBy', 'CDK');

app.synth();
