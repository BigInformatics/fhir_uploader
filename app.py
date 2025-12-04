"""
FHIR Server Uploader
Uploads processed FHIR bundles to FHIR server with custom authentication
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv


class FHIRUploader:
    """Upload FHIR resources to server with custom authentication"""
    
    def __init__(self, 
                 hostname: str,
                 client_id: str,
                 client_secret: str,
                 batch_size: int = 10,
                 delay_seconds: float = 0.5):
        """
        Initialize FHIR uploader
        
        Args:
            hostname: FHIR server hostname (e.g., 'fhir.example.com')
            client_id: Access Client ID
            client_secret: Access Client Secret
            batch_size: Number of bundles to upload before progress update
            delay_seconds: Delay between uploads to avoid rate limiting
        """
        self.base_url = f"https://{hostname}/fhir/R4"
        self.client_id = client_id
        self.client_secret = client_secret
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        
        # Setup session with retries
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        
        return {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json',
            'CF-Access-Client-Id': self.client_id,
            'CF-Access-Client-Secret': self.client_secret
        }
    
    def test_connection(self) -> bool:
        """Test connection to FHIR server"""
        
        try:
            response = self.session.get(
                f"{self.base_url}/metadata",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ Successfully connected to FHIR server")
                metadata = response.json()
                print(f"  Server: {metadata.get('software', {}).get('name', 'Unknown')}")
                print(f"  Version: {metadata.get('fhirVersion', 'Unknown')}")
                return True
            else:
                print(f"✗ Connection failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Connection error: {str(e)}")
            return False
    
    def upload_bundle(self, bundle: Dict) -> Optional[Dict]:
        """
        Upload a FHIR bundle to the server
        
        Args:
            bundle: FHIR Bundle resource
            
        Returns:
            Response from server or None if failed
        """
        
        try:
            response = self.session.post(
                self.base_url,
                headers=self._get_headers(),
                json=bundle,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"  Upload failed: {response.status_code}")
                print(f"  Response: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"  Upload error: {str(e)}")
            return None
    
    def upload_bundle_file(self, file_path: Path) -> bool:
        """
        Upload a FHIR bundle from file
        
        Args:
            file_path: Path to FHIR bundle JSON file
            
        Returns:
            True if successful, False otherwise
        """
        
        try:
            with open(file_path, 'r') as f:
                bundle = json.load(f)
            
            result = self.upload_bundle(bundle)
            
            if result:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"  Error processing file {file_path.name}: {str(e)}")
            return False
    
    def upload_directory(self, directory: Path) -> Dict[str, int]:
        """
        Upload all FHIR bundles from a directory
        
        Args:
            directory: Directory containing FHIR bundle JSON files
            
        Returns:
            Dictionary with upload statistics
        """
        
        bundle_files = sorted(list(directory.glob("*.json")))
        total_files = len(bundle_files)
        
        print(f"\nUploading {total_files} bundles from {directory}")
        print("=" * 70)
        
        stats = {
            'total': total_files,
            'successful': 0,
            'failed': 0,
            'patients': 0,
            'observations': 0,
            'medications': 0
        }
        
        for idx, file_path in enumerate(bundle_files, 1):
            print(f"[{idx}/{total_files}] Uploading {file_path.name}...", end=" ")
            
            # Count resources in bundle
            try:
                with open(file_path, 'r') as f:
                    bundle = json.load(f)
                
                for entry in bundle.get('entry', []):
                    resource_type = entry['resource'].get('resourceType')
                    if resource_type == 'Patient':
                        stats['patients'] += 1
                    elif resource_type == 'Observation':
                        stats['observations'] += 1
                    elif resource_type == 'MedicationStatement':
                        stats['medications'] += 1
            except:
                pass
            
            # Upload
            success = self.upload_bundle_file(file_path)
            
            if success:
                stats['successful'] += 1
                print("✓")
            else:
                stats['failed'] += 1
                print("✗")
            
            # Progress update
            if idx % self.batch_size == 0:
                print(f"  Progress: {stats['successful']} successful, {stats['failed']} failed")
            
            # Rate limiting delay
            time.sleep(self.delay_seconds)
        
        # Final summary
        print("\n" + "=" * 70)
        print("Upload Summary:")
        print(f"  Total bundles: {stats['total']}")
        print(f"  Successful: {stats['successful']} ({stats['successful']/stats['total']*100:.1f}%)")
        print(f"  Failed: {stats['failed']}")
        print(f"\nResources uploaded:")
        print(f"  Patients: {stats['patients']}")
        print(f"  Observations: {stats['observations']}")
        print(f"  Medications: {stats['medications']}")
        
        return stats
    
    def search_patients(self, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Search for patients on FHIR server
        
        Args:
            params: Search parameters (e.g., {'family': 'Smith'})
            
        Returns:
            Search results bundle
        """
        
        try:
            response = self.session.get(
                f"{self.base_url}/Patient",
                headers=self._get_headers(),
                params=params or {},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Search failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Search error: {str(e)}")
            return None


def main():
    """Main execution"""
    
    # Load environment variables
    load_dotenv()
    
    hostname = os.getenv('HTTP_HOSTNAME')
    client_id = os.getenv('HTTP_CLIENT_ID')
    client_secret = os.getenv('HTTP_CLIENT_SECRET')
    processed_fhir_dir = os.getenv('PROCESSED_FHIR_DIR', './processed_fhir')
    
    if not all([hostname, client_id, client_secret]):
        print("Error: Missing environment variables")
        print("Please set HTTP_HOSTNAME, HTTP_CLIENT_ID, and HTTP_CLIENT_SECRET")
        print("\nCreate a .env file with:")
        print("HTTP_HOSTNAME=your-fhir-server.com")
        print("HTTP_CLIENT_ID=your-client-id")
        print("HTTP_CLIENT_SECRET=your-client-secret")
        return
    
    # Initialize uploader
    uploader = FHIRUploader(
        hostname=hostname,
        client_id=client_id,
        client_secret=client_secret,
        batch_size=10,
        delay_seconds=0.5
    )
    
    # Test connection
    print("Testing FHIR server connection...")
    if not uploader.test_connection():
        print("\nCannot connect to FHIR server. Please check:")
        print("1. Server hostname is correct")
        print("2. Client ID and secret are valid")
        print("3. Network connectivity")
        return
    
    # Upload processed bundles
    input_dir = Path(processed_fhir_dir)
    
    if not input_dir.exists():
        print(f"\nError: Directory {input_dir} does not exist")
        print("Run post_process_fhir.py first to generate processed bundles")
        return
    
    # Upload
    stats = uploader.upload_directory(input_dir)
    
    # Verify upload
    print("\nVerifying upload...")
    search_result = uploader.search_patients({'_count': '10'})
    if search_result:
        total = search_result.get('total', 0)
        print(f"✓ Found {total} patients on server")


if __name__ == "__main__":
    main()
