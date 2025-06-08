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

    def get_related_tags(self, tag_query: str = "", limit: int = 50) -> list:
        tags = [t for t in tag_query.strip().split() if t]

        include_tags = [t for t in tags if not t.startswith("-")]
        exclude_tags = [t[1:] for t in tags if t.startswith("-")]

        with self.connect() as conn:
            cursor = conn.cursor()

            if not include_tags and not exclude_tags:
                # sin etiquetas: devolver los tags más comunes
                cursor.execute(f"""
                    SELECT t.id, t.name, t.type, t.source, COUNT(rt.tag_id) as count
                    FROM resource_tags rt
                    JOIN tags t ON t.id = rt.tag_id
                    GROUP BY rt.tag_id
                    ORDER BY count DESC
                    LIMIT ?
                """, (limit,))
                columns = [desc[0] for desc in cursor.description if desc[0] != "count"]
                return [dict(zip(columns, row[:-1])) for row in cursor.fetchall()]

            # obtener ids de etiquetas a incluir
            if include_tags:
                q_marks_inc = ",".join("?" for _ in include_tags)
                cursor.execute(f"SELECT id FROM tags WHERE name IN ({q_marks_inc})", include_tags)
                tag_ids_inc = [row[0] for row in cursor.fetchall()]
            else:
                tag_ids_inc = []

            # obtener ids de etiquetas a excluir
            if exclude_tags:
                q_marks_exc = ",".join("?" for _ in exclude_tags)
                cursor.execute(f"SELECT id FROM tags WHERE name IN ({q_marks_exc})", exclude_tags)
                tag_ids_exc = [row[0] for row in cursor.fetchall()]
            else:
                tag_ids_exc = []

            # buscar recursos que cumplan
            query = """
                SELECT rt.resource_id
                FROM resource_tags rt
                GROUP BY rt.resource_id
            """

            having_clauses = []
            params = []

            if tag_ids_inc:
                query += f"""
                    HAVING SUM(CASE WHEN rt.tag_id IN ({','.join('?' for _ in tag_ids_inc)}) THEN 1 ELSE 0 END) = ?
                """
                params.extend(tag_ids_inc)
                params.append(len(tag_ids_inc))

            if tag_ids_exc:
                query += " AND " if "HAVING" in query else " HAVING "
                query += f"""
                    SUM(CASE WHEN rt.tag_id IN ({','.join('?' for _ in tag_ids_exc)}) THEN 1 ELSE 0 END) = 0
                """
                params.extend(tag_ids_exc)

            cursor.execute(query, params)
            resource_ids = [row[0] for row in cursor.fetchall()]
            if not resource_ids:
                return []

            # buscar etiquetas relacionadas (excluyendo las ya buscadas)
            all_tag_ids = tag_ids_inc + tag_ids_exc
            q_marks_rids = ",".join("?" for _ in resource_ids)
            q_marks_excl = ",".join("?" for _ in all_tag_ids) if all_tag_ids else "NULL"

            cursor.execute(f"""
                SELECT t.id, t.name, t.type, t.source, COUNT(rt.tag_id) as count
                FROM resource_tags rt
                JOIN tags t ON t.id = rt.tag_id
                WHERE rt.resource_id IN ({q_marks_rids})
                {"AND rt.tag_id NOT IN (" + q_marks_excl + ")" if all_tag_ids else ""}
                GROUP BY rt.tag_id
                ORDER BY count DESC
                LIMIT ?
            """, resource_ids + all_tag_ids + [limit] if all_tag_ids else resource_ids + [limit])

            columns = [desc[0] for desc in cursor.description if desc[0] != "count"]
            return [dict(zip(columns, row[:-1])) for row in cursor.fetchall()]