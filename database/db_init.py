# database/db_init.py

import sqlite3
import os

# ruta del archivo de base de datos
DB_PATH = os.path.join("data", "gallery.db")

# crea la carpeta data si no existe
os.makedirs("data", exist_ok=True)

# conecta a la base de datos (se crea si no existe)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# activa las claves foráneas
cursor.execute("PRAGMA foreign_keys = ON")

# crea la tabla resources
cursor.execute("""
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY,
    booru_id INTEGER,
    source TEXT NOT NULL,
    file_path TEXT NOT NULL,
    preview_path TEXT,
    file_type TEXT NOT NULL,
    size INTEGER,
    width INTEGER,
    height INTEGER,
    duration REAL,
    rating TEXT,
    booru_status TEXT,
    md5 TEXT UNIQUE,
    created_at TEXT,
    downloaded_at TEXT NOT NULL,
    tags_updated_at TEXT
)
""")

# crea la tabla resource_sources
cursor.execute("""
CREATE TABLE IF NOT EXISTS resource_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    source_name TEXT,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
)
""")

# crea la tabla resource_meta
cursor.execute("""
CREATE TABLE IF NOT EXISTS resource_meta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL UNIQUE,
    is_favorite BOOLEAN DEFAULT 0,
    is_hidden BOOLEAN DEFAULT 0,
    user_rating INTEGER,
    notes TEXT,
    view_count INTEGER DEFAULT 0,
    last_viewed TEXT,
    pinned BOOLEAN DEFAULT 0,
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
)
""")

# crea la tabla user_collections
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# crea la tabla resource_collections
cursor.execute("""
CREATE TABLE IF NOT EXISTS resource_collections (
    resource_id INTEGER NOT NULL,
    collection_id INTEGER NOT NULL,
    PRIMARY KEY (resource_id, collection_id),
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (collection_id) REFERENCES user_collections(id) ON DELETE CASCADE
)
""")

# crea la tabla shared_collections
cursor.execute("""
CREATE TABLE IF NOT EXISTS shared_collections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# crea la tabla shared_collection_items
cursor.execute("""
CREATE TABLE IF NOT EXISTS shared_collection_items (
    collection_id INTEGER NOT NULL,
    booru_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    PRIMARY KEY (collection_id, booru_id, source),
    FOREIGN KEY (collection_id) REFERENCES shared_collections(id) ON DELETE CASCADE
)
""")

# crea la tabla tags
cursor.execute("""
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'general',
    source TEXT NOT NULL,
    UNIQUE(name, source)
)
""")

# crea la tabla resource_tags
cursor.execute("""
CREATE TABLE IF NOT EXISTS resource_tags (
    resource_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (resource_id, tag_id),
    FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
)
""")

conn.commit()
conn.close()

print("✓ Base de datos inicializada correctamente.")
