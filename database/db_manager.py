import sqlite3

class DBManager:
    def __init__(self, db_path="data/gallery.db"):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)

    def get_all_previews(self):
        """Devuelve una lista de (preview_path, booru_id)"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT preview_path, booru_id FROM resources")
            return cursor.fetchall()

    def get_all_tags(self):
        """Devuelve una lista de diccionarios con todos los campos de la tabla tags"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, type, source FROM tags")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_previews_by_tags(self, tag_names):
        """
        Devuelve previews que tengan TODOS los tags en tag_names.
        """
        if not tag_names:
            return self.get_all_previews()
        with self.connect() as conn:
            cursor = conn.cursor()
            # Obtener los tag_id de los nombres
            q_marks = ",".join("?" for _ in tag_names)
            cursor.execute(f"SELECT id FROM tags WHERE name IN ({q_marks})", tag_names)
            tag_ids = [row[0] for row in cursor.fetchall()]
            if not tag_ids:
                return []
            # Consulta para obtener los recursos que tengan TODOS los tag_ids
            q_marks = ",".join("?" for _ in tag_ids)
            cursor.execute(f"""
                SELECT r.preview_path, r.booru_id
                FROM resources r
                JOIN resource_tags rt ON r.id = rt.resource_id
                WHERE rt.tag_id IN ({q_marks})
                GROUP BY r.id
                HAVING COUNT(DISTINCT rt.tag_id) = ?
            """, tag_ids + [len(tag_ids)])
            return cursor.fetchall()

    # Puedes agregar más métodos: buscar por id, eliminar, actualizar, etc.

# Uso recomendado en tu código principal:
# from database.db_manager import DBManager
# db = DBManager()
# previews = db.get_all_previews()