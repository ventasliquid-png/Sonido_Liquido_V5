from zeep import Client

URL = "https://fwshomo.afip.gov.ar/wsmtxca/services/MTXCAService?wsdl"

def inspect():
    print(f"Connecting to {URL}...")
    try:
        client = Client(URL)
        print("\n=== SERVICE SIGNATURE ===")
        print(client.service.autorizarComprobante)
        
        print("\n=== TYPES ===")
        # Introspect types if needed
        for type_name in ['ComprobanteType', 'ItemType']:
            try:
                t = client.get_type(f'ns0:{type_name}')
                print(f"\nType {type_name}:")
                print(t.signature())
            except:
                pass

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
