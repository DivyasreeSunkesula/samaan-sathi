#!/usr/bin/env node
"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
require("source-map-support/register");
const cdk = __importStar(require("aws-cdk-lib"));
const network_stack_1 = require("../lib/network-stack");
const database_stack_1 = require("../lib/database-stack");
const auth_stack_1 = require("../lib/auth-stack");
const storage_stack_1 = require("../lib/storage-stack");
const compute_stack_1 = require("../lib/compute-stack");
const api_stack_1 = require("../lib/api-stack");
const ml_stack_1 = require("../lib/ml-stack");
const monitoring_stack_1 = require("../lib/monitoring-stack");
const app = new cdk.App();
const env = {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.AWS_REGION || 'ap-south-1',
};
const envName = process.env.ENVIRONMENT || 'dev';
// Network infrastructure
const networkStack = new network_stack_1.NetworkStack(app, `SamaanSathi-Network-${envName}`, {
    env,
    description: 'VPC and networking resources for Samaan Sathi AI',
});
// Authentication
const authStack = new auth_stack_1.AuthStack(app, `SamaanSathi-Auth-${envName}`, {
    env,
    description: 'Cognito user pools and authentication',
});
// Storage layer
const storageStack = new storage_stack_1.StorageStack(app, `SamaanSathi-Storage-${envName}`, {
    env,
    description: 'S3 buckets for data storage',
});
// Database layer
const databaseStack = new database_stack_1.DatabaseStack(app, `SamaanSathi-Database-${envName}`, {
    env,
    vpc: networkStack.vpc,
    description: 'RDS PostgreSQL and DynamoDB tables',
});
// ML infrastructure
const mlStack = new ml_stack_1.MLStack(app, `SamaanSathi-ML-${envName}`, {
    env,
    vpc: networkStack.vpc,
    dataBucket: storageStack.dataBucket,
    description: 'SageMaker and ML model infrastructure',
});
// Compute layer (Lambda functions)
const computeStack = new compute_stack_1.ComputeStack(app, `SamaanSathi-Compute-${envName}`, {
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
const apiStack = new api_stack_1.ApiStack(app, `SamaanSathi-API-${envName}`, {
    env,
    userPool: authStack.userPool,
    lambdaFunctions: computeStack.functions,
    description: 'API Gateway and REST endpoints',
});
// Monitoring and logging
const monitoringStack = new monitoring_stack_1.MonitoringStack(app, `SamaanSathi-Monitoring-${envName}`, {
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiYXBwLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsiYXBwLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7OztBQUNBLHVDQUFxQztBQUNyQyxpREFBbUM7QUFDbkMsd0RBQW9EO0FBQ3BELDBEQUFzRDtBQUN0RCxrREFBOEM7QUFDOUMsd0RBQW9EO0FBQ3BELHdEQUFvRDtBQUNwRCxnREFBNEM7QUFDNUMsOENBQTBDO0FBQzFDLDhEQUEwRDtBQUUxRCxNQUFNLEdBQUcsR0FBRyxJQUFJLEdBQUcsQ0FBQyxHQUFHLEVBQUUsQ0FBQztBQUUxQixNQUFNLEdBQUcsR0FBRztJQUNWLE9BQU8sRUFBRSxPQUFPLENBQUMsR0FBRyxDQUFDLG1CQUFtQjtJQUN4QyxNQUFNLEVBQUUsT0FBTyxDQUFDLEdBQUcsQ0FBQyxVQUFVLElBQUksWUFBWTtDQUMvQyxDQUFDO0FBRUYsTUFBTSxPQUFPLEdBQUcsT0FBTyxDQUFDLEdBQUcsQ0FBQyxXQUFXLElBQUksS0FBSyxDQUFDO0FBRWpELHlCQUF5QjtBQUN6QixNQUFNLFlBQVksR0FBRyxJQUFJLDRCQUFZLENBQUMsR0FBRyxFQUFFLHVCQUF1QixPQUFPLEVBQUUsRUFBRTtJQUMzRSxHQUFHO0lBQ0gsV0FBVyxFQUFFLGtEQUFrRDtDQUNoRSxDQUFDLENBQUM7QUFFSCxpQkFBaUI7QUFDakIsTUFBTSxTQUFTLEdBQUcsSUFBSSxzQkFBUyxDQUFDLEdBQUcsRUFBRSxvQkFBb0IsT0FBTyxFQUFFLEVBQUU7SUFDbEUsR0FBRztJQUNILFdBQVcsRUFBRSx1Q0FBdUM7Q0FDckQsQ0FBQyxDQUFDO0FBRUgsZ0JBQWdCO0FBQ2hCLE1BQU0sWUFBWSxHQUFHLElBQUksNEJBQVksQ0FBQyxHQUFHLEVBQUUsdUJBQXVCLE9BQU8sRUFBRSxFQUFFO0lBQzNFLEdBQUc7SUFDSCxXQUFXLEVBQUUsNkJBQTZCO0NBQzNDLENBQUMsQ0FBQztBQUVILGlCQUFpQjtBQUNqQixNQUFNLGFBQWEsR0FBRyxJQUFJLDhCQUFhLENBQUMsR0FBRyxFQUFFLHdCQUF3QixPQUFPLEVBQUUsRUFBRTtJQUM5RSxHQUFHO0lBQ0gsR0FBRyxFQUFFLFlBQVksQ0FBQyxHQUFHO0lBQ3JCLFdBQVcsRUFBRSxvQ0FBb0M7Q0FDbEQsQ0FBQyxDQUFDO0FBRUgsb0JBQW9CO0FBQ3BCLE1BQU0sT0FBTyxHQUFHLElBQUksa0JBQU8sQ0FBQyxHQUFHLEVBQUUsa0JBQWtCLE9BQU8sRUFBRSxFQUFFO0lBQzVELEdBQUc7SUFDSCxHQUFHLEVBQUUsWUFBWSxDQUFDLEdBQUc7SUFDckIsVUFBVSxFQUFFLFlBQVksQ0FBQyxVQUFVO0lBQ25DLFdBQVcsRUFBRSx1Q0FBdUM7Q0FDckQsQ0FBQyxDQUFDO0FBRUgsbUNBQW1DO0FBQ25DLE1BQU0sWUFBWSxHQUFHLElBQUksNEJBQVksQ0FBQyxHQUFHLEVBQUUsdUJBQXVCLE9BQU8sRUFBRSxFQUFFO0lBQzNFLEdBQUc7SUFDSCxHQUFHLEVBQUUsWUFBWSxDQUFDLEdBQUc7SUFDckIsUUFBUSxFQUFFLGFBQWEsQ0FBQyxRQUFRO0lBQ2hDLFdBQVcsRUFBRSxhQUFhLENBQUMsV0FBVztJQUN0QyxXQUFXLEVBQUUsYUFBYSxDQUFDLFdBQVc7SUFDdEMsVUFBVSxFQUFFLFlBQVksQ0FBQyxVQUFVO0lBQ25DLFFBQVEsRUFBRSxTQUFTLENBQUMsUUFBUTtJQUM1QixnQkFBZ0IsRUFBRSxTQUFTLENBQUMsZ0JBQWdCO0lBQzVDLFdBQVcsRUFBRSxxQ0FBcUM7Q0FDbkQsQ0FBQyxDQUFDO0FBRUgsY0FBYztBQUNkLE1BQU0sUUFBUSxHQUFHLElBQUksb0JBQVEsQ0FBQyxHQUFHLEVBQUUsbUJBQW1CLE9BQU8sRUFBRSxFQUFFO0lBQy9ELEdBQUc7SUFDSCxRQUFRLEVBQUUsU0FBUyxDQUFDLFFBQVE7SUFDNUIsZUFBZSxFQUFFLFlBQVksQ0FBQyxTQUFTO0lBQ3ZDLFdBQVcsRUFBRSxnQ0FBZ0M7Q0FDOUMsQ0FBQyxDQUFDO0FBRUgseUJBQXlCO0FBQ3pCLE1BQU0sZUFBZSxHQUFHLElBQUksa0NBQWUsQ0FBQyxHQUFHLEVBQUUsMEJBQTBCLE9BQU8sRUFBRSxFQUFFO0lBQ3BGLEdBQUc7SUFDSCxHQUFHLEVBQUUsUUFBUSxDQUFDLEdBQUc7SUFDakIsZUFBZSxFQUFFLFlBQVksQ0FBQyxTQUFTO0lBQ3ZDLFFBQVEsRUFBRSxhQUFhLENBQUMsUUFBUTtJQUNoQyxXQUFXLEVBQUUsa0NBQWtDO0NBQ2hELENBQUMsQ0FBQztBQUVILDRCQUE0QjtBQUM1QixHQUFHLENBQUMsSUFBSSxDQUFDLEVBQUUsQ0FBQyxHQUFHLENBQUMsQ0FBQyxHQUFHLENBQUMsU0FBUyxFQUFFLGFBQWEsQ0FBQyxDQUFDO0FBQy9DLEdBQUcsQ0FBQyxJQUFJLENBQUMsRUFBRSxDQUFDLEdBQUcsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxhQUFhLEVBQUUsT0FBTyxDQUFDLENBQUM7QUFDN0MsR0FBRyxDQUFDLElBQUksQ0FBQyxFQUFFLENBQUMsR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLFdBQVcsRUFBRSxLQUFLLENBQUMsQ0FBQztBQUV6QyxHQUFHLENBQUMsS0FBSyxFQUFFLENBQUMiLCJzb3VyY2VzQ29udGVudCI6WyIjIS91c3IvYmluL2VudiBub2RlXHJcbmltcG9ydCAnc291cmNlLW1hcC1zdXBwb3J0L3JlZ2lzdGVyJztcclxuaW1wb3J0ICogYXMgY2RrIGZyb20gJ2F3cy1jZGstbGliJztcclxuaW1wb3J0IHsgTmV0d29ya1N0YWNrIH0gZnJvbSAnLi4vbGliL25ldHdvcmstc3RhY2snO1xyXG5pbXBvcnQgeyBEYXRhYmFzZVN0YWNrIH0gZnJvbSAnLi4vbGliL2RhdGFiYXNlLXN0YWNrJztcclxuaW1wb3J0IHsgQXV0aFN0YWNrIH0gZnJvbSAnLi4vbGliL2F1dGgtc3RhY2snO1xyXG5pbXBvcnQgeyBTdG9yYWdlU3RhY2sgfSBmcm9tICcuLi9saWIvc3RvcmFnZS1zdGFjayc7XHJcbmltcG9ydCB7IENvbXB1dGVTdGFjayB9IGZyb20gJy4uL2xpYi9jb21wdXRlLXN0YWNrJztcclxuaW1wb3J0IHsgQXBpU3RhY2sgfSBmcm9tICcuLi9saWIvYXBpLXN0YWNrJztcclxuaW1wb3J0IHsgTUxTdGFjayB9IGZyb20gJy4uL2xpYi9tbC1zdGFjayc7XHJcbmltcG9ydCB7IE1vbml0b3JpbmdTdGFjayB9IGZyb20gJy4uL2xpYi9tb25pdG9yaW5nLXN0YWNrJztcclxuXHJcbmNvbnN0IGFwcCA9IG5ldyBjZGsuQXBwKCk7XHJcblxyXG5jb25zdCBlbnYgPSB7XHJcbiAgYWNjb3VudDogcHJvY2Vzcy5lbnYuQ0RLX0RFRkFVTFRfQUNDT1VOVCxcclxuICByZWdpb246IHByb2Nlc3MuZW52LkFXU19SRUdJT04gfHwgJ2FwLXNvdXRoLTEnLFxyXG59O1xyXG5cclxuY29uc3QgZW52TmFtZSA9IHByb2Nlc3MuZW52LkVOVklST05NRU5UIHx8ICdkZXYnO1xyXG5cclxuLy8gTmV0d29yayBpbmZyYXN0cnVjdHVyZVxyXG5jb25zdCBuZXR3b3JrU3RhY2sgPSBuZXcgTmV0d29ya1N0YWNrKGFwcCwgYFNhbWFhblNhdGhpLU5ldHdvcmstJHtlbnZOYW1lfWAsIHtcclxuICBlbnYsXHJcbiAgZGVzY3JpcHRpb246ICdWUEMgYW5kIG5ldHdvcmtpbmcgcmVzb3VyY2VzIGZvciBTYW1hYW4gU2F0aGkgQUknLFxyXG59KTtcclxuXHJcbi8vIEF1dGhlbnRpY2F0aW9uXHJcbmNvbnN0IGF1dGhTdGFjayA9IG5ldyBBdXRoU3RhY2soYXBwLCBgU2FtYWFuU2F0aGktQXV0aC0ke2Vudk5hbWV9YCwge1xyXG4gIGVudixcclxuICBkZXNjcmlwdGlvbjogJ0NvZ25pdG8gdXNlciBwb29scyBhbmQgYXV0aGVudGljYXRpb24nLFxyXG59KTtcclxuXHJcbi8vIFN0b3JhZ2UgbGF5ZXJcclxuY29uc3Qgc3RvcmFnZVN0YWNrID0gbmV3IFN0b3JhZ2VTdGFjayhhcHAsIGBTYW1hYW5TYXRoaS1TdG9yYWdlLSR7ZW52TmFtZX1gLCB7XHJcbiAgZW52LFxyXG4gIGRlc2NyaXB0aW9uOiAnUzMgYnVja2V0cyBmb3IgZGF0YSBzdG9yYWdlJyxcclxufSk7XHJcblxyXG4vLyBEYXRhYmFzZSBsYXllclxyXG5jb25zdCBkYXRhYmFzZVN0YWNrID0gbmV3IERhdGFiYXNlU3RhY2soYXBwLCBgU2FtYWFuU2F0aGktRGF0YWJhc2UtJHtlbnZOYW1lfWAsIHtcclxuICBlbnYsXHJcbiAgdnBjOiBuZXR3b3JrU3RhY2sudnBjLFxyXG4gIGRlc2NyaXB0aW9uOiAnUkRTIFBvc3RncmVTUUwgYW5kIER5bmFtb0RCIHRhYmxlcycsXHJcbn0pO1xyXG5cclxuLy8gTUwgaW5mcmFzdHJ1Y3R1cmVcclxuY29uc3QgbWxTdGFjayA9IG5ldyBNTFN0YWNrKGFwcCwgYFNhbWFhblNhdGhpLU1MLSR7ZW52TmFtZX1gLCB7XHJcbiAgZW52LFxyXG4gIHZwYzogbmV0d29ya1N0YWNrLnZwYyxcclxuICBkYXRhQnVja2V0OiBzdG9yYWdlU3RhY2suZGF0YUJ1Y2tldCxcclxuICBkZXNjcmlwdGlvbjogJ1NhZ2VNYWtlciBhbmQgTUwgbW9kZWwgaW5mcmFzdHJ1Y3R1cmUnLFxyXG59KTtcclxuXHJcbi8vIENvbXB1dGUgbGF5ZXIgKExhbWJkYSBmdW5jdGlvbnMpXHJcbmNvbnN0IGNvbXB1dGVTdGFjayA9IG5ldyBDb21wdXRlU3RhY2soYXBwLCBgU2FtYWFuU2F0aGktQ29tcHV0ZS0ke2Vudk5hbWV9YCwge1xyXG4gIGVudixcclxuICB2cGM6IG5ldHdvcmtTdGFjay52cGMsXHJcbiAgZGF0YWJhc2U6IGRhdGFiYXNlU3RhY2suZGF0YWJhc2UsXHJcbiAgZHluYW1vVGFibGU6IGRhdGFiYXNlU3RhY2suZHluYW1vVGFibGUsXHJcbiAgdWRoYWFyVGFibGU6IGRhdGFiYXNlU3RhY2sudWRoYWFyVGFibGUsXHJcbiAgZGF0YUJ1Y2tldDogc3RvcmFnZVN0YWNrLmRhdGFCdWNrZXQsXHJcbiAgdXNlclBvb2w6IGF1dGhTdGFjay51c2VyUG9vbCxcclxuICB1c2VyUG9vbENsaWVudElkOiBhdXRoU3RhY2sudXNlclBvb2xDbGllbnRJZCxcclxuICBkZXNjcmlwdGlvbjogJ0xhbWJkYSBmdW5jdGlvbnMgZm9yIGJ1c2luZXNzIGxvZ2ljJyxcclxufSk7XHJcblxyXG4vLyBBUEkgR2F0ZXdheVxyXG5jb25zdCBhcGlTdGFjayA9IG5ldyBBcGlTdGFjayhhcHAsIGBTYW1hYW5TYXRoaS1BUEktJHtlbnZOYW1lfWAsIHtcclxuICBlbnYsXHJcbiAgdXNlclBvb2w6IGF1dGhTdGFjay51c2VyUG9vbCxcclxuICBsYW1iZGFGdW5jdGlvbnM6IGNvbXB1dGVTdGFjay5mdW5jdGlvbnMsXHJcbiAgZGVzY3JpcHRpb246ICdBUEkgR2F0ZXdheSBhbmQgUkVTVCBlbmRwb2ludHMnLFxyXG59KTtcclxuXHJcbi8vIE1vbml0b3JpbmcgYW5kIGxvZ2dpbmdcclxuY29uc3QgbW9uaXRvcmluZ1N0YWNrID0gbmV3IE1vbml0b3JpbmdTdGFjayhhcHAsIGBTYW1hYW5TYXRoaS1Nb25pdG9yaW5nLSR7ZW52TmFtZX1gLCB7XHJcbiAgZW52LFxyXG4gIGFwaTogYXBpU3RhY2suYXBpLFxyXG4gIGxhbWJkYUZ1bmN0aW9uczogY29tcHV0ZVN0YWNrLmZ1bmN0aW9ucyxcclxuICBkYXRhYmFzZTogZGF0YWJhc2VTdGFjay5kYXRhYmFzZSxcclxuICBkZXNjcmlwdGlvbjogJ0Nsb3VkV2F0Y2ggZGFzaGJvYXJkcyBhbmQgYWxhcm1zJyxcclxufSk7XHJcblxyXG4vLyBBZGQgdGFncyB0byBhbGwgcmVzb3VyY2VzXHJcbmNkay5UYWdzLm9mKGFwcCkuYWRkKCdQcm9qZWN0JywgJ1NhbWFhblNhdGhpJyk7XHJcbmNkay5UYWdzLm9mKGFwcCkuYWRkKCdFbnZpcm9ubWVudCcsIGVudk5hbWUpO1xyXG5jZGsuVGFncy5vZihhcHApLmFkZCgnTWFuYWdlZEJ5JywgJ0NESycpO1xyXG5cclxuYXBwLnN5bnRoKCk7XHJcbiJdfQ==