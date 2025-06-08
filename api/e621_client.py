# archivo: api/e621_client.py

import requests

class E621Client:
    BASE_URL = "https://e621.net"
    HEADERS = {
        "User-Agent": "TuApp/1.0 (by YourName or Email)"
    }

    def __init__(self):
        pass

    def fetch_posts(self, tags: list[str], page: int = 1, limit: int = 100) -> list[dict]:
        """
        obtiene una lista de posts desde e621 basado en tags, página y límite
        """
        tag_query = " ".join(tags)
        url = f"{self.BASE_URL}/posts.json"
        params = {
            "tags": tag_query,
            "page": page,
            "limit": limit
        }

        try:
            response = requests.get(url, headers=self.HEADERS, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("posts", [])
        except requests.RequestException as e:
            print(f"Error al obtener posts de e621: {e}")
            return []

    def fetch_tag_predictions(self, partial: str, limit: int = 5) -> list[dict]:
        """
        obtiene sugerencias de tags usando name_matches=partial*
        """
        search_term = f"{partial}*"
        url = f"{self.BASE_URL}/tags.json"
        params = {
            "search[name_matches]": search_term,
            "limit": limit
        }

        try:
            response = requests.get(url, headers=self.HEADERS, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error al obtener sugerencias de tags: {e}")
            return []

    def fetch_exact_tag(self, tag_name: str) -> dict | None:
        """
        obtiene la info de un tag exacto (sin wildcard), útil para obtener el post_count
        """
        url = f"{self.BASE_URL}/tags.json"
        params = {
            "search[name]": tag_name
        }

        try:
            response = requests.get(url, headers=self.HEADERS, params=params)
            response.raise_for_status()
            tags = response.json()
            return tags[0] if tags else None
        except requests.RequestException as e:
            print(f"Error al obtener tag exacto: {e}")
            return None
