import os
import sqlite3
from datetime import datetime
from urllib.parse import urlparse


def e621_save_json(json_data, db_path='data/gallery.db'):
    if not json_data or 'posts' not in json_data:
        print('json inválido o sin posts')
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    for post in json_data['posts']:
        if post.get('flags', {}).get('deleted'):
            continue

        # datos principales
        booru_id = post['id']
        source = 'e621'
        rating_map = {'s': 'safe', 'q': 'questionable', 'e': 'explicit'}
        rating = rating_map.get(post.get('rating', 's'), 'safe')

        # flags
        flags = post.get('flags', {})
        booru_status = 'active'
        for flag, value in flags.items():
            if value:
                booru_status = flag
                break

        # archivo y paths
        file_info = post.get('file', {})
        preview_info = post.get('preview', {})

        file_url = file_info.get('url')
        preview_url = preview_info.get('url')

        file_name = os.path.basename(urlparse(file_url).path) if file_url else None
        preview_name = os.path.basename(urlparse(preview_url).path) if preview_url else None

        file_path = f"downloads/originals/{file_name}" if file_name else None
        preview_path = f"downloads/preview/{preview_name}" if preview_name else None

        ext = file_info.get('ext')
        size = file_info.get('size')
        width = file_info.get('width')
        height = file_info.get('height')
        md5 = file_info.get('md5')
        duration = post.get('duration') or None
        created_at = post.get('created_at')
        downloaded_at = datetime.now().isoformat()
        tags_updated_at = downloaded_at

        # insertar en resources
        cur.execute("""
            INSERT OR IGNORE INTO resources (
                booru_id, source, file_url, preview_url, file_path, 
                preview_path, file_type, size,
                width, height, duration, rating, booru_status, md5,
                created_at, downloaded_at, tags_updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            booru_id, source, file_url, preview_url, file_path, 
            preview_path, ext, size,
            width, height, duration, rating, booru_status, md5,
            created_at, downloaded_at, tags_updated_at
        ))

        # obtener id del recurso
        cur.execute("SELECT id FROM resources WHERE md5 = ?", (md5,))
        resource_row = cur.fetchone()
        if not resource_row:
            continue  # no se insertó ni existe, salta este post

        resource_id = resource_row[0]

        # insertar sources adicionales
        post_sources = post.get('sources', [])
        for s in post_sources:
            cur.execute("""
                INSERT OR IGNORE INTO resource_sources (resource_id, url, source_name)
                VALUES (?, ?, ?)
            """, (resource_id, s, 'e621'))

        # insertar tags y relación
        tags = post.get('tags', {})
        for tag_type, tag_list in tags.items():
            for tag_name in tag_list:
                # insertar tag si no existe
                cur.execute("""
                    INSERT OR IGNORE INTO tags (name, type, source)
                    VALUES (?, ?, ?)
                """, (tag_name, tag_type, source))

                # obtener tag_id
                cur.execute("""
                    SELECT id FROM tags WHERE name = ? AND source = ?
                """, (tag_name, source))
                tag_row = cur.fetchone()
                if tag_row:
                    tag_id = tag_row[0]
                    # insertar relación
                    cur.execute("""
                        INSERT OR IGNORE INTO resource_tags (resource_id, tag_id)
                        VALUES (?, ?)
                    """, (resource_id, tag_id))

    conn.commit()
    conn.close()
