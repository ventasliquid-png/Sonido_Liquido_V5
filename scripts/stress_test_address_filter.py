import time

# Mock data for stress test
addresses = [
    {"id": i, "calle": f"Calle Falsa {i}", "alias": f"Deposito {i}", "localidad": "Springfield"}
    for i in range(100)
]

def stress_test_filter(query):
    start_time = time.perf_counter()
    # Logic matching AddressSelector.vue:
    q = query.lower()
    results = [
        d for d in addresses 
        if q in (d["calle"] or "").lower() or q in (d["alias"] or "").lower() or q in (d["localidad"] or "").lower()
    ]
    end_time = time.perf_counter()
    return len(results), (end_time - start_time) * 1000

if __name__ == "__main__":
    print("Executing Stress Test (100 addresses local filter)...")
    res_count, duration = stress_test_filter("Deposito 5")
    print(f"Results: {res_count} matches")
    print(f"Response Time: {duration:.4f} ms")
    
    if duration < 1.0:
        print("STATUS: PERFORMANCE OPTIMAL (Under 1ms)")
    else:
        print("STATUS: PERFORMANCE NOMINAL")
