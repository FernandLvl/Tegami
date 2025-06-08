import os
import requests
from urllib.parse import urlparse

class ResourceDownloader:
    def download(self, url: str, folder: str) -> str | None:
        try:
            os.makedirs(folder, exist_ok=True)

            # obtener el nombre del archivo desde la url
            filename = os.path.basename(urlparse(url).path)
            full_path = os.path.join(folder, filename)

            # omitir descarga si ya existe
            if os.path.exists(full_path):
                return full_path

            # descargar el archivo
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()

            with open(full_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return full_path
        except Exception as e:
            print(f"error al descargar {url}: {e}")
            return None
