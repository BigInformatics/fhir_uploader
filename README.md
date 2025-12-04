# FHIR Server Uploader

A Python application for uploading FHIR (Fast Healthcare Interoperability Resources) bundles to a FHIR server with custom authentication support.

## Features

- **FHIR R4 Compliant**: Upload FHIR bundles to R4-compatible servers
- **Custom Authentication**: Support for Cloudflare Access authentication headers
- **Batch Processing**: Upload multiple FHIR bundles from a directory
- **Retry Logic**: Automatic retries for failed requests with exponential backoff
- **Rate Limiting**: Configurable delays between uploads to avoid server throttling
- **Progress Tracking**: Real-time progress updates and upload statistics
- **Resource Counting**: Tracks uploaded Patients, Observations, and Medications
- **Connection Testing**: Verify server connectivity before uploading

## Prerequisites

- Python 3.8 or higher
- Access to a FHIR R4 server
- Valid client ID and client secret for authentication

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/BigInformatics/fhir_uploader.git
cd fhir_uploader
```

### 2. Set Up Virtual Environment

Create and activate a virtual environment named `.venv`:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Create Environment File

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

### 2. Edit `.env` File

Update the `.env` file with your FHIR server credentials:

```env
HTTP_HOSTNAME=your-fhir-server.com
HTTP_CLIENT_ID=your-client-id
HTTP_CLIENT_SECRET=your-client-secret
```

**Environment Variables:**

- `HTTP_HOSTNAME`: Your FHIR server hostname (without https://)
- `HTTP_CLIENT_ID`: Cloudflare Access Client ID for authentication
- `HTTP_CLIENT_SECRET`: Cloudflare Access Client Secret for authentication

## Usage

### Uploading FHIR Bundles

1. **Prepare Your Data**: Place your FHIR bundle JSON files in a directory (default: `./processed_fhir`)

2. **Run the Uploader**:

```bash
python app.py
```

The application will:
- Test the connection to the FHIR server
- Upload all JSON files from the `processed_fhir` directory
- Display progress and statistics
- Verify the upload by searching for patients

### Using as a Library

You can also use the `FHIRUploader` class in your own Python scripts:

```python
from app import FHIRUploader
from pathlib import Path

# Initialize uploader
uploader = FHIRUploader(
    hostname="your-fhir-server.com",
    client_id="your-client-id",
    client_secret="your-client-secret",
    batch_size=10,
    delay_seconds=0.5
)

# Test connection
if uploader.test_connection():
    # Upload a single bundle file
    success = uploader.upload_bundle_file(Path("path/to/bundle.json"))
    
    # Upload all bundles from a directory
    stats = uploader.upload_directory(Path("./processed_fhir"))
    
    # Search for patients
    results = uploader.search_patients({'family': 'Smith'})
```

## Project Structure

```
fhir_uploader/
├── app.py              # Main application and FHIRUploader class
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment configuration
├── LICENSE             # MIT License
└── README.md           # This file
```

## Key Components

### FHIRUploader Class

**Constructor Parameters:**
- `hostname`: FHIR server hostname
- `client_id`: Authentication client ID
- `client_secret`: Authentication client secret
- `batch_size`: Number of bundles between progress updates (default: 10)
- `delay_seconds`: Delay between uploads in seconds (default: 0.5)

**Main Methods:**
- `test_connection()`: Test connection to FHIR server
- `upload_bundle(bundle)`: Upload a single FHIR bundle
- `upload_bundle_file(file_path)`: Upload a bundle from a file
- `upload_directory(directory)`: Upload all bundles from a directory
- `search_patients(params)`: Search for patients on the server

## Error Handling

The application includes robust error handling:
- Automatic retries for failed requests (3 attempts)
- Backoff strategy for rate limiting
- Detailed error messages for troubleshooting
- Connection testing before upload

## Example Output

```
Testing FHIR server connection...
✓ Successfully connected to FHIR server
  Server: HAPI FHIR Server
  Version: 4.0.1

Uploading 25 bundles from ./processed_fhir
======================================================================
[1/25] Uploading bundle_001.json... ✓
[2/25] Uploading bundle_002.json... ✓
...
  Progress: 10 successful, 0 failed
...
======================================================================
Upload Summary:
  Total bundles: 25
  Successful: 25 (100.0%)
  Failed: 0

Resources uploaded:
  Patients: 25
  Observations: 150
  Medications: 75

Verifying upload...
✓ Found 25 patients on server
```

## Dependencies

- `requests>=2.31.0` - HTTP library for API calls
- `python-dotenv>=1.0.0` - Environment variable management
- `numpy>=1.24.0` - Numerical operations
- `urllib3>=2.0.0` - HTTP client

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Copyright

Copyright (c) 2025 Informatics FYI, Inc.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
