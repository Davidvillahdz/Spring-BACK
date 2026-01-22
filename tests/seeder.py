import psycopg2
import random
from faker import Faker
from datetime import datetime, timedelta

# CONFIGURACIÓN DE TU BASE DE DATOS
DB_CONFIG = {
    "dbname": "devdb",
    "user": "ups",
    "password": "ups123",
    "host": "localhost",
    "port": "5432"
}

fake = Faker('es_ES') # Datos en español

def connect():
    return psycopg2.connect(**DB_CONFIG)

def seed_data():
    conn = connect()
    cur = conn.cursor()
    
    print("🧹 Limpiando datos (TRUNCATE)...")
    # Usamos TRUNCATE ahora que las tablas existen y son correctas
    cur.execute("TRUNCATE TABLE product_categories, products, categories, users RESTART IDENTITY CASCADE;")
    
    print("👤 Creando 5 Usuarios...")
    user_ids = []
    for _ in range(5):
        name = fake.name()
        email = fake.email()
        cur.execute(
            "INSERT INTO users (name, email, password, created_at, updated_at, deleted) VALUES (%s, %s, '123', NOW(), NOW(), false) RETURNING id;",
            (name, email)
        )
        user_ids.append(cur.fetchone()[0])

    print("🏷️ Creando 10 Categorías...")
    cat_ids = []
    categories = ['Laptops', 'Smartphones', 'Audio', 'Video', 'Gaming', 'Oficina', 'Hogar', 'Software', 'Periféricos', 'Tablets']
    for cat in categories:
        cur.execute(
            "INSERT INTO categories (name, description, created_at, updated_at, deleted) VALUES (%s, %s, NOW(), NOW(), false) RETURNING id;",
            (cat, fake.sentence())
        )
        cat_ids.append(cur.fetchone()[0])

    print("📦 Generando 1000 Productos (esto tomará unos segundos)...")
    
    adjetivos = ['Pro', 'Ultra', 'Gaming', 'Slim', 'Max', 'Lite', 'X', '2024']
    tipos = ['Laptop', 'Mouse', 'Monitor', 'Teclado', 'Auriculares', 'Cámara', 'Tablet']
    
    for i in range(1000):
        name = f"{random.choice(tipos)} {fake.word().capitalize()} {random.choice(adjetivos)}"
        price = round(random.uniform(10.0, 5000.0), 2)
        owner_id = random.choice(user_ids)
        
        created_at = datetime.now() - timedelta(days=random.randint(0, 365))
        
        # CORRECCIÓN: Se eliminó el campo 'stock' de aquí abajo
        cur.execute(
            """INSERT INTO products (name, description, price, user_id, created_at, updated_at, deleted) 
               VALUES (%s, %s, %s, %s, %s, %s, false) RETURNING id;""",
            (name, fake.text(max_nb_chars=100), price, owner_id, created_at, created_at)
        )
        product_id = cur.fetchone()[0]

        selected_cats = random.sample(cat_ids, 2)
        for cat_id in selected_cats:
            cur.execute("INSERT INTO product_categories (product_id, category_id) VALUES (%s, %s);", (product_id, cat_id))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ ¡Carga masiva completada con éxito!")

if __name__ == "__main__":
    seed_data()