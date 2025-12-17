"""
ComfyUI API Client
Handles communication with ComfyUI backend server
"""

import json
import urllib.request
import urllib.error
import urllib.parse
import uuid
import time
import io
from typing import Dict, List, Tuple, Optional


class ComfyUIClient:
    """Client for interacting with ComfyUI API"""
    
    def __init__(self, server_address: str = "http://localhost:8188"):
        """
        Initialize ComfyUI client
        
        Args:
            server_address: URL of the ComfyUI server
        """
        self.server_address = server_address.rstrip('/')
        self.client_id = str(uuid.uuid4())
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to ComfyUI server
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            url = f"{self.server_address}/system_stats"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    return True, "Connected successfully to ComfyUI server"
                else:
                    return False, f"Server returned status {response.status}"
        except urllib.error.URLError as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def queue_prompt(self, workflow: Dict) -> Optional[str]:
        """
        Queue a workflow prompt to ComfyUI
        
        Args:
            workflow: ComfyUI workflow dictionary
            
        Returns:
            Prompt ID if successful, None otherwise
        """
        try:
            prompt_data = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            
            data = json.dumps(prompt_data).encode('utf-8')
            url = f"{self.server_address}/prompt"
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('prompt_id')
                
        except Exception as e:
            print(f"Error queuing prompt: {str(e)}")
            return None
    
    def get_history(self, prompt_id: str) -> Optional[Dict]:
        """
        Get history/results for a prompt
        
        Args:
            prompt_id: The prompt ID to query
            
        Returns:
            History dictionary if available, None otherwise
        """
        try:
            url = f"{self.server_address}/history/{prompt_id}"
            req = urllib.request.Request(url, method='GET')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                history = json.loads(response.read().decode('utf-8'))
                return history.get(prompt_id)
                
        except Exception as e:
            print(f"Error getting history: {str(e)}")
            return None
    
    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> Optional[bytes]:
        """
        Download an image from ComfyUI
        
        Args:
            filename: Name of the image file
            subfolder: Subfolder within the output directory
            folder_type: Type of folder (output, input, temp)
            
        Returns:
            Image data as bytes if successful, None otherwise
        """
        try:
            params = {
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type
            }
            
            url = f"{self.server_address}/view?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, method='GET')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read()
                
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return None
    
    def upload_image(self, image_data: bytes, filename: str, subfolder: str = "", overwrite: bool = True) -> Optional[Dict]:
        """
        Upload an image to ComfyUI
        
        Args:
            image_data: Image data as bytes
            filename: Name for the uploaded file
            subfolder: Subfolder within the input directory
            overwrite: Whether to overwrite existing file
            
        Returns:
            Upload result dictionary if successful, None otherwise
        """
        try:
            # Prepare multipart form data
            boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
            
            body = io.BytesIO()
            
            # Add image field
            body.write(f'--{boundary}\r\n'.encode())
            body.write(f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode())
            body.write(b'Content-Type: image/png\r\n\r\n')
            body.write(image_data)
            body.write(b'\r\n')
            
            # Add overwrite field
            body.write(f'--{boundary}\r\n'.encode())
            body.write(b'Content-Disposition: form-data; name="overwrite"\r\n\r\n')
            body.write(b'true\r\n' if overwrite else b'false\r\n')
            
            # Add subfolder field if specified
            if subfolder:
                body.write(f'--{boundary}\r\n'.encode())
                body.write(b'Content-Disposition: form-data; name="subfolder"\r\n\r\n')
                body.write(subfolder.encode())
                body.write(b'\r\n')
            
            body.write(f'--{boundary}--\r\n'.encode())
            
            url = f"{self.server_address}/upload/image"
            req = urllib.request.Request(
                url,
                data=body.getvalue(),
                headers={
                    'Content-Type': f'multipart/form-data; boundary={boundary}'
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result
                
        except Exception as e:
            print(f"Error uploading image: {str(e)}")
            return None
    
    def wait_for_completion(self, prompt_id: str, timeout: int = 300, poll_interval: float = 1.0) -> Optional[Dict]:
        """
        Wait for a prompt to complete and return results
        
        Args:
            prompt_id: The prompt ID to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between polls in seconds
            
        Returns:
            History dictionary if completed, None if timeout or error
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            history = self.get_history(prompt_id)
            
            if history is not None:
                # Check if execution is complete
                if 'outputs' in history:
                    return history
            
            time.sleep(poll_interval)
        
        print(f"Timeout waiting for prompt {prompt_id}")
        return None
    
    def get_output_images(self, history: Dict) -> List[Tuple[str, str, str]]:
        """
        Extract output image information from history
        
        Args:
            history: History dictionary from ComfyUI
            
        Returns:
            List of tuples (filename, subfolder, folder_type)
        """
        images = []
        
        if 'outputs' not in history:
            return images
        
        for node_id, node_output in history['outputs'].items():
            if 'images' in node_output:
                for image in node_output['images']:
                    filename = image.get('filename', '')
                    subfolder = image.get('subfolder', '')
                    folder_type = image.get('type', 'output')
                    images.append((filename, subfolder, folder_type))
        
        return images


def register():
    """Register module"""
    pass


def unregister():
    """Unregister module"""
    pass
