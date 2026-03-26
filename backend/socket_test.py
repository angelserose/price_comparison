import socket
import subprocess

print("Testing Supabase hostname resolution...\n")

hostname = "db.iruysnusweouqqmvmwtq.supabase.co"

# Try nslookup
print("1. Testing with nslookup:")
try:
    result = subprocess.run(['nslookup', hostname], capture_output=True, text=True, timeout=5)
    print(result.stdout)
except Exception as e:
    print(f"Error: {e}\n")

# Try getaddrinfo with AF_INET only (IPv4)
print("2. Testing with Python socket (IPv4 only):")
try:
    addr = socket.getaddrinfo(hostname, 5432, socket.AF_INET, socket.SOCK_STREAM)
    print(f"✓ IPv4 resolved: {addr[0]}\n")
except Exception as e:
    print(f"✗ IPv4 failed: {e}\n")

# Try getaddrinfo with AF_INET6 only (IPv6)
print("3. Testing with Python socket (IPv6 only):")
try:
    addr = socket.getaddrinfo(hostname, 5432, socket.AF_INET6, socket.SOCK_STREAM)
    print(f"✓ IPv6 resolved: {addr[0]}\n")
except Exception as e:
    print(f"✗ IPv6 failed: {e}\n")

# Try direct socket connection
print("4. Testing direct socket connection:")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((hostname, 5432))
    if result == 0:
        print(f"✓ Connection successful!\n")
    else:
        print(f"✗ Connection failed: {result}\n")
    sock.close()
except Exception as e:
    print(f"✗ Error: {e}\n")
