# Upgrade_Psc_MCQ_Extractor
🤖 AI-powered MCQ Extractor API - Upload PDFs, extract Multiple Choice Questions using Google Generative AI, get structured JSON output with FastAPI backend

A FastAPI-based web service that extracts Multiple Choice Questions (MCQs) from PDF documents using Google's Generative AI with **99.5+% accuracy** on heavy PDFs and 100% accuracy on small PDFs. Upload PDF files and get structured JSON output with extracted questions through an intuitive web interface.

## 🚀 Features

- **High Accuracy**: 99.5+% extraction accuracy on heavy/complex PDFs
- **PDF Upload & Processing**: Upload PDF documents for AI-powered MCQ extraction
- **Background Processing**: Non-blocking file processing with real-time status updates
- **Google Generative AI**: Leverages Google's AI models for intelligent question extraction
- **Batch Processing**: Efficiently handles large documents through batch processing
- **Custom Input Support**: Customize extraction parameters and instructions
- **Web Interface**: Built-in HTML interface for easy file uploads
- **Metadata Tracking**: Complete audit trail with timestamps and processing status
- **Auto-redirect**: Seamless redirect to status page after upload
- **RESTful API**: Clean REST endpoints for integration

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Background Processing](#background-processing)
- [AI Integration](#ai-integration)
- [Error Handling](#error-handling)
- [Contributing](#contributing)

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Google Generative AI API key
- PDF documents for processing

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/trogon-php/Upgrade_Psc_MCQ_Extractor.git
cd Upgrade_Psc_MCQ_Extractor
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
# Create .env file with your Google AI API key
echo "API_KEY=your_google_generative_ai_api_key_here" > .env
```

4. **Create required directories**
```bash
mkdir -p tempUploads Outputs metadata
```

5. **Initialize metadata file**
```bash
echo "[]" > metadata/metadata_list.json
```

6. **Edit your HTML interface**
```bash
# cd static
# vi index.html
// configure as per your design
```

7. **Run the application**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
API_KEY=your_google_generative_ai_api_key
```

### Google Generative AI Setup

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add the API key to your `.env` file
4. Ensure your API key has appropriate permissions

### Directory Structure

```
Upgrade_Psc_MCQ_Extractor/
├── main.py                 # FastAPI application
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── tempUploads/           # Temporary PDF storage
├── Outputs/               # Processed JSON files
├── metadata/              # Processing metadata
│   └── metadata_list.json # Tracking file
├── static/                # Static web files
│   └── index.html        # Upload interface
└── mcq_extractor/         # Core processing module
    └── batch_processor.py # AI-powered extraction
```

## 🔌 API Endpoints

### 1. Root Endpoint
```http
GET /
```
Returns welcome message and API status.

**Response:**
```json
{
  "message": "Welcome to the MCQ Extractor!"
}
```

### 2. Upload Interface
```http
GET /upload
```
Serves the HTML upload interface from `static/index.html`.

### 3. File Upload & Processing
```http
POST /upload
```
Upload PDF file for MCQ extraction with auto-redirect to status page.

**Request:**
- `file`: PDF file (multipart/form-data)
- `customInput`: Processing instructions (form field)

**Response:**
- **302 Redirect** to `/metadata/{uuid}` for status tracking

### 4. Get All Metadata
```http
GET /metadata
```
Retrieve all processing metadata and history.

**Response:**
```json
[
  {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "original_filename": "document.pdf",
    "pdf_filename": "123e4567-e89b-12d3-a456-426614174000.pdf",
    "json_filename": "123e4567-e89b-12d3-a456-426614174000.json",
    "status": "Processed",
    "upload_timestamp": "2024-01-15T10:30:00Z",
    "userId": "demoUser123"
  }
]
```

### 5. Get Processing Status
```http
GET /metadata/{uuid}
```
Get specific file processing status and metadata.

**Response:**
```json
{
  "message": "File Uploaded Successfully",
  "metadata": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000",
    "original_filename": "document.pdf",
    "pdf_filename": "123e4567-e89b-12d3-a456-426614174000.pdf",
    "json_filename": "123e4567-e89b-12d3-a456-426614174000.json",
    "status": "Processing",
    "upload_timestamp": "2024-01-15T10:30:00Z",
    "userId": "demoUser123"
  }
}
```

## 💻 Usage Examples

### Web Interface Usage

1. Navigate to `http://localhost:8000/upload`
2. Select your PDF file
3. Enter custom extraction instructions
4. Click upload
5. Automatically redirected to status page
6. Refresh to see processing updates

### Using cURL

**Upload a PDF file:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf" \
  -F "customInput=Extract all multiple choice questions with detailed explanations"
```

**Check processing status:**
```bash
curl "http://localhost:8000/metadata/123e4567-e89b-12d3-a456-426614174000"
```

### Using Python requests

```python
import requests

# Upload file
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    data = {'customInput': 'Extract MCQs with explanations and difficulty levels'}
    response = requests.post('http://localhost:8000/upload', files=files, data=data, allow_redirects=False)
    
# Get redirect location
redirect_url = response.headers.get('location')
unique_id = redirect_url.split('/')[-1]

# Check status
status_response = requests.get(f'http://localhost:8000/metadata/{unique_id}')
status = status_response.json()
print(f"Processing Status: {status['metadata']['status']}")
```

## 🔄 Background Processing

The API uses FastAPI's `BackgroundTasks` for efficient processing:

### Processing Flow

1. **File Upload**: PDF saved to `tempUploads/`
2. **Metadata Creation**: Tracking record created
3. **Background Task**: Processing starts asynchronously
4. **Auto-redirect**: User redirected to status page
5. **AI Processing**: Google Generative AI extracts MCQs
6. **Result Storage**: JSON output saved to `Outputs/`
7. **Status Update**: Metadata updated with completion status

### Processing States

- `Processing`: File is being processed by AI
- `Processed`: Successfully completed with MCQs extracted
- `Processed , No questions found`: No MCQs detected in the PDF
- `Error`: Processing failed (file not found, etc.)

## 🤖 AI Integration

### Google Generative AI Features

- **High Accuracy**: 99.5+% extraction accuracy on heavy/complex PDFs
- **Intelligent Extraction**: Context-aware MCQ identification
- **Batch Processing**: Handles large documents efficiently
- **Custom Instructions**: Tailored extraction based on user input
- **Structured Output**: Consistent JSON format for results

### Custom Input Examples

```text
"Extract all multiple choice questions with explanations"
"Focus on technical questions only"
"Extract questions with difficulty levels"
"Include answer explanations and rationale"
```

## 📄 Dependencies

```txt
fastapi
pdfplumber
python-dotenv
google-generativeai
uuid
```

### Key Components

- **FastAPI**: High-performance web framework
- **pdfplumber**: PDF text extraction
- **google-generativeai**: AI-powered question extraction
- **python-dotenv**: Environment variable management
- **uuid**: Unique identifier generation

## 🛡️ Error Handling

### Common Scenarios

- **File Not Found**: Graceful handling when uploaded file is missing
- **No Questions Found**: Appropriate status when PDF contains no MCQs
- **API Errors**: Proper error responses for invalid requests
- **Processing Failures**: Background task error handling

### HTTP Status Codes

- `200`: Success
- `302`: Redirect after upload
- `404`: Metadata not found
- `500`: Server error during processing

## 📁 Output Format

Extracted MCQs are saved as JSON files in the `Outputs/` directory:

```json
[
  {
    "question": "What is the primary function of mitochondria?",
    "options": [
      "Protein synthesis",
      "Energy production",
      "DNA replication",
      "Waste removal"
    ],
    "correct_answer": "2" or 2,
  }
]
```

## 🔧 Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Debug Mode

Enable debug prints by checking the console output:
- `"Saved"` - Metadata save operation
- `"update"` - Metadata update operation
- `"Before adding background task"` - Task queuing
- `"After adding background task"` - Task queued successfully

### Extending the Processor

Customize the `MCQBatchProcessor` in `mcq_extractor/batch_processor.py`:

```python
class MCQBatchProcessor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Initialize Google Generative AI client
        
    def process_pdf_in_batches(self, file_path: str, custom_input: str):
        # Your custom AI processing logic
        pass
```

## 📊 Performance Considerations

- **Background Processing**: Non-blocking uploads for better user experience
- **File Management**: Automatic cleanup of temporary files
- **AI Rate Limits**: Respect Google Generative AI API limits
- **Memory Usage**: Efficient PDF processing with pdfplumber


## 🎯 Quick Start

1. Get Google Generative AI API key
2. Clone repo and install dependencies
3. Set API_KEY in .env file
4. Run `uvicorn main:app --reload`
5. Visit `http://localhost:8000/upload`
6. Upload PDF and watch the magic happen!

**Built with ❤️ using FastAPI and Google Generative AI**
