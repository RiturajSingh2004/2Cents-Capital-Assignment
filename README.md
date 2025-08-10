# ADGM Corporate Agent

An AI-powered legal assistant for Abu Dhabi Global Market (ADGM) document compliance review and validation.

## 🚀 Features

- **Document Upload & Analysis**: Upload .docx documents for automated compliance checking
- **ADGM Compliance Validation**: Verify documents against ADGM regulations and requirements  
- **Red Flag Detection**: Identify legal issues, inconsistencies, and violations
- **Smart Document Markup**: Add contextual comments and highlights to original documents
- **Comprehensive Reporting**: Generate detailed JSON reports with findings and recommendations
- **RAG-Enhanced Analysis**: Retrieval-Augmented Generation using ADGM knowledge base
- **Gemini 2.0 Flash Integration**: Fast, efficient AI analysis with Google's latest model

## 📋 Supported Document Types

- **Memorandum of Association**
- **Articles of Association**
- **Company Registration Applications**
- **Board Resolutions**
- Additional corporate documents (extensible)

## 🛠️ Architecture

```
ADGM Corporate Agent
├── FastAPI Backend (Python)
├── Gemini 2.0 Flash API (AI Analysis)
├── ChromaDB (Vector Knowledge Base)
├── Document Processing (python-docx, mammoth)
└── REST API (JSON responses)
```

## ⚡ Quick Start

### 1. Prerequisites

- Python 3.9+
- Google Gemini API key
- 2GB+ available disk space

### 2. Installation

```bash
# Clone repository
git clone <repository-url>
cd adgm-corporate-agent

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 3. Configuration

Edit `.env` file:

```bash
# Required: Get your API key from https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Adjust settings
MAX_FILE_SIZE=52428800
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
MAX_CONCURRENT_ANALYSES=5
```

### 4. Start the Server

```bash
# Using startup script (recommended)
python run.py

# Or directly with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start at `http://localhost:8000`

## 📖 API Documentation

Once running, access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔧 API Endpoints

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload` | Upload document for analysis |
| `GET` | `/api/documents/{id}/status` | Check processing status |
| `GET` | `/api/documents/{id}/analyze` | Get analysis results |
| `GET` | `/api/documents/{id}/report` | Get detailed JSON report |
| `GET` | `/api/documents/{id}/download` | Download marked-up document |
| `DELETE` | `/api/documents/{id}` | Delete document and files |
| `GET` | `/api/documents` | List all processed documents |

### Validation & System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/adgm/validate` | Direct content validation |
| `GET` | `/api/system/status` | System status and statistics |

## 💻 CLI Client Usage

Test the API using the included CLI client:

```bash
# Upload and analyze document (full workflow)
python cli_client.py --file "memorandum.docx"

# Check system status
python cli_client.py --system

# Check document status
python cli_client.py --status "document_id"

# Get analysis results
python cli_client.py --analyze "document_id"

# Download reviewed document
python cli_client.py --download "document_id" --output "reviewed_doc.docx"
```

## 📊 Example Usage

### 1. Upload Document

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@memorandum.docx"
```

Response:
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "data": {
    "document_id": "abc123-def456-789",
    "filename": "memorandum.docx",
    "status": "uploaded",
    "estimated_processing_time": "2-5 minutes"
  }
}
```

### 2. Check Status

```bash
curl "http://localhost:8000/api/documents/abc123-def456-789/status"
```

### 3. Get Analysis Results

```bash
curl "http://localhost:8000/api/documents/abc123-def456-789/analyze"
```

Response:
```json
{
  "success": true,
  "data": {
    "compliance_score": 85.5,
    "completeness_score": 92.0,
    "flags": [
      {
        "severity": "warning",
        "title": "Missing Director Information",
        "description": "Director residential address not specified",
        "suggested_fix": "Add complete director address as per ADGM requirements"
      }
    ],
    "missing_sections": ["Subscriber Details"],
    "summary": "Document mostly compliant with minor issues to address"
  }
}
```

## 🏗️ Project Structure

```
adgm-corporate-agent/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models.py              # Pydantic models
│   ├── services/
│   │   ├── document_parser.py  # Document processing
│   │   ├── gemini_analyzer.py  # AI analysis with Gemini
│   │   └── adgm_validator.py   # ADGM compliance logic
│   └── utils/
│       ├── file_handler.py     # File operations
│       └── report_generator.py # Report generation
├── data/
│   ├── chroma_db/             # Vector database
│   └── adgm_knowledge/        # ADGM regulations
├── uploads/                   # Uploaded documents
├── outputs/                   # Processed documents
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── run.py                    # Startup script
├── cli_client.py             # CLI testing tool
└── README.md                 # This file
```

## 🔍 Key Components

### Document Parser
- Extracts text and structure from .docx files
- Identifies document types automatically
- Preserves formatting for markup insertion

### Gemini Analyzer
- Uses Gemini 2.0 Flash for AI analysis
- Structured prompts for different validation types
- Rate limiting and error handling
- JSON-mode responses for reliability

### ADGM Validator
- ChromaDB vector knowledge base
- ADGM-specific compliance rules
- Section-by-section validation
- Scoring and recommendations

### Report Generator
- Executive summaries
- Detailed JSON reports
- Prioritized recommendations
- Export capabilities

## ⚙️ Configuration Options

### Environment Variables

```bash
# API Configuration
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-2.0-flash-exp

# File Settings
MAX_FILE_SIZE=52428800        # 50MB max
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs

# Processing Settings
MAX_CONCURRENT_ANALYSES=5
MAX_TOKENS_PER_REQUEST=8000

# Database Settings
CHROMA_DB_PATH=data/chroma_db
ADGM_KNOWLEDGE_PATH=data/adgm_knowledge
```

### Document Type Configuration

Modify `config.py` to add new document types:

```python
ADGM_DOCUMENT_TYPES = {
    "new_doc_type": {
        "name": "New Document Type",
        "required_sections": ["section1", "section2"],
        "validation_rules": {...}
    }
}
```

## 🚨 Error Handling

The system includes comprehensive error handling:

- **File validation**: Size, format, and content checks
- **API rate limiting**: Prevents Gemini API throttling
- **Graceful degradation**: Fallback responses when AI analysis fails
- **Background processing**: Non-blocking document analysis
- **Resource cleanup**: Automatic file cleanup and memory management

## 📈 Performance

- **Gemini 2.0 Flash**: Sub-second AI analysis
- **Async processing**: Non-blocking operations
- **Memory efficient**: Streams large documents
- **Rate limiting**: Respects API quotas
- **Concurrent processing**: Multiple documents simultaneously

## 🔒 Security Considerations

- File type validation prevents malicious uploads
- Size limits prevent resource exhaustion
- API key protection through environment variables
- Input sanitization for all user content
- Temporary file cleanup

## 📚 ADGM Knowledge Base

The system includes a curated knowledge base of ADGM regulations:

- Company formation requirements
- Director and shareholder rules
- Share capital requirements
- Compliance obligations
- Prohibited activities

Add more regulations by placing documents in `data/adgm_knowledge/`

## 🧪 Testing

```bash
# Test with sample documents
python cli_client.py --file "test_documents/memorandum.docx"

# System health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs
```

## 🔄 Updates & Maintenance

### Adding New ADGM Regulations

1. Place regulation documents in `data/adgm_knowledge/`
2. Restart the service to re-index
3. Update validation rules in `config.py` if needed

### Monitoring

Check system status:
```bash
curl http://localhost:8000/api/system/status
```

Monitor logs for processing status and errors.

## 🚀 Deployment

### Production Deployment

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "run.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

1. Check the [API documentation](http://localhost:8000/docs)
2. Review the logs for error details
3. Test with the CLI client for debugging
4. Verify Gemini API key configuration

## 🔮 Roadmap

- [ ] Web frontend interface
- [ ] Multi-language document support
- [ ] Advanced workflow automation
- [ ] Integration with ADGM systems
- [ ] Batch processing capabilities
- [ ] Enhanced document templates

---

**Ready to get started?** Follow the Quick Start guide above and begin analyzing ADGM documents with AI-powered compliance checking!