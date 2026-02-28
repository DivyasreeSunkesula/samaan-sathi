# Lambda Dependencies Layer

This directory will contain Python dependencies for Lambda functions.

## Installation

The dependencies will be installed automatically during deployment, or you can install them manually:

```bash
pip install -r ../../requirements.txt -t python/
```

## Structure

```
dependencies/
└── python/
    ├── boto3/
    ├── psycopg2/
    └── ... (other packages)
```
