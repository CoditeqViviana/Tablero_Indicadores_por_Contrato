# Tablero de Indicadores por Contrato

Tablero web (un solo archivo, sin servidor) para seguir **Facturación, Costo, Truput y Autoconsumo** por contrato de los clientes **Quala, Colombina del Cauca y Noel**.

Todo el procesamiento ocurre en el navegador: subes los tres informes de Odoo y el tablero calcula los indicadores. Los archivos **no se envían a ningún servidor**.

## Archivos

- **`index.html`** — el tablero. Es lo único necesario para publicarlo.
- `render.yaml` — configuración opcional para desplegar en Render.
- `README.md` — este archivo.

> El archivo `Tablero_Indicadores_por_Contrato.html` es idéntico a `index.html` (copia con el nombre original).

## Informes que se cargan en el tablero

1. **Reporte Truput** — Odoo › Truput › Filtro por año 2026
2. **Apunte Contable** — Odoo › Contabilidad › Contabilidad › Apuntes contables › Filtro cuenta 6 › Filtro fecha 2026 › Filtro apunte contable «Autoc» › Selecciono todo › Exporto «Libros IVA E ICA V18 2026»
3. **Traslado** — Odoo › Inventario › Autoconsumo Clientes › Filtro Fecha de Creación: 1-01-2026 a la fecha actual › Aplicar › Descargo

(Esta misma guía está dentro del tablero, en la vista **Guía rápida**.)

---

## Publicar en GitHub Pages

1. Crea una cuenta en https://github.com e inicia sesión.
2. Crea un repositorio nuevo (botón **New**). Ponle un nombre, por ejemplo `tablero-indicadores`, y déjalo **Public**.
3. Sube el archivo `index.html` (botón **Add file › Upload files**, arrastra `index.html` y luego **Commit changes**).
4. Ve a **Settings › Pages**.
5. En **Build and deployment › Source** elige **Deploy from a branch**.
6. En **Branch** elige `main` y la carpeta `/ (root)`, y pulsa **Save**.
7. Espera 1–2 minutos. GitHub mostrará la URL pública, del estilo:
   `https://TU-USUARIO.github.io/tablero-indicadores/`

Cada vez que quieras actualizar el tablero, vuelve a subir el `index.html` nuevo al repositorio.

---

## Publicar en Render

Render sirve el tablero como **Static Site** (sitio estático).

### Opción A — Desde el panel de Render (más sencillo)

1. Sube primero el `index.html` a un repositorio de GitHub (pasos 1–3 de arriba).
2. Entra a https://render.com e inicia sesión (puedes usar tu cuenta de GitHub).
3. **New › Static Site**.
4. Conecta y selecciona tu repositorio.
5. Configura:
   - **Build Command**: déjalo vacío.
   - **Publish Directory**: `.` (un punto).
6. Pulsa **Create Static Site**. En unos minutos tendrás una URL pública del estilo
   `https://tablero-indicadores.onrender.com`.

### Opción B — Con `render.yaml` (Blueprint)

1. Sube al repositorio tanto `index.html` como `render.yaml`.
2. En Render: **New › Blueprint**, selecciona el repositorio y confirma. Render leerá `render.yaml` y creará el sitio automáticamente.

---

## Notas

- El tablero usa internet para cargar la librería de lectura de Excel (SheetJS) y las tipografías. Quien lo abra necesita conexión.
- No requiere base de datos ni backend. Los archivos que subes quedan guardados en el navegador de cada persona (almacenamiento local), así que al reabrir el enlace se ven los últimos datos cargados sin volver a subirlos. Ese guardado es por navegador y por dispositivo (no se comparte entre usuarios). Hay un botón **Borrar datos guardados** junto a los cargadores.
- También se guarda la **fecha y hora de la última actualización**, visible bajo el subtítulo del menú.
- Los datos de **Personal Asignado** y la guía están dentro del propio `index.html`; para cambiarlos se edita ese archivo.
