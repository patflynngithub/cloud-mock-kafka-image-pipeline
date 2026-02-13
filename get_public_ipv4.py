"""
Gets the current public IPv4 address of a running Amazon Cloud EC2 instance
"""

import sys
import requests

# =====================================================================

# if __name__ == "__main__":
#    print("Error: This file cannot be run directly. Please import it as a module.")
#    sys.exit(1)

# =====================================================================

def get_public_ipv4():
    """
    Gets the current public IPv4 address of a running Amazon Cloud EC2 instance.
    """

    try:
        # IMDSv2 requires a token
        token_url = "http://169.254.169.254/latest/api/token"
        token_headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
        token_response = requests.put(token_url, headers=token_headers, timeout=2)
        token = token_response.text

        # Retrieve public IP using the token
        ip_url = "http://169.254.169.254/latest/meta-data/public-ipv4"
        ip_headers = {"X-aws-ec2-metadata-token": token}
        ip_response = requests.get(ip_url, headers=ip_headers, timeout=2)
        
        return ip_response.text
    except requests.exceptions.RequestException as e:
        print(f"Error accessing metadata service: {e}")
        return None

public_ip = get_public_ipv4()
if public_ip:
    print(f"The instance's public IP address is: {public_ip}")

