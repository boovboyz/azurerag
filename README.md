# SharePoint RAG with Azure AI Search

A Retrieval-Augmented Generation (RAG) application that enables Q&A over SharePoint documents using Azure AI Search and OpenAI. **Now with permission-aware document access!**

## Architecture

```
User Request + Azure AD Token
          ↓
     [API + Auth]
          ↓
   Extract user groups
          ↓
   [Security Filter]
   allowed_groups ∩ user_groups
          ↓
   [Azure Search]
   Only matching docs
          ↓
      [RAG Chain]
          ↓
      Response
```

## Features

- **SharePoint Integration**: Connects to SharePoint via Microsoft Graph API
- **Multi-format Support**: Parses PDF, DOCX, PPTX, and XLSX files
- **Vector Search**: Uses Azure AI Search for semantic document retrieval
- **RAG Pipeline**: LangChain-based RAG with OpenAI GPT models
- **🔐 Permission-Aware Access**: Respects SharePoint document permissions via Azure AD authentication

## Setup

### Prerequisites

- Python 3.10+
- Azure AI Search service
- OpenAI API key
- Azure AD app registration with SharePoint permissions (`Sites.Read.All`)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/boovboyz/azurerag.git
   cd azurerag
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Discover SharePoint IDs:
   ```bash
   python test.py "https://yourtenant.sharepoint.com/sites/YourSite/Shared Documents/YourFolder"
   ```
   Copy the output SITE_ID, DRIVE_ID, and FOLDER_ID to your `.env` file.

### Usage

1. **Ingest documents** from SharePoint (now includes permissions):
   ```bash
   python scripts/ingest_sharepoint.py
   ```

2. **Start the API server**:
   ```bash
   uvicorn rag_app.api:app --host 0.0.0.0 --port 8000
   ```

3. **Query your documents**:
   ```bash
   # Unauthenticated (no permission filtering)
   curl -X POST "http://localhost:8000/ask?question=What%20is%20in%20my%20documents"
   
   # Authenticated (with permission filtering)
   curl -X POST "http://localhost:8000/ask/secure?question=..." \
     -H "Authorization: Bearer <azure-ad-token>"
   ```

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/ask?question=<query>` | No | Query all documents (no filtering) |
| POST | `/ask/secure?question=<query>` | Yes | Query with permission filtering |
| GET | `/me` | Yes | Get authenticated user info |
| GET | `/health` | No | Health check |

## Project Structure

```
├── rag_app/
│   ├── api.py              # FastAPI endpoints (v2.0)
│   ├── auth.py             # Azure AD JWT authentication
│   ├── azure_search.py     # Azure AI Search vector store
│   ├── chunking.py         # Text splitting
│   ├── config.py           # Environment configuration
│   ├── document_parser.py  # PDF/DOCX/PPTX/XLSX parsing
│   ├── embeddings.py       # OpenAI embeddings
│   ├── ingestion.py        # Document ingestion with ACLs
│   ├── rag_chain.py        # RAG pipeline with security filters
│   └── sharepoint_loader.py # SharePoint client + permissions
├── scripts/
│   └── ingest_sharepoint.py # Ingestion CLI
├── test.py                  # SharePoint ID discovery tool
├── requirements.txt
└── .env.example
```

## 🔐 Permission-Aware Access

Documents are now indexed with their SharePoint permissions. When using the `/ask/secure` endpoint:

1. User authenticates with Azure AD token
2. User's groups are extracted from the token
3. Azure Search filters documents to only those the user can access
4. RAG generates answers from authorized documents only

### Azure AD Setup for Secure Access

1. Register an API application in Azure AD
2. Configure token to include group claims
3. Set `AZURE_AD_API_CLIENT_ID` in `.env`
4. Users authenticate and pass Bearer token to `/ask/secure`

## License

MIT

