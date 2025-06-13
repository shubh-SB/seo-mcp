import requests
import json

url = "http://0.0.0.0:8000/mcp"  # Use the root URL for JSON-RPC
# url = "https://e109ff52be8ae2f43000e6be358dc3ea.serveo.net/mcp"  # Use the root URL for JSON-RPC
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


# The full JSON-RPC request payload
jsonrpc_payload_for_get_backlinks_list = {
    "jsonrpc": "2.0",
    "method": "tools/call", # The name of your tool
    "params": {
        "name": "get_backlinks_list",  #<-- The actual tool name
        "arguments": {                 # <-- The arguments for your tool
            "domain": "salarybox.in",
        }
    },
    "id": "123" # A unique request ID
}

jsonrpc_payload_for_get_traffic = {
    "jsonrpc": "2.0",
    "method": "tools/call", # The name of your tool
    "params": {
        "name": "get_traffic",  #<-- The actual tool name
        "arguments": {                 # <-- The arguments for your tool
            "domain_or_url": "https://salarybox.in",
            # "country": "in",
            # "mode": "subdomains",
        }
    },
    "id": "123" # A unique request ID
}


def send_req():
    print("\n--- JSON payload being sent ---")
    print(json.dumps(jsonrpc_payload_for_get_traffic, indent=2))
    print("-----------------------------\n")
    response = requests.post(url, headers=headers, data=json.dumps(jsonrpc_payload_for_get_traffic), stream=True)

    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', '')

        if 'text/event-stream' in content_type:
            print("Received Server-Sent Event stream:")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        try:
                            event_data = json.loads(decoded_line[len('data: '):])
                            print("Event Data:", event_data)
                        except json.JSONDecodeError:
                            print("Could not decode JSON from SSE line:", decoded_line)
                    else:
                        print("Non-data SSE line:", decoded_line)
        elif 'application/json' in content_type:
            print("Received JSON response:")
            try:
                print(response.json())
            except json.JSONDecodeError:
                print("Could not decode JSON from response:", response.text)
        else:
            print("Received unknown content type:", content_type)
            print("Raw response:", response.text)
    else:
        print("Error Status Code:", response.status_code)
        print("Error Body:", response.text)



if __name__ == "__main__":
    send_req()
