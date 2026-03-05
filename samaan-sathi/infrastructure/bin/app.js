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
const cognito = __importStar(require("aws-cdk-lib/aws-cognito"));
const dynamodb = __importStar(require("aws-cdk-lib/aws-dynamodb"));
const new_tables_stack_1 = require("../lib/new-tables-stack");
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
// Import existing Auth resources (already deployed - DO NOT REDEPLOY)
// These values are from the existing SamaanSathi-Auth-dev stack
const existingUserPoolId = 'ap-south-1_ZJrTmXTKR';
const existingUserPoolClientId = '5h6j21bsfoe4fampjfal2tebel';
// Storage layer (S3 Data Lake with medallion architecture)
const storageStack = new storage_stack_1.StorageStack(app, `SamaanSathi-Storage-${envName}`, {
    env,
    description: 'S3 buckets for data lake (raw/processed/features/predictions)',
});
// New DynamoDB tables (3 new AI tables)
const newTablesStack = new new_tables_stack_1.NewTablesStack(app, `SamaanSathi-NewTables-${envName}`, {
    env,
    description: 'New DynamoDB tables for AI features',
});
// ML infrastructure (SageMaker role for on-demand processing)
const mlStack = new ml_stack_1.MLStack(app, `SamaanSathi-ML-${envName}`, {
    env,
    description: 'SageMaker role for batch ML processing',
});
// Import UserPool and existing tables
const userPool = cognito.UserPool.fromUserPoolId(newTablesStack, 'ImportedUserPool', existingUserPoolId);
const existingInventoryTable = dynamodb.Table.fromTableName(newTablesStack, 'ExistingInventoryTable', 'samaan-sathi-inventory');
const existingUdhaarTable = dynamodb.Table.fromTableName(newTablesStack, 'ExistingUdhaarTable', 'samaan-sathi-udhaar');
// Compute layer (Lambda functions - no VPC, serverless)
const computeStack = new compute_stack_1.ComputeStack(app, `SamaanSathi-Compute-${envName}`, {
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
const apiStack = new api_stack_1.ApiStack(app, `SamaanSathi-API-${envName}`, {
    env,
    userPool: userPool,
    lambdaFunctions: computeStack.functions,
    description: 'API Gateway and REST endpoints',
});
// Monitoring and logging
const monitoringStack = new monitoring_stack_1.MonitoringStack(app, `SamaanSathi-Monitoring-${envName}`, {
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
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiYXBwLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsiYXBwLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7OztBQUNBLHVDQUFxQztBQUNyQyxpREFBbUM7QUFDbkMsaUVBQW1EO0FBQ25ELG1FQUFxRDtBQUNyRCw4REFBeUQ7QUFDekQsd0RBQW9EO0FBQ3BELHdEQUFvRDtBQUNwRCxnREFBNEM7QUFDNUMsOENBQTBDO0FBQzFDLDhEQUEwRDtBQUUxRCxNQUFNLEdBQUcsR0FBRyxJQUFJLEdBQUcsQ0FBQyxHQUFHLEVBQUUsQ0FBQztBQUUxQixNQUFNLEdBQUcsR0FBRztJQUNWLE9BQU8sRUFBRSxPQUFPLENBQUMsR0FBRyxDQUFDLG1CQUFtQjtJQUN4QyxNQUFNLEVBQUUsT0FBTyxDQUFDLEdBQUcsQ0FBQyxVQUFVLElBQUksWUFBWTtDQUMvQyxDQUFDO0FBRUYsTUFBTSxPQUFPLEdBQUcsT0FBTyxDQUFDLEdBQUcsQ0FBQyxXQUFXLElBQUksS0FBSyxDQUFDO0FBRWpELHNFQUFzRTtBQUN0RSxnRUFBZ0U7QUFDaEUsTUFBTSxrQkFBa0IsR0FBRyxzQkFBc0IsQ0FBQztBQUNsRCxNQUFNLHdCQUF3QixHQUFHLDRCQUE0QixDQUFDO0FBRTlELDJEQUEyRDtBQUMzRCxNQUFNLFlBQVksR0FBRyxJQUFJLDRCQUFZLENBQUMsR0FBRyxFQUFFLHVCQUF1QixPQUFPLEVBQUUsRUFBRTtJQUMzRSxHQUFHO0lBQ0gsV0FBVyxFQUFFLCtEQUErRDtDQUM3RSxDQUFDLENBQUM7QUFFSCx3Q0FBd0M7QUFDeEMsTUFBTSxjQUFjLEdBQUcsSUFBSSxpQ0FBYyxDQUFDLEdBQUcsRUFBRSx5QkFBeUIsT0FBTyxFQUFFLEVBQUU7SUFDakYsR0FBRztJQUNILFdBQVcsRUFBRSxxQ0FBcUM7Q0FDbkQsQ0FBQyxDQUFDO0FBRUgsOERBQThEO0FBQzlELE1BQU0sT0FBTyxHQUFHLElBQUksa0JBQU8sQ0FBQyxHQUFHLEVBQUUsa0JBQWtCLE9BQU8sRUFBRSxFQUFFO0lBQzVELEdBQUc7SUFDSCxXQUFXLEVBQUUsd0NBQXdDO0NBQ3RELENBQUMsQ0FBQztBQUVILHNDQUFzQztBQUN0QyxNQUFNLFFBQVEsR0FBRyxPQUFPLENBQUMsUUFBUSxDQUFDLGNBQWMsQ0FDOUMsY0FBYyxFQUNkLGtCQUFrQixFQUNsQixrQkFBa0IsQ0FDbkIsQ0FBQztBQUVGLE1BQU0sc0JBQXNCLEdBQUcsUUFBUSxDQUFDLEtBQUssQ0FBQyxhQUFhLENBQ3pELGNBQWMsRUFDZCx3QkFBd0IsRUFDeEIsd0JBQXdCLENBQ3pCLENBQUM7QUFFRixNQUFNLG1CQUFtQixHQUFHLFFBQVEsQ0FBQyxLQUFLLENBQUMsYUFBYSxDQUN0RCxjQUFjLEVBQ2QscUJBQXFCLEVBQ3JCLHFCQUFxQixDQUN0QixDQUFDO0FBRUYsd0RBQXdEO0FBQ3hELE1BQU0sWUFBWSxHQUFHLElBQUksNEJBQVksQ0FBQyxHQUFHLEVBQUUsdUJBQXVCLE9BQU8sRUFBRSxFQUFFO0lBQzNFLEdBQUc7SUFDSCxXQUFXLEVBQUUsc0JBQXNCO0lBQ25DLFdBQVcsRUFBRSxtQkFBbUI7SUFDaEMsYUFBYSxFQUFFLGNBQWMsQ0FBQyxhQUFhO0lBQzNDLG9CQUFvQixFQUFFLGNBQWMsQ0FBQyxvQkFBb0I7SUFDekQsY0FBYyxFQUFFLGNBQWMsQ0FBQyxjQUFjO0lBQzdDLFVBQVUsRUFBRSxZQUFZLENBQUMsVUFBVTtJQUNuQyxXQUFXLEVBQUUsWUFBWSxDQUFDLFdBQVc7SUFDckMsUUFBUSxFQUFFLFFBQVE7SUFDbEIsZ0JBQWdCLEVBQUUsd0JBQXdCO0lBQzFDLFdBQVcsRUFBRSwwQ0FBMEM7Q0FDeEQsQ0FBQyxDQUFDO0FBRUgsY0FBYztBQUNkLE1BQU0sUUFBUSxHQUFHLElBQUksb0JBQVEsQ0FBQyxHQUFHLEVBQUUsbUJBQW1CLE9BQU8sRUFBRSxFQUFFO0lBQy9ELEdBQUc7SUFDSCxRQUFRLEVBQUUsUUFBUTtJQUNsQixlQUFlLEVBQUUsWUFBWSxDQUFDLFNBQVM7SUFDdkMsV0FBVyxFQUFFLGdDQUFnQztDQUM5QyxDQUFDLENBQUM7QUFFSCx5QkFBeUI7QUFDekIsTUFBTSxlQUFlLEdBQUcsSUFBSSxrQ0FBZSxDQUFDLEdBQUcsRUFBRSwwQkFBMEIsT0FBTyxFQUFFLEVBQUU7SUFDcEYsR0FBRztJQUNILEdBQUcsRUFBRSxRQUFRLENBQUMsR0FBRztJQUNqQixlQUFlLEVBQUUsWUFBWSxDQUFDLFNBQVM7SUFDdkMsV0FBVyxFQUFFLGtDQUFrQztDQUNoRCxDQUFDLENBQUM7QUFFSCw0QkFBNEI7QUFDNUIsR0FBRyxDQUFDLElBQUksQ0FBQyxFQUFFLENBQUMsR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLFNBQVMsRUFBRSxhQUFhLENBQUMsQ0FBQztBQUMvQyxHQUFHLENBQUMsSUFBSSxDQUFDLEVBQUUsQ0FBQyxHQUFHLENBQUMsQ0FBQyxHQUFHLENBQUMsYUFBYSxFQUFFLE9BQU8sQ0FBQyxDQUFDO0FBQzdDLEdBQUcsQ0FBQyxJQUFJLENBQUMsRUFBRSxDQUFDLEdBQUcsQ0FBQyxDQUFDLEdBQUcsQ0FBQyxXQUFXLEVBQUUsS0FBSyxDQUFDLENBQUM7QUFDekMsR0FBRyxDQUFDLElBQUksQ0FBQyxFQUFFLENBQUMsR0FBRyxDQUFDLENBQUMsR0FBRyxDQUFDLFlBQVksRUFBRSxXQUFXLENBQUMsQ0FBQztBQUVoRCxHQUFHLENBQUMsS0FBSyxFQUFFLENBQUMiLCJzb3VyY2VzQ29udGVudCI6WyIjIS91c3IvYmluL2VudiBub2RlXHJcbmltcG9ydCAnc291cmNlLW1hcC1zdXBwb3J0L3JlZ2lzdGVyJztcclxuaW1wb3J0ICogYXMgY2RrIGZyb20gJ2F3cy1jZGstbGliJztcclxuaW1wb3J0ICogYXMgY29nbml0byBmcm9tICdhd3MtY2RrLWxpYi9hd3MtY29nbml0byc7XHJcbmltcG9ydCAqIGFzIGR5bmFtb2RiIGZyb20gJ2F3cy1jZGstbGliL2F3cy1keW5hbW9kYic7XHJcbmltcG9ydCB7IE5ld1RhYmxlc1N0YWNrIH0gZnJvbSAnLi4vbGliL25ldy10YWJsZXMtc3RhY2snO1xyXG5pbXBvcnQgeyBTdG9yYWdlU3RhY2sgfSBmcm9tICcuLi9saWIvc3RvcmFnZS1zdGFjayc7XHJcbmltcG9ydCB7IENvbXB1dGVTdGFjayB9IGZyb20gJy4uL2xpYi9jb21wdXRlLXN0YWNrJztcclxuaW1wb3J0IHsgQXBpU3RhY2sgfSBmcm9tICcuLi9saWIvYXBpLXN0YWNrJztcclxuaW1wb3J0IHsgTUxTdGFjayB9IGZyb20gJy4uL2xpYi9tbC1zdGFjayc7XHJcbmltcG9ydCB7IE1vbml0b3JpbmdTdGFjayB9IGZyb20gJy4uL2xpYi9tb25pdG9yaW5nLXN0YWNrJztcclxuXHJcbmNvbnN0IGFwcCA9IG5ldyBjZGsuQXBwKCk7XHJcblxyXG5jb25zdCBlbnYgPSB7XHJcbiAgYWNjb3VudDogcHJvY2Vzcy5lbnYuQ0RLX0RFRkFVTFRfQUNDT1VOVCxcclxuICByZWdpb246IHByb2Nlc3MuZW52LkFXU19SRUdJT04gfHwgJ2FwLXNvdXRoLTEnLFxyXG59O1xyXG5cclxuY29uc3QgZW52TmFtZSA9IHByb2Nlc3MuZW52LkVOVklST05NRU5UIHx8ICdkZXYnO1xyXG5cclxuLy8gSW1wb3J0IGV4aXN0aW5nIEF1dGggcmVzb3VyY2VzIChhbHJlYWR5IGRlcGxveWVkIC0gRE8gTk9UIFJFREVQTE9ZKVxyXG4vLyBUaGVzZSB2YWx1ZXMgYXJlIGZyb20gdGhlIGV4aXN0aW5nIFNhbWFhblNhdGhpLUF1dGgtZGV2IHN0YWNrXHJcbmNvbnN0IGV4aXN0aW5nVXNlclBvb2xJZCA9ICdhcC1zb3V0aC0xX1pKclRtWFRLUic7XHJcbmNvbnN0IGV4aXN0aW5nVXNlclBvb2xDbGllbnRJZCA9ICc1aDZqMjFic2ZvZTRmYW1wamZhbDJ0ZWJlbCc7XHJcblxyXG4vLyBTdG9yYWdlIGxheWVyIChTMyBEYXRhIExha2Ugd2l0aCBtZWRhbGxpb24gYXJjaGl0ZWN0dXJlKVxyXG5jb25zdCBzdG9yYWdlU3RhY2sgPSBuZXcgU3RvcmFnZVN0YWNrKGFwcCwgYFNhbWFhblNhdGhpLVN0b3JhZ2UtJHtlbnZOYW1lfWAsIHtcclxuICBlbnYsXHJcbiAgZGVzY3JpcHRpb246ICdTMyBidWNrZXRzIGZvciBkYXRhIGxha2UgKHJhdy9wcm9jZXNzZWQvZmVhdHVyZXMvcHJlZGljdGlvbnMpJyxcclxufSk7XHJcblxyXG4vLyBOZXcgRHluYW1vREIgdGFibGVzICgzIG5ldyBBSSB0YWJsZXMpXHJcbmNvbnN0IG5ld1RhYmxlc1N0YWNrID0gbmV3IE5ld1RhYmxlc1N0YWNrKGFwcCwgYFNhbWFhblNhdGhpLU5ld1RhYmxlcy0ke2Vudk5hbWV9YCwge1xyXG4gIGVudixcclxuICBkZXNjcmlwdGlvbjogJ05ldyBEeW5hbW9EQiB0YWJsZXMgZm9yIEFJIGZlYXR1cmVzJyxcclxufSk7XHJcblxyXG4vLyBNTCBpbmZyYXN0cnVjdHVyZSAoU2FnZU1ha2VyIHJvbGUgZm9yIG9uLWRlbWFuZCBwcm9jZXNzaW5nKVxyXG5jb25zdCBtbFN0YWNrID0gbmV3IE1MU3RhY2soYXBwLCBgU2FtYWFuU2F0aGktTUwtJHtlbnZOYW1lfWAsIHtcclxuICBlbnYsXHJcbiAgZGVzY3JpcHRpb246ICdTYWdlTWFrZXIgcm9sZSBmb3IgYmF0Y2ggTUwgcHJvY2Vzc2luZycsXHJcbn0pO1xyXG5cclxuLy8gSW1wb3J0IFVzZXJQb29sIGFuZCBleGlzdGluZyB0YWJsZXNcclxuY29uc3QgdXNlclBvb2wgPSBjb2duaXRvLlVzZXJQb29sLmZyb21Vc2VyUG9vbElkKFxyXG4gIG5ld1RhYmxlc1N0YWNrLFxyXG4gICdJbXBvcnRlZFVzZXJQb29sJyxcclxuICBleGlzdGluZ1VzZXJQb29sSWRcclxuKTtcclxuXHJcbmNvbnN0IGV4aXN0aW5nSW52ZW50b3J5VGFibGUgPSBkeW5hbW9kYi5UYWJsZS5mcm9tVGFibGVOYW1lKFxyXG4gIG5ld1RhYmxlc1N0YWNrLFxyXG4gICdFeGlzdGluZ0ludmVudG9yeVRhYmxlJyxcclxuICAnc2FtYWFuLXNhdGhpLWludmVudG9yeSdcclxuKTtcclxuXHJcbmNvbnN0IGV4aXN0aW5nVWRoYWFyVGFibGUgPSBkeW5hbW9kYi5UYWJsZS5mcm9tVGFibGVOYW1lKFxyXG4gIG5ld1RhYmxlc1N0YWNrLFxyXG4gICdFeGlzdGluZ1VkaGFhclRhYmxlJyxcclxuICAnc2FtYWFuLXNhdGhpLXVkaGFhcidcclxuKTtcclxuXHJcbi8vIENvbXB1dGUgbGF5ZXIgKExhbWJkYSBmdW5jdGlvbnMgLSBubyBWUEMsIHNlcnZlcmxlc3MpXHJcbmNvbnN0IGNvbXB1dGVTdGFjayA9IG5ldyBDb21wdXRlU3RhY2soYXBwLCBgU2FtYWFuU2F0aGktQ29tcHV0ZS0ke2Vudk5hbWV9YCwge1xyXG4gIGVudixcclxuICBkeW5hbW9UYWJsZTogZXhpc3RpbmdJbnZlbnRvcnlUYWJsZSxcclxuICB1ZGhhYXJUYWJsZTogZXhpc3RpbmdVZGhhYXJUYWJsZSxcclxuICBmb3JlY2FzdFRhYmxlOiBuZXdUYWJsZXNTdGFjay5mb3JlY2FzdFRhYmxlLFxyXG4gIGN1c3RvbWVyUHJvZmlsZVRhYmxlOiBuZXdUYWJsZXNTdGFjay5jdXN0b21lclByb2ZpbGVUYWJsZSxcclxuICBkZWNpc2lvbnNUYWJsZTogbmV3VGFibGVzU3RhY2suZGVjaXNpb25zVGFibGUsXHJcbiAgZGF0YUJ1Y2tldDogc3RvcmFnZVN0YWNrLmRhdGFCdWNrZXQsXHJcbiAgYmlsbHNCdWNrZXQ6IHN0b3JhZ2VTdGFjay5iaWxsc0J1Y2tldCxcclxuICB1c2VyUG9vbDogdXNlclBvb2wsXHJcbiAgdXNlclBvb2xDbGllbnRJZDogZXhpc3RpbmdVc2VyUG9vbENsaWVudElkLFxyXG4gIGRlc2NyaXB0aW9uOiAnTGFtYmRhIGZ1bmN0aW9ucyB3aXRoIEFJIERlY2lzaW9uIEVuZ2luZScsXHJcbn0pO1xyXG5cclxuLy8gQVBJIEdhdGV3YXlcclxuY29uc3QgYXBpU3RhY2sgPSBuZXcgQXBpU3RhY2soYXBwLCBgU2FtYWFuU2F0aGktQVBJLSR7ZW52TmFtZX1gLCB7XHJcbiAgZW52LFxyXG4gIHVzZXJQb29sOiB1c2VyUG9vbCxcclxuICBsYW1iZGFGdW5jdGlvbnM6IGNvbXB1dGVTdGFjay5mdW5jdGlvbnMsXHJcbiAgZGVzY3JpcHRpb246ICdBUEkgR2F0ZXdheSBhbmQgUkVTVCBlbmRwb2ludHMnLFxyXG59KTtcclxuXHJcbi8vIE1vbml0b3JpbmcgYW5kIGxvZ2dpbmdcclxuY29uc3QgbW9uaXRvcmluZ1N0YWNrID0gbmV3IE1vbml0b3JpbmdTdGFjayhhcHAsIGBTYW1hYW5TYXRoaS1Nb25pdG9yaW5nLSR7ZW52TmFtZX1gLCB7XHJcbiAgZW52LFxyXG4gIGFwaTogYXBpU3RhY2suYXBpLFxyXG4gIGxhbWJkYUZ1bmN0aW9uczogY29tcHV0ZVN0YWNrLmZ1bmN0aW9ucyxcclxuICBkZXNjcmlwdGlvbjogJ0Nsb3VkV2F0Y2ggZGFzaGJvYXJkcyBhbmQgYWxhcm1zJyxcclxufSk7XHJcblxyXG4vLyBBZGQgdGFncyB0byBhbGwgcmVzb3VyY2VzXHJcbmNkay5UYWdzLm9mKGFwcCkuYWRkKCdQcm9qZWN0JywgJ1NhbWFhblNhdGhpJyk7XHJcbmNkay5UYWdzLm9mKGFwcCkuYWRkKCdFbnZpcm9ubWVudCcsIGVudk5hbWUpO1xyXG5jZGsuVGFncy5vZihhcHApLmFkZCgnTWFuYWdlZEJ5JywgJ0NESycpO1xyXG5jZGsuVGFncy5vZihhcHApLmFkZCgnQ29zdENlbnRlcicsICdBSS1SZXRhaWwnKTtcclxuXHJcbmFwcC5zeW50aCgpO1xyXG4iXX0=