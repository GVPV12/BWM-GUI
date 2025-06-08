# Bulk Watermark Maker

Una herramienta de escritorio intuitiva y eficiente, diseñada para aplicar marcas de agua de texto a múltiples imágenes simultáneamente. Ideal para fotógrafos, artistas digitales y cualquier persona que necesite proteger o identificar lotes de imágenes de forma rápida y sencilla.

## GUI
![Captura5435345](https://github.com/user-attachments/assets/02a81534-dd5c-4769-af62-066da4f411d1)
## Ejemplo proceso completado
![Capturarewrwrwe](https://github.com/user-attachments/assets/e1e447c4-33ed-4886-a310-b1983ad0b295)
## Output
![20220615_142349-01 (1)](https://github.com/user-attachments/assets/08d2e751-378d-4bdc-87f0-8916bebbcfd3)

## 🚀 Funcionalidades Principales

* **Procesamiento por Lotes:** Aplica marcas de agua a todas las imágenes de una carpeta de entrada y guarda los resultados en una carpeta de salida designada.
* **Marca de Agua de Texto Personalizable:**
    * Define el texto de tu marca de agua.
    * Ajusta el tamaño de la fuente.
    * Controla el ancho del trazo para un efecto delineado.
* **Posicionamiento Flexible:** Elige entre varias opciones de posicionamiento para tu marca de agua:
    * Esquinas (superior izquierda, superior derecha, inferior izquierda, inferior derecha).
    * Centro, con opciones de desplazamiento para ajuste fino.
    * **Posición Aleatoria:** Coloca la marca de agua en una ubicación aleatoria dentro de la imagen, útil para evitar que los algoritmos de eliminación de marcas de agua detecten patrones.
* **Gestión de Presets:** Guarda tus marcas de agua de texto favoritas como presets para reutilizarlas fácilmente. Puedes guardar nuevas, editarlas o eliminarlas.
* **Soporte de Formato Amplio:** Compatible con una gran variedad de formatos de imagen de entrada.
* **Feedback Visual y Auditivo:** Animación de carga, mensajes claros de éxito o error, y sonidos distintivos para cada resultado del proceso (requiere `pygame` instalado).
* **Interfaz Gráfica Sencilla (GUI):** Desarrollado con Tkinter para una experiencia de usuario amigable.
* **Portable:** Se puede empaquetar para ejecutar sin necesidad de instalar Python ni dependencias en la máquina del usuario (usando PyInstaller).

## 🖼️ Formatos de Imagen Soportados

El programa es compatible con los siguientes formatos de imagen de entrada:

* `.png`
* `.jpg`
* `.jpeg`
* `.bmp`
* `.gif`
* `.tiff`
* `.jfif`
* `.webp`

Todas las imágenes procesadas se guardarán en formato `.jpg` en la carpeta de salida.

## ⚙️ Cómo Usar (Instrucciones para Usuarios)

1.  **Selecciona la Carpeta de Entrada:** Haz clic en "Examinar" junto a "Carpeta de Imágenes de Entrada" para elegir la carpeta que contiene las imágenes a las que deseas añadir marcas de agua.
2.  **Selecciona la Carpeta de Salida:** Haz clic en "Examinar" junto a "Carpeta de Imágenes de Salida" para elegir (o crear) la carpeta donde se guardarán las imágenes con marca de agua.
3.  **Configura la Marca de Agua:**
    * Introduce el "Texto de la Marca".
    * Ajusta el "Tamaño de Fuente" y el "Ancho de Trazo (px)".
    * Selecciona la "Posición de la Marca de Agua" (esquina, centro, o aleatoria) y ajusta el "Margen (px)" o "Desplazamiento Centro (px)" si aplica.
4.  **Gestiona Presets (Opcional):**
    * Para guardar tu configuración de marca de agua actual, haz clic en "Guardar Nueva".
    * Para cargar una marca de agua guardada, selecciónala del menú desplegable "Seleccionar Marca".
    * Puedes "Editar" o "Borrar" presets existentes.
5.  **Aplica la Marca de Agua:** Haz clic en el botón "Aplicar Marca de Agua". Verás un indicador de "Cargando..." y al finalizar, un mensaje de estado con sonido y una 'X' roja (si hubo errores) o simplemente un mensaje de éxito (si todo fue bien).

---

¡Espero que disfrutes usando Bulk Watermark Maker!


---

# ENG

# Bulk Watermark Maker

An intuitive and efficient desktop tool designed to apply text watermarks to multiple images simultaneously. Ideal for photographers, digital artists, and anyone needing to quickly and easily protect or identify batches of images.

## GUI
![Captura5435345](https://github.com/user-attachments/assets/02a81534-dd5c-4769-af62-066da4f411d1)
## Example of a successful process
![Capturarewrwrwe](https://github.com/user-attachments/assets/e1e447c4-33ed-4886-a310-b1983ad0b295)
## Output
![20220615_142349-01 (1)](https://github.com/user-attachments/assets/08d2e751-378d-4bdc-87f0-8916bebbcfd3)

## 🚀 Key Features

* **Batch Processing:** Apply watermarks to all images in an input folder and save the results to a designated output folder.
* **Customizable Text Watermark:**
    * Define your watermark text.
    * Adjust font size.
    * Control stroke width for an outlined effect.
* **Flexible Positioning:** Choose from various positioning options for your watermark:
    * Corners (top-left, top-right, bottom-left, bottom-right).
    * Center, with offset options for fine-tuning.
    * **Random Position:** Place the watermark in a random location within the image, useful for preventing watermark removal algorithms from detecting patterns.
* **Preset Management:** Save your favorite watermark texts as presets for easy reuse. You can save new ones, edit, or delete existing ones.
* **Broad Format Support:** Compatible with a wide variety of input image formats.
* **Visual and Auditory Feedback:** Loading animation, clear success or error messages, and distinct sounds for each process outcome (requires `pygame` installed).
* **Simple Graphical User Interface (GUI):** Developed with Tkinter for a user-friendly experience.
* **Portable:** Can be packaged to run without needing Python or dependencies installed on the user's machine (using PyInstaller).

## 🖼️ Supported Image Formats

The program supports the following input image formats:

* `.png`
* `.jpg`
* `.jpeg`
* `.bmp`
* `.gif`
* `.tiff`
* `.jfif`
* `.webp`

All processed images will be saved in `.jpg` format in the output folder.

## ⚙️ How to Use (User Instructions)

1.  **Select Input Folder:** Click "Browse" next to "Input Images Folder" to choose the folder containing the images you want to watermark.
2.  **Select Output Folder:** Click "Browse" next to "Output Images Folder" to choose (or create) the folder where the watermarked images will be saved.
3.  **Configure Watermark:**
    * Enter the "Watermark Text".
    * Adjust "Font Size" and "Stroke Width (px)".
    * Select "Watermark Position" (corner, center, or random) and adjust "Margin (px)" or "Center Offset (px)" if applicable.
4.  **Manage Presets (Optional):**
    * To save your current watermark settings, click "Save New".
    * To load a saved watermark, select it from the "Select Watermark" dropdown menu.
    * You can "Edit" or "Delete" existing presets.
5.  **Apply Watermark:** Click the "Apply Watermark" button. You will see a "Loading..." indicator, and upon completion, a status message with sound and a red 'X' (if there were errors) or simply a success message (if all went well).

---

I hope you enjoy using Bulk Watermark Maker!
