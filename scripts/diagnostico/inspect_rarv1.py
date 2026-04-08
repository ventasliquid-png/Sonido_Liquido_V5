from cryptography import x509
from cryptography.hazmat.backends import default_backend

try:
    with open(r"C:\dev\RAR_V1\certs\rarv1.crt", "rb") as f:
        cert_data = f.read()
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        print(f"Issuer: {cert.issuer}")
        print(f"Subject: {cert.subject}")
except Exception as e:
    print(f"Error inspecting cert: {e}")
