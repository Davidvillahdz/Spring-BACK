#!/usr/bin/env python3
"""
Script de Verificación - Práctica 10: Paginación Avanzada con Spring Boot
Objetivo: Validar Page, Slice, Filtros Dinámicos y Ordenamiento
Autor: Adaptado para ICC Fundamentos
"""

import sys
import time
import json

# -----------------------------
# Dependencia obligatoria
# -----------------------------
try:
    import requests
except ImportError:
    print("ERROR: La librería 'requests' no está instalada.")
    print("Ejecute: pip install requests")
    sys.exit(1)

# -----------------------------
# Configuración
# -----------------------------
BASE_URL = "http://localhost:8080/api/products"
SCORE = 0
MAX_SCORE = 10

# -----------------------------
# Utilidades
# -----------------------------
def print_header(title, points):
    print(f"\n{'='*60}")
    print(f"[TEST] {title} ({points} pts)")
    print(f"{'-'*60}")

def add_points(points, message):
    global SCORE
    SCORE += points
    print(f"  ✅ +{points} pts: {message}")

def fail_test(message):
    print(f"  ❌ FALLO: {message}")

def safe_get(url, params=None):
    try:
        response = requests.get(url, params=params)
        return response
    except Exception as e:
        print(f"  [ERROR CONEXIÓN]: {e}")
        return None

# -----------------------------
# PRUEBAS
# -----------------------------

def check_data_availability():
    """Verifica que existan datos para probar"""
    print_header("Verificación Inicial de Datos", 1)
    res = safe_get(BASE_URL, {"size": 1})
    if res and res.status_code == 200:
        data = res.json()
        total = data.get("totalElements", 0)
        print(f"  [INFO] Total de productos encontrados: {total}")
        if total > 5:
            add_points(1, "Dataset suficiente detectado")
            return True
        else:
            fail_test("Se necesitan al menos 5 productos. Ejecuta el seeder.py primero.")
            return False
    fail_test("El servidor no responde o dio error")
    return False

def test_page_structure():
    """Valida la estructura completa de PAGE"""
    print_header("Estructura PAGE (Metadatos Completos)", 2)
    
    # Petición estándar
    res = safe_get(BASE_URL, {"page": 0, "size": 5})
    
    if res and res.status_code == 200:
        data = res.json()
        
        # Validar claves obligatorias de Page
        required_keys = ["content", "totalPages", "totalElements", "size", "number"]
        missing = [k for k in required_keys if k not in data]
        
        if not missing:
            add_points(1, "JSON contiene todos los metadatos de Page")
            
            # Validar contenido
            if len(data["content"]) == 5:
                add_points(1, "Tamaño de página respetado (size=5)")
            else:
                fail_test(f"Se esperaban 5 elementos, llegaron {len(data['content'])}")
        else:
            fail_test(f"Faltan campos de Page: {missing}")
    else:
        fail_test("Error al consultar endpoint PAGE")

def test_slice_structure():
    """Valida la estructura ligera de SLICE"""
    print_header("Estructura SLICE (Rendimiento)", 2)
    
    # Petición al endpoint slice
    res = safe_get(f"{BASE_URL}/slice", {"page": 0, "size": 5})
    
    if res and res.status_code == 200:
        data = res.json()
        
        # Validar que NO tenga metadatos pesados
        forbidden_keys = ["totalElements", "totalPages"]
        present_forbidden = [k for k in forbidden_keys if k in data]
        
        # Validar claves de Slice
        required_keys = ["content", "first", "last"]
        
        if not present_forbidden:
            add_points(1, "Slice NO contiene cálculos de conteo total (Correcto)")
            
            if "hasNext" in data or "last" in data: # A veces Slice json varía ligeramente según versión, pero hasNext es clave
                add_points(1, "Estructura Slice válida")
            else:
                fail_test("No parece un objeto Slice válido")
        else:
            fail_test(f"El endpoint Slice devolvió campos prohibidos (es un Page?): {present_forbidden}")
    else:
        fail_test("Error al consultar endpoint SLICE")

def test_filtering():
    """Valida el buscador con filtros"""
    print_header("Filtros + Paginación (/search)", 2)
    
    # Buscar algo que probablemente exista (generado por seeder)
    # Buscamos "Laptop" que el seeder suele crear
    term = "Laptop"
    res = safe_get(f"{BASE_URL}/search", {"name": term, "page": 0, "size": 10})
    
    if res and res.status_code == 200:
        data = res.json()
        content = data.get("content", [])
        
        if len(content) > 0:
            # Verificar que al menos el primero coincida
            first_item = content[0]
            if term.lower() in first_item["name"].lower():
                add_points(2, f"Filtro por nombre '{term}' funciona correctamente")
            else:
                fail_test(f"El producto '{first_item['name']}' no contiene '{term}'")
        else:
            print("  [WARN] No se encontraron Laptops para validar filtro. (No resta puntos pero verifica tu data)")
            add_points(1, "Endpoint responde 200 OK (sin datos para validar lógica)")
    else:
        fail_test("Error al consultar SEARCH")

def test_sorting():
    """Valida el ordenamiento dinámico"""
    print_header("Ordenamiento (Sort)", 2)
    
    # Ordenar por precio descendente (el más caro primero)
    res = safe_get(BASE_URL, {"sort": "price,desc", "size": 5})
    
    if res and res.status_code == 200:
        data = res.json()
        content = data.get("content", [])
        
        if len(content) >= 2:
            p1 = content[0]["price"]
            p2 = content[1]["price"]
            
            print(f"  [INFO] Precio 1: ${p1} vs Precio 2: ${p2}")
            
            if p1 >= p2:
                add_points(2, "Ordenamiento DESC correcto (Mayor a menor)")
            else:
                fail_test("El ordenamiento falló. El segundo precio es mayor al primero.")
        else:
            fail_test("Insuficientes datos para probar ordenamiento")
    else:
        fail_test("Error al consultar endpoint con SORT")

def test_security():
    print_header("6. Seguridad (Validación)", 1)
    res = safe_get(BASE_URL, {"sort": "password,desc"}) 
    
    # CORRECCIÓN AQUÍ: Usamos "is not None"
    if res is not None and res.status_code in [400, 500]:
        add_points(1, "Bloquea ordenamiento por campos inválidos")
    elif res is not None and res.status_code == 200:
        fail_test("PERMITIÓ ordenar por password (Grave)")
    else:
        # Imprime el código para depurar si falla
        code = res.status_code if res is not None else "None"
        add_points(0.5, f"Respuesta inesperada: {code}")
# -----------------------------
# EJECUCIÓN
# -----------------------------
if __name__ == "__main__":
    print("\nINICIANDO VALIDACIÓN DE PRÁCTICA 10")
    print("Endpoint Base:", BASE_URL)
    
    if check_data_availability():
        test_page_structure()
        test_slice_structure()
        test_filtering()
        test_sorting()
        test_security()
    
    print("\n" + "="*60)
    print("RESULTADO FINAL")
    print("="*60)
    print(f"PUNTUACIÓN: {SCORE} / {MAX_SCORE}")
    
    if SCORE == MAX_SCORE:
        print("🏆 ¡EXCELENTE! Todos los requisitos técnicos están cubiertos.")
    elif SCORE >= 7:
        print("👍 MUY BIEN. Revisa los fallos puntuales.")
    else:
        print("⚠️ NECESITA MEJORAS. Revisa la implementación.")