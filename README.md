# 🏷️ Tegami

> ⚠️ **Este proyecto está actualmente en desarrollo**  
> Aún no es funcional, pero ya cuenta con una base de interfaz gráfica con vistas de galería en lista e íconos.  
> **No se recomienda su uso fuera de pruebas y desarrollo por ahora.**

---

## 📌 ¿Qué es esto?

**Tegami** es una aplicación de escritorio pensada para organizar, explorar y visualizar imágenes descargadas desde boorus (como *e621*, *rule34*, *Gelbooru*, etc.), permitiendo filtrado por etiquetas y diferentes vistas de galería.

La meta es tener una herramienta liviana, personalizable y útil para artistas, coleccionistas o entusiastas de imágenes etiquetadas.

---

## 🧩 Características planeadas

- 🐾 Organización automática por etiquetas.
- 💾 Gestión de colecciones locales desde carpetas.
- 🔎 Búsqueda avanzada y filtrado por múltiples tags.
- 🖼️ Vistas de galería tipo cuadrícula o lista.
- 🌐 Soporte para múltiples fuentes booru.
- ⚙️ Personalización mediante módulos o "mods".
- 🎮 Minijuegos ocultos (sí, easter eggs 👀).

---

## 🛠️ Estado actual

- [x] Interfaz inicial con PySide6
- [x] Vistas básicas de galería (lista / cuadrícula)
- [x] Panel lateral de etiquetas (dock)
- [x] Barra inferior de estado con botones de vista
- [ ] Descarga de posts vía API
- [ ] Organización y almacenamiento de imágenes
- [ ] Filtrado real por tags
- [ ] Configuración persistente en disco
- [ ] Soporte parcial a múltiples boorus

---

## 🐍 Requisitos (por ahora)

- Python 3.10 o superior
- PySide6 (`pip install PySide6`)
- Conexión a internet para probar consultas a boorus

---

## 🚧 Instalación

Actualmente no hay instalador. Si quieres probar la interfaz:

```bash
git clone https://github.com/FernandLvl/Tegami.git
cd Tegami
python main.py
