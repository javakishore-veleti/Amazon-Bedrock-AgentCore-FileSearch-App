# Amazon Bedrock Agent Core File Search App

A Python application leveraging Amazon Bedrock's Agent Core capabilities for intelligent file search and retrieval.

## Features

- 🤖 Amazon Bedrock Agent Core integration
- 📁 Intelligent file search and retrieval
- 🔍 Multi-format file support
- 🚀 FastAPI backend
- � AWS IAM authentication

## Prerequisites

- Python 3.9+
- AWS Account with Bedrock access

## Installation

### Setup

```bash
bash DevOps/setup.sh
```

This will:
1. Create a Python virtual environment
2. Install all dependencies
3. Set up your `.env` file from `.env.example`

### Manual Installation

If you prefer manual setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env with your AWS credentials and configuration
```

## Configuration

Update your `.env` file with:

```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
BEDROCK_MODEL_ID=anthropic.claude-v2
```

## Running the Application

### Development Mode

```bashware/amazon-bedrock-app/main.py
```

The API will be available at `http://localhost:8000`

## Project Structure

```
├── middleware/
│   └── amazon-bedrock-app/
│       └── main.py                 # Python application entry point
├── DevOps/
│   └── setup.sh                    # Setup script
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Python tool configuration
├── Makefile                        # Development commands
├── .env                            # Environment variables (create from .env.example)
├── CONTRIBUTING.md                 # Contribution guidelines
├── CHANGELOG.md                    # Version history
└── README.md                       # This file
```
.env.example                    # Example environment variables
├── README.md                       # This file
└── LICENSE                         # MIT Licens
- `POST /api/search` - Search files using Bedrock agent
- `GET /api/files` - List available files
- `GET /api/files/{id}` - Retrieve specific file

## Testing

```bash
# Using make
make test

# Or manually
source venv/bin/activate
pytest middleware/
```

make dev

# R issues and questions, please refer to the [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/).
