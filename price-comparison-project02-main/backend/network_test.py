import socket
import urllib.request

print("Testing Python network connectivity...\n")

# Test 1: DNS lookup for google.com
try:
    print("Test 1: DNS lookup for google.com")
    addr = socket.getaddrinfo('google.com', 443)
    print(f"✓ Success: {addr[0]}\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")

# Test 2: HTTP request to google.com
try:
    print("Test 2: HTTP request to google.com")
    response = urllib.request.urlopen('http://google.com', timeout=5)
    print(f"✓ Success: Status {response.status}\n")
except Exception as e:
    print(f"✗ Failed: {e}\n")

# Test 3: Check if we're behind a proxy
import os
proxy_env = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
print("Test 3: Environment proxy settings")
for var in proxy_env:
    value = os.environ.get(var)
    if value:
        print(f"Found: {var}={value}")

if not any(os.environ.get(var) for var in proxy_env):
    print("No proxy environment variables found")
