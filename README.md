# FHIR Server Uploader

Uploads processed FHIR bundles to FHIR server with custom authentication.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root directory with the following environment variables:

### Required Environment Variables

- **HTTP_HOSTNAME**: FHIR server hostname (e.g., `fhir.example.com`)
- **HTTP_CLIENT_ID**: Access Client ID for authentication
- **HTTP_CLIENT_SECRET**: Access Client Secret for authentication

### Optional Environment Variables

- **PROCESSED_FHIR_DIR**: Directory containing processed FHIR bundles (default: `./processed_fhir`)

### Example .env File

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

Then edit `.env`:

```
HTTP_HOSTNAME=your-fhir-server.com
HTTP_CLIENT_ID=your-client-id
HTTP_CLIENT_SECRET=your-client-secret
PROCESSED_FHIR_DIR=./processed_fhir
```

## Usage

Run the uploader:

```bash
python app.py
```

The script will:
1. Load environment variables from `.env`
2. Test connection to the FHIR server
3. Upload all FHIR bundles from the configured directory
4. Verify the upload by searching for patients

## License

MIT License - see LICENSE file for details.
