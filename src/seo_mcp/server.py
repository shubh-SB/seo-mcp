"""
Backlinks MCP Server

This server is used to get the backlinks of a given domain.
"""

import requests
import time
import json
import os
from datetime import datetime
import urllib.parse
from typing import Dict, List, Optional, Tuple, Any, cast

from fastmcp import FastMCP
from seo_mcp.backlinks import get_backlinks
from seo_mcp.keywords import get_keyword_ideas

mcp = FastMCP("SEO MCP")

# CapSolver website: https://dashboard.capsolver.com/passport/register?inviteCode=1dTH7WQSfHD0
# Get API Key from environment variable - must be set for production use
api_key = os.environ.get("CAPSOLVER_API_KEY")
 
# Cache file path for storing signatures
SIGNATURE_CACHE_FILE = "signature_cache.json"

def iso_to_timestamp(iso_date_string: str) -> float:
    """
    Convert ISO 8601 format datetime string to timestamp
    Example: "2025-04-12T14:59:18Z" -> 1744916358.0
    """
    # Handle UTC time represented by "Z"
    if iso_date_string.endswith('Z'):
        iso_date_string = iso_date_string[:-1] + '+00:00'
    dt = datetime.fromisoformat(iso_date_string)
    return dt.timestamp()

def get_capsolver_token(site_url: str) -> Optional[str]:
    """
    Step 1: Use CapSolver to solve the captcha and get a token
    
    Args:
        site_url: Site URL to query
        
    Returns:
        Verification token or None if failed
    """
    if not api_key:
        print("ERROR: CAPSOLVER_API_KEY environment variable not set")
        return None
    
    payload = {
        "clientKey": api_key,
        "task": {
            "type": 'AntiTurnstileTaskProxyLess',
            "websiteKey": "0x4AAAAAAAAzi9ITzSN9xKMi",  # site key of your target site: ahrefs.com,
            "websiteURL": site_url,
            "metadata": {
                "action": ""  # optional
            }
        }
    }
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        print(f"ERROR: Failed to create captcha task: {res.text}")
        return None
    print(f"INFO: Got taskId: {task_id}, waiting for solution...")
 
    while True:
        time.sleep(1)  # delay
        payload = {"clientKey": api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        resp = res.json()
        status = resp.get("status")
        if status == "ready":
            token = resp.get("solution", {}).get('token')
            print(f"INFO: Captcha token obtained successfully")
            return token
        if status == "failed" or resp.get("errorId"):
            print(f"ERROR: Captcha solving failed: {res.text}")
            return None

def save_signature_to_cache(signature: str, valid_until: str, domain: str) -> bool:
    """
    Save signature information to local cache file
    
    Args:
        signature: Obtained signature
        valid_until: Signature expiration time
        domain: Domain name
        
    Returns:
        True if saved successfully, False otherwise
    """
    # Read existing cache
    cache_data: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(SIGNATURE_CACHE_FILE):
        try:
            with open(SIGNATURE_CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
        except:
            pass
    
    # Update cache for current domain
    cache_data[domain] = {
        "signature": signature,
        "valid_until": valid_until,
        "timestamp": datetime.now().timestamp()
    }
    
    try:
        with open(SIGNATURE_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f)
        print(f"INFO: Signature cached to file: {SIGNATURE_CACHE_FILE}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to cache signature: {e}")
        return False

def load_signature_from_cache(domain: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Load signature information for a specific domain from local cache file
    Returns the signature and valid_until if cache is valid, otherwise None
    
    Args:
        domain: Domain to query
        
    Returns:
        (signature, valid_until) tuple, or (None, None) if no valid cache
    """
    if not os.path.exists(SIGNATURE_CACHE_FILE):
        print("INFO: Cache file doesn't exist")
        return None, None
    
    try:
        with open(SIGNATURE_CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
        
        # Check if cache exists for current domain
        if domain not in cache_data:
            print(f"INFO: No signature in cache for domain: {domain}")
            return None, None
        
        domain_cache = cache_data[domain]
        
        # Check if signature is expired
        valid_until = domain_cache.get("valid_until")
        
        if valid_until:
            # Convert ISO date string to timestamp for comparison
            valid_until_timestamp = iso_to_timestamp(valid_until)
            current_time = time.time()
            
            if current_time < valid_until_timestamp:
                time_left = int(valid_until_timestamp - current_time)
                print(f"INFO: Using cached signature for {domain}, valid for {time_left} seconds")
                return domain_cache.get("signature"), valid_until
            else:
                print(f"INFO: Cached signature for {domain} has expired")
                return None, None
        else:
            print("INFO: No valid_until information in cache data")
            return None, None
    except Exception as e:
        print(f"ERROR: Failed to read cached signature: {e}")
        return None, None

def get_signature(token: str, domain: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Step 2: Get signature and validUntil parameters using the token
    
    Args:
        token: Verification token
        domain: Domain to query
        
    Returns:
        (signature, valid_until) tuple, or (None, None) if failed
    """
    url = "https://ahrefs.com/v4/stGetFreeBacklinksOverview"
    payload = {
        "captcha": token,
        "mode": "subdomains",
        "url": domain
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"ERROR: Failed to get signature, status code: {response.status_code}")
        print(response.text)
        return None, None
    
    data = response.json()
    print(f"DEBUG: Signature data received")
    
    try:
        # Assuming data format is always ['Ok', {signature object}]
        if isinstance(data, list) and len(cast(List[Any], data)) > 1:
            second_element: Dict[str, Any] = cast(Dict[str, Any], data[1])
            signature: str = cast(str, second_element['signedInput']['signature'])
            valid_until: str = cast(str, second_element['signedInput']['input']['validUntil'])
            
            print(f"INFO: Signature obtained, valid until: {valid_until}")
            
            # Save the new signature to cache
            save_signature_to_cache(signature, valid_until, domain)
            
            return signature, valid_until
        else:
            print("ERROR: Unexpected response data format")
            return None, None
    except Exception as e:
        print(f"ERROR: Failed to parse signature data: {e}")
        return None, None


@mcp.tool()
def get_backlinks_list(domain: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get backlinks list for the specified domain
    Args:
        domain (str): The domain to query
    Returns:
        List of backlinks for the domain, containing title, URL, domain rating, etc.
    """
    # Try to get signature from cache
    signature, valid_until = load_signature_from_cache(domain)
    
    # If no valid signature in cache, get a new one
    if not signature or not valid_until:
        # Step 1: Get token
        site_url = f"https://ahrefs.com/backlink-checker/?input={domain}&mode=subdomains"
        token = get_capsolver_token(site_url)
        if not token:
            print(f"ERROR: Failed to get verification token for domain: {domain}")
            raise Exception(f"Failed to get verification token for domain: {domain}")
        
        # Step 2: Get signature and validUntil
        signature, valid_until = get_signature(token, domain)
        if not signature or not valid_until:
            print(f"ERROR: Failed to get signature for domain: {domain}")
            raise Exception(f"Failed to get signature for domain: {domain}")
    
    # Step 3: Get backlinks list
    return get_backlinks(signature, valid_until, domain)


@mcp.tool()
def keyword_generator(keyword: str, country: str = "us", search_engine: str = "Google") -> Optional[List[str]]:
    """
    Get keyword ideas for the specified keyword
    """
    site_url = f"https://ahrefs.com/keyword-generator/?country={country}&input={urllib.parse.quote(keyword)}"
    token = get_capsolver_token(site_url)
    if not token:
        print(f"ERROR: Failed to get verification token for keyword: {keyword}")
        raise Exception(f"Failed to get verification token for keyword: {keyword}")
    return get_keyword_ideas(token, keyword, country, search_engine)

# Main execution

def main():
    """Run the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
