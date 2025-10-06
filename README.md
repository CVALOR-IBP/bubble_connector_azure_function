# Bubble Connector Azure Function

## Repository Status & Branch Information

**Current Repository**: `bubble_connector_azure_function`  
**Current Branch**: `main`  
**Latest Update**: October 6, 2023  
**Repository Type**: Azure Functions application for real-time Bubble to Snowflake synchronization

### Branch Information
- **Current Branch**: `main` - Production-ready Azure Functions application
- **Other Branches**: None (single branch repository)
- **Branch Differences**: This is the only branch containing the complete Azure Functions implementation

## Overview

This repository contains an **Azure Functions application** that provides real-time data synchronization between Bubble.io applications and Snowflake data warehouse. Unlike the standalone Python script in the original `bubble_connector` repository, this Azure Function implementation offers cloud-hosted HTTP endpoints for live data synchronization.

## Purpose

The **Bubble Connector Azure Function** serves as a **cloud-based microservice** that enables:

- **Real-time Synchronization**: Live data sync between Bubble and Snowflake
- **HTTP API Endpoints**: RESTful endpoints for Bubble plugin integration
- **Cloud Hosting**: Scalable Azure Functions deployment
- **Event-driven Processing**: Triggered by Bubble record changes
- **Schema Management**: Automatic table creation and schema updates

## Key Design Decisions & Technical Specifications

### Architecture Decisions
1. **Azure Functions over standalone scripts**: Chose serverless architecture for scalability and cloud hosting
2. **HTTP API approach**: Implemented RESTful endpoints for better integration with Bubble plugins
3. **Dynamic schema management**: Tables are created automatically based on data structure
4. **Environment-based schema separation**: DEV vs LIVE schemas for development and production data
5. **Temporary table strategy**: Uses temporary tables for full sync operations to ensure data consistency

### Technical Implementation Details
- **Record Change Detection**: Uses before/after record comparison to determine INSERT/UPDATE/DELETE operations
- **Column Name Sanitization**: Automatically converts special characters to underscores for Snowflake compatibility
- **Error Handling**: Comprehensive logging and graceful error responses
- **Connection Management**: Direct Snowflake connections per request (stateless design)
- **Data Type Handling**: All fields stored as VARCHAR for maximum flexibility

### Performance Considerations
- **Stateless Functions**: Each request is independent for better scalability
- **Batch Operations**: Full sync uses temporary tables for efficient bulk operations
- **Connection Pooling**: Relies on Azure Functions runtime for connection management
- **Logging**: Application Insights integration for monitoring and debugging

## Architecture & Data Flow

```
Bubble.io Application → HTTP API → Azure Functions → Snowflake Database
                            ↓
                    Bubble Plugin Code → Real-time Triggers
```

## Technology Stack

This repository uses the following technologies:

- **Azure Functions** - Cloud serverless compute platform for hosting HTTP endpoints
- **Python 3.11** - Runtime environment for the Azure Functions
- **snowflake-connector-python** - Snowflake database connectivity library
- **azure-functions** - Azure Functions SDK for Python
- **JavaScript** - Bubble plugin integration code for real-time triggers
- **JSON** - Data exchange format between Bubble and Azure Functions
- **HTTP/REST** - API communication protocol

**Application Type**: Azure Functions microservice for real-time data synchronization  
**Hosting Platform**: Microsoft Azure (Azure Functions)  
**Target Database**: Snowflake Data Warehouse

## External Dependencies

### Required External Services

1. **Azure Functions Host**
   - **Platform**: Microsoft Azure
   - **Runtime**: Python 3.11
   - **Authentication**: Azure Function keys
   - **Purpose**: Cloud hosting and execution

2. **Snowflake Data Warehouse**
   - **Connection**: Via environment variables
   - **Authentication**: Username/password or key-pair
   - **Purpose**: Target data warehouse for synchronized data

3. **Bubble.io Application**
   - **Integration**: Via HTTP API calls
   - **Authentication**: Azure Function keys
   - **Purpose**: Source application for data synchronization

### Environment Variables Required

```bash
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_DEV_SCHEMA=dev_schema
SNOWFLAKE_LIVE_SCHEMA=live_schema
SNOWFLAKE_WAREHOUSE=your_warehouse
```

## Directory Structure & Navigation

### Directory Overview

```
bubble_connector_azure_function/
├── 📄 function_app.py              # 🚀 MAIN AZURE FUNCTION - HTTP endpoints
├── 📄 requirements.txt             # 📦 Python dependencies
├── 📄 host.json                    # ⚙️ Azure Functions configuration
├── 📁 BubblePluginCode/            # 🔌 Bubble plugin integration
│   ├── FullSync.js                 # Full table synchronization plugin
│   └── RecordUpdate.js             # Individual record update plugin
└── 📄 README.md                    # 📖 This documentation
```

### File Last Updated Dates
- **function_app.py**: October 6, 2023
- **requirements.txt**: October 6, 2023  
- **host.json**: October 6, 2023
- **BubblePluginCode/FullSync.js**: October 6, 2023
- **BubblePluginCode/RecordUpdate.js**: October 6, 2023
- **README.md**: October 6, 2023

**Latest Update Across All Files**: October 6, 2023

### Core Application Files

| File | Purpose | Key Functions | Where to Look For |
|------|--------|---------------|-------------------|
| [`function_app.py`](function_app.py) | **🚀 Main Azure Function** | `RecordChange()`, `FullTableSync()` | HTTP endpoints, data processing logic |
| [`requirements.txt`](requirements.txt) | **📦 Dependencies** | Python package requirements | Azure Functions dependencies |
| [`host.json`](host.json) | **⚙️ Configuration** | Azure Functions runtime settings | Logging, extension bundles |

### Bubble Plugin Integration

| File | Purpose | Key Functions | Where to Look For |
|------|--------|---------------|-------------------|
| [`BubblePluginCode/FullSync.js`](BubblePluginCode/FullSync.js) | **🔄 Full Sync Plugin** | Triggers complete table synchronization | Bubble plugin integration |
| [`BubblePluginCode/RecordUpdate.js`](BubblePluginCode/RecordUpdate.js) | **📝 Record Update Plugin** | Handles individual record changes | Real-time sync triggers |

### Quick Navigation Guide

**🔍 Looking for something specific?**

- **HTTP Endpoints**: Check `function_app.py` for API endpoints
- **Bubble Integration**: Check `BubblePluginCode/` directory
- **Database Operations**: Check `function_app.py` for Snowflake functions
- **Configuration**: Check `host.json` and environment variables
- **Dependencies**: Check `requirements.txt`

## API Endpoints

### 1. Record Change Endpoint

**URL**: `/api/recordchange`  
**Method**: `POST`  
**Purpose**: Handles individual record changes (INSERT/UPDATE/DELETE)

**Request Body**:
```json
{
  "app_type": "your_app_type",
  "record_then": { "id": "record_id", ... },
  "record_now": { "id": "record_id", ... }
}
```

**Response**:
```json
{
  "success": true
}
```

### 2. Full Table Sync Endpoint

**URL**: `/api/fulltablesync`  
**Method**: `POST`  
**Purpose**: Performs complete table synchronization

**Request Body**:
```json
{
  "app_type": "your_app_type",
  "records": [{ "id": "1", "field": "value" }, ...]
}
```

**Response**:
```json
{
  "success": true
}
```

## Quick Start Guide

### Prerequisites

1. **Azure Account** with Functions access
2. **Snowflake account** with appropriate permissions
3. **Bubble.io application** with API access
4. **Azure Functions Core Tools** installed locally
5. **Python 3.11** installed on your development machine

### Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bubble_connector_azure_function
   ```

2. **Set up Python virtual environment**
   ```bash
   # Create virtual environment
   python3.11 -m venv .venv
   
   # Activate virtual environment
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate   # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Azure Functions Core Tools** (if not already installed)
   ```bash
   # On macOS with Homebrew
   brew tap azure/functions
   brew install azure-functions-core-tools@4
   
   # On Windows with Chocolatey
   choco install azure-functions-core-tools-4
   
   # On Linux
   curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
   sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg
   sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'
   sudo apt-get update
   sudo apt-get install azure-functions-core-tools-4
   ```

5. **Configure environment variables**
   ```bash
   # Set up local.settings.json for local development
   {
     "IsEncrypted": false,
     "Values": {
       "SNOWFLAKE_USER": "your_username",
       "SNOWFLAKE_PASSWORD": "your_password",
       "SNOWFLAKE_ACCOUNT": "your_account",
       "SNOWFLAKE_DATABASE": "your_database",
       "SNOWFLAKE_DEV_SCHEMA": "dev_schema",
       "SNOWFLAKE_LIVE_SCHEMA": "live_schema",
       "SNOWFLAKE_WAREHOUSE": "your_warehouse"
     }
   }
   ```

6. **Run locally**
   ```bash
   func start
   ```

7. **Deploy to Azure**
   ```bash
   func azure functionapp publish <your-function-app-name>
   ```

### New Machine Setup

To set up this repository on a new machine:

1. **Install Prerequisites**:
   - Python 3.11
   - Azure Functions Core Tools v4
   - Git

2. **Clone and Setup**:
   ```bash
   git clone <repository-url>
   cd bubble_connector_azure_function
   python3.11 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - Set up `local.settings.json` with your Snowflake credentials
   - Configure Azure CLI if deploying: `az login`

4. **Test Locally**:
   ```bash
   func start
   # Test endpoints at http://localhost:7071/api/recordchange and /api/fulltablesync
   ```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SNOWFLAKE_USER` | Snowflake username | Yes |
| `SNOWFLAKE_PASSWORD` | Snowflake password | Yes |
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier | Yes |
| `SNOWFLAKE_DATABASE` | Target database name | Yes |
| `SNOWFLAKE_DEV_SCHEMA` | Development schema | Yes |
| `SNOWFLAKE_LIVE_SCHEMA` | Production schema | No (defaults to dev) |
| `SNOWFLAKE_WAREHOUSE` | Snowflake warehouse | No (defaults to COMPUTE_WH) |

### Azure Functions Configuration

The `host.json` file configures:
- **Logging**: Application Insights integration
- **Extension Bundle**: Azure Functions extensions
- **Sampling**: Request sampling settings

## Deployment Options

### Azure Functions Deployment

1. **Azure Portal**: Deploy via Azure Portal interface
2. **Azure CLI**: Deploy using Azure CLI commands
3. **VS Code**: Deploy using Azure Functions extension
4. **GitHub Actions**: Automated deployment from repository

### Hosting Requirements

- **Azure Functions Consumption Plan** or **Premium Plan**
- **Python 3.11** runtime
- **Application Insights** for monitoring
- **Key Vault** for secure credential storage (recommended)

## Bubble Plugin Integration

### Setting up Bubble Plugins

1. **Copy plugin code** from `BubblePluginCode/` directory
2. **Create new plugins** in your Bubble application
3. **Configure API keys** in Bubble's plugin settings
4. **Set up triggers** for record changes and full syncs

### Plugin Configuration

- **Azure Key**: Function key for authentication
- **Full Table Sync URL**: Endpoint for full synchronization
- **Record Update Function URL**: Endpoint for individual updates

## Technical Specifications

### Data Processing Pipeline

1. **HTTP Request Processing**
   - Validates request format and authentication
   - Parses JSON request body
   - Determines schema (dev/live) based on app_type

2. **Database Operations**
   - Connects to Snowflake with environment variables
   - Creates tables dynamically based on data structure
   - Handles schema changes and table alterations

3. **Synchronization Logic**
   - **Record Changes**: Individual INSERT/UPDATE/DELETE operations
   - **Full Sync**: Complete table synchronization with conflict resolution
   - **Schema Management**: Automatic column addition and table creation

### Key Features

- **Real-time Processing**: HTTP-triggered functions for immediate sync
- **Schema Flexibility**: Dynamic table creation and column management
- **Error Handling**: Comprehensive logging and error responses
- **Scalability**: Cloud-native serverless architecture
- **Security**: Environment variable configuration

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Verify Snowflake credentials in environment variables
   - Check network connectivity from Azure Functions

2. **Authentication Errors**
   - Verify Azure Function keys in Bubble plugins
   - Check function key permissions

3. **Schema Issues**
   - Review table creation logs
   - Check column name formatting

### Monitoring

- **Azure Application Insights**: Built-in monitoring and logging
- **Function Logs**: Available in Azure Portal
- **Performance Metrics**: Function execution times and success rates

## Support & Maintenance

This Azure Function application is designed for **production use** with Bubble applications requiring real-time data synchronization. It provides a scalable, cloud-hosted solution for keeping Bubble and Snowflake data in sync.

For technical support or modifications, refer to the Azure Functions documentation and ensure all environment variables are properly configured in your Azure Function App settings.
