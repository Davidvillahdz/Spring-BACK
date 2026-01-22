import requests
import time
import statistics

BASE_URL = "http://localhost:8080/api/products"

def measure_endpoint(url_suffix, label, iterations=20):
    times = []
    print(f"🔄 Probando {label} ({iterations} veces)...")
    
    for _ in range(iterations):
        start = time.time()
        response = requests.get(f"{BASE_URL}{url_suffix}")
        end = time.time()
        
        if response.status_code == 200:
            times.append((end - start) * 1000) # Convertir a ms
        else:
            print(f"❌ Error {response.status_code}")

    avg_time = statistics.mean(times)
    print(f"   ⏱️ Tiempo Promedio: {avg_time:.2f} ms")
    return avg_time

def run_tests():
    print("🚀 INICIANDO TEST DE RENDIMIENTO - SPRING BOOT PAGINATION")
    print("-" * 50)

    # 1. Prueba de PAGE (Cuenta total + Datos)
    page_time = measure_endpoint("?page=0&size=20", "PAGE (Completo)")

    # 2. Prueba de SLICE (Solo Datos)
    slice_time = measure_endpoint("/slice?page=0&size=20", "SLICE (Ligero)")

    print("-" * 50)
    print("📊 RESULTADOS FINALES:")
    print(f"PAGE:  {page_time:.2f} ms")
    print(f"SLICE: {slice_time:.2f} ms")
    
    diff = page_time - slice_time
    improvement = (diff / page_time) * 100
    
    if slice_time < page_time:
        print(f"✅ SLICE es un {improvement:.1f}% más rápido que PAGE.")
    else:
        print("⚠️ Tiempos similares (el dataset podría ser pequeño aún).")

if __name__ == "__main__":
    run_tests()