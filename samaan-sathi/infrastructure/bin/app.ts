#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import { NewTablesStack } from '../lib/new-tables-stack';
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

// Import existing Auth resources (already deployed - DO NOT REDEPLOY)
// These values are from the existing SamaanSathi-Auth-dev stack
const existingUserPoolId = 'ap-south-1_ZJrTmXTKR';
const existingUserPoolClientId = '5h6j21bsfoe4fampjfal2tebel';

// Storage layer (S3 Data Lake with medallion architecture)
const storageStack = new StorageStack(app, `SamaanSathi-Storage-${envName}`, {
  env,
  description: 'S3 buckets for data lake (raw/processed/features/predictions)',
});

// New DynamoDB tables (3 new AI tables)
const newTablesStack = new NewTablesStack(app, `SamaanSathi-NewTables-${envName}`, {
  env,
  description: 'New DynamoDB tables for AI features',
});

// ML infrastructure (SageMaker role for on-demand processing)
const mlStack = new MLStack(app, `SamaanSathi-ML-${envName}`, {
  env,
  description: 'SageMaker role for batch ML processing',
});

// Import UserPool and existing tables
const userPool = cognito.UserPool.fromUserPoolId(
  newTablesStack,
  'ImportedUserPool',
  existingUserPoolId
);

const existingInventoryTable = dynamodb.Table.fromTableName(
  newTablesStack,
  'ExistingInventoryTable',
  'samaan-sathi-inventory'
);

const existingUdhaarTable = dynamodb.Table.fromTableName(
  newTablesStack,
  'ExistingUdhaarTable',
  'samaan-sathi-udhaar'
);

// Compute layer (Lambda functions - no VPC, serverless)
const computeStack = new ComputeStack(app, `SamaanSathi-Compute-${envName}`, {
  env,
  dynamoTable: existingInventoryTable,
  udhaarTable: existingUdhaarTable,
  forecastTable: newTablesStack.forecastTable,
  customerProfileTable: newTablesStack.customerProfileTable,
  decisionsTable: newTablesStack.decisionsTable,
  dataBucket: storageStack.dataBucket,
  billsBucket: storageStack.billsBucket,
  userPool: userPool,
  userPoolClientId: existingUserPoolClientId,
  description: 'Lambda functions with AI Decision Engine',
});

// API Gateway
const apiStack = new ApiStack(app, `SamaanSathi-API-${envName}`, {
  env,
  userPool: userPool,
  lambdaFunctions: computeStack.functions,
  description: 'API Gateway and REST endpoints',
});

// Monitoring and logging
const monitoringStack = new MonitoringStack(app, `SamaanSathi-Monitoring-${envName}`, {
  env,
  api: apiStack.api,
  lambdaFunctions: computeStack.functions,
  description: 'CloudWatch dashboards and alarms',
});

// Add tags to all resources
cdk.Tags.of(app).add('Project', 'SamaanSathi');
cdk.Tags.of(app).add('Environment', envName);
cdk.Tags.of(app).add('ManagedBy', 'CDK');
cdk.Tags.of(app).add('CostCenter', 'AI-Retail');

app.synth();
