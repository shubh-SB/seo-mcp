from typing import Any, List, Optional

import requests


def format_backlinks(backlinks_data: List[Any], domain: str) -> List[Any]:
    """
    Format backlinks data
    """
    if backlinks_data and len(backlinks_data) > 1 and "topBacklinks" in backlinks_data[1]:
        backlinks = backlinks_data[1]["topBacklinks"]["backlinks"]
        print(f"SUCCESS: Retrieved {len(backlinks)} backlinks for {domain}")
        # Only keep necessary fields
        simplified_backlinks = []
        for backlink in backlinks:
            simplified_backlink = {
                "anchor": backlink.get("anchor", ""),
                "domainRating": backlink.get("domainRating", 0),
                "title": backlink.get("title", ""),
                "urlFrom": backlink.get("urlFrom", ""),
                "urlTo": backlink.get("urlTo", ""),
                "edu": backlink.get("edu", False),
                "gov": backlink.get("gov", False),
            }
            simplified_backlinks.append(simplified_backlink)
        return simplified_backlinks
    else:
        print(f"ERROR: No valid backlinks data retrieved for {domain}")
        return []
    

def get_backlinks(signature: str, valid_until: str, domain: str) -> Optional[List[Any]]:
    if not signature or not valid_until:
        print("ERROR: No signature or valid_until, cannot proceed")
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeBacklinksList"
    payload = {
        "reportType": "TopBacklinks",
        "signedInput": {
            "signature": signature,
            "input": {
                "validUntil": valid_until,
                "mode": "subdomains",
                "url": f"{domain}/"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"ERROR: Failed to get backlinks, status code: {response.status_code}, response: {response.text}")
        return None
    
    data = response.json()

    return format_backlinks(data, domain)



