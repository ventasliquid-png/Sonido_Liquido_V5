import requests
import ssl

URL = "https://fwshomo.afip.gov.ar/wsmtxca/services/MTXCAService?wsdl"

def probe():
    print(f"Probing {URL}...")
    try:
        # Intentar request normal
        resp = requests.get(URL, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Content Sample: {resp.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
        
    print("\nSSL Info:")
    print(ssl.OPENSSL_VERSION)

if __name__ == "__main__":
    probe()
