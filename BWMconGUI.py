import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json
import requests
import threading
import time
import sys # ¡Importar sys para PyInstaller!
import random

# --- Configuración para los sonidos ---
SOUND_FILE = 'success_sound.wav'
ERROR_SOUND_FILE = 'error_sound.wav'

# Intentar importar pygame.mixer para sonido multiplataforma
try:
    import pygame.mixer
    PYGAME_MIXER_AVAILABLE = True
except ImportError:
    PYGAME_MIXER_AVAILABLE = False
    print("Advertencia: pygame no está instalado o no se pudo importar. Los sonidos pueden no reproducirse en todos los sistemas operativos.")


class ImageWatermarkerApp:
    def __init__(self, master):
        self.master = master
        master.title("Bulk Watermark Maker")
        
        # Dimensiones de la ventana principal
        window_width = 750
        window_height = 680
        
        # Obtener las dimensiones de la pantalla
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calcular las coordenadas x e y para centrar la ventana
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        master.resizable(False, False)

        # Intento de cargar el icono
        icon_path = None
        # Verificar si el programa se está ejecutando desde un paquete de PyInstaller
        if hasattr(sys, '_MEIPASS'):
            # Si sí, la ruta base es sys._MEIPASS
            icon_path = os.path.join(sys._MEIPASS, 'watermark_icon.ico')
            print(f"DEBUG: Ejecutando desde PyInstaller, buscando icono en: {icon_path}")
        else:
            # Si no (ejecutando desde script Python normal), la ruta base es el directorio actual
            icon_path = 'watermark_icon.ico'
            print(f"DEBUG: Ejecutando como script normal, buscando icono en: {icon_path}")

        if icon_path and os.path.exists(icon_path):
            try:
                master.iconbitmap(icon_path)
                print(f"DEBUG: Icono '{icon_path}' cargado exitosamente para la ventana.")
            except tk.TclError as e:
                print(f"Advertencia: No se pudo cargar el icono '{icon_path}' para la ventana: {e}. Usando el icono predeterminado del sistema.")
        else:
            print(f"Advertencia: Archivo de icono '{icon_path}' no encontrado en la ruta esperada. Usando el icono predeterminado del sistema.")


        # Inicializar pygame mixer si está disponible
        self.mixer_initialized = False
        if PYGAME_MIXER_AVAILABLE:
            try:
                pygame.mixer.init()
                self.mixer_initialized = True
                print("pygame.mixer inicializado correctamente.")
            except pygame.error as e:
                print(f"Advertencia: No se pudo inicializar pygame mixer: {e}. Los sonidos no se reproducirán.")
                self.mixer_initialized = False


        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#e0e0e0")
        style.configure("TLabel", background="#e0e0e0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        style.configure("TEntry", font=("Arial", 10))
        style.configure("TCombobox", font=("Arial", 10))
        style.configure("TLabelframe", background="#e0e0e0")
        style.configure("TLabelframe.Label", background="#e0e0e0", font=("Arial", 10, "bold"))
        style.configure("TRadiobutton", background="#e0e0e0", font=("Arial", 9))


        # Variables de control
        self.input_folder_path = tk.StringVar()
        self.output_folder_path = tk.StringVar()
        self.watermark_text = tk.StringVar(value="")
        self.font_size = tk.IntVar(value=50)
        self.stroke_width = tk.IntVar(value=3)

        # Variables para la posición de la marca de agua
        self.watermark_position = tk.StringVar(value="random")
        self.center_offset_option = tk.StringVar(value="center")
        self.margin_value = tk.IntVar(value=20)
        self.center_offset_px = tk.IntVar(value=100)

        # Variables para la gestión de marcas de agua guardadas
        self.watermark_presets_file = "watermark_presets.json"
        self.watermark_presets = []

        # Variables para guardar las rutas de carpetas y settings de trazo
        self.app_settings_file = "app_settings.json"
        self.load_app_settings()

        # Configuración de la fuente Poppins
        self.font_name = "Poppins-Medium.ttf"
        self.poppins_font_url = "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Medium.ttf"
        self.my_font_path = self.download_font_if_not_exists(self.font_name, self.poppins_font_url, ".")


        self.create_widgets()

        # Cargar los presets después de que los widgets existan
        self.load_watermark_presets()

        # Inicializar el campo de texto de la marca de agua con el primer preset si existe
        if self.watermark_presets:
            self.watermark_combobox.set(self.watermark_presets[0])
            self.watermark_text.set(self.watermark_presets[0])
        else:
            self.watermark_combobox.set('')

        # Configurar el protocolo de cierre para guardar settings al cerrar la ventana
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configurar el estado inicial del combobox de offset central
        self.update_center_offset_combobox_state()

    def download_font_if_not_exists(self, font_name, font_url, download_path="."):
        """
        Descarga un archivo de fuente si no existe.
        """
        font_full_path = os.path.join(download_path, font_name)
        if not os.path.exists(font_full_path):
            print(f"Descargando {font_name} de {font_url}...")
            try:
                response = requests.get(font_url, stream=True)
                response.raise_for_status() # Lanza un error para códigos de estado HTTP malos
                with open(font_full_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Descarga exitosa de {font_name} en {download_path}")
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error de Descarga de Fuente", f"Error al descargar la fuente '{font_name}': {e}. Se usará una fuente predeterminada.")
                return None
        else:
            print(f"La fuente {font_name} ya existe en {download_path}.")
        return font_full_path

    def load_app_settings(self):
        """Carga las rutas de carpetas y el ancho de trazo guardados desde un archivo JSON."""
        if os.path.exists(self.app_settings_file):
            try:
                with open(self.app_settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.input_folder_path.set(settings.get('input_folder', ''))
                    self.output_folder_path.set(settings.get('output_folder', ''))
                    self.stroke_width.set(settings.get('stroke_width', 3))
                    self.watermark_position.set(settings.get('watermark_position', 'random')) 
            except json.JSONDecodeError:
                messagebox.showwarning("Error al cargar settings", "El archivo de configuración está corrupto. Se iniciará con rutas y configuraciones por defecto.")
        # Si no existe el archivo, las variables ya están vacías con sus valores por defecto

    def save_app_settings(self):
        """Guarda las rutas de carpetas y el ancho de trazo en un archivo JSON."""
        settings = {
            'input_folder': self.input_folder_path.get(),
            'output_folder': self.output_folder_path.get(),
            'stroke_width': self.stroke_width.get(),
            'watermark_position': self.watermark_position.get()
        }
        try:
            with open(self.app_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error al guardar settings", f"No se pudieron guardar las rutas y configuraciones: {e}")

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sección de Carpeta de Entrada
        input_frame = ttk.LabelFrame(main_frame, text="Carpeta de Imágenes de Entrada", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Entry(input_frame, textvariable=self.input_folder_path, width=60, state="readonly").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(input_frame, text="Examinar", command=self.browse_input_folder).grid(row=0, column=1, padx=2, pady=5)

        # Sección de Carpeta de Salida
        output_frame = ttk.LabelFrame(main_frame, text="Carpeta de Imágenes de Salida", padding="10")
        output_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Entry(output_frame, textvariable=self.output_folder_path, width=60, state="readonly").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(output_frame, text="Examinar", command=self.browse_output_folder).grid(row=0, column=1, padx=2, pady=5)

        # Sección de Configuración de la Marca de Agua
        watermark_config_frame = ttk.LabelFrame(main_frame, text="Configuración de la Marca de Agua", padding="10")
        watermark_config_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Fila 0: Texto de la Marca
        ttk.Label(watermark_config_frame, text="Texto de la Marca:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.watermark_entry = ttk.Entry(watermark_config_frame, textvariable=self.watermark_text, width=50)
        self.watermark_entry.grid(row=0, column=1, columnspan=5, padx=5, pady=5, sticky="ew")

        # Fila 1: Tamaño de Fuente, Ancho de Trazo, Margen
        ttk.Label(watermark_config_frame, text="Tamaño de Fuente:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Spinbox(watermark_config_frame, from_=10, to_=200, textvariable=self.font_size, width=5).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(watermark_config_frame, text="Ancho de Trazo (px):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Spinbox(watermark_config_frame, from_=0, to_=10, textvariable=self.stroke_width, width=5).grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(watermark_config_frame, text="Margen (px):").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        ttk.Spinbox(watermark_config_frame, from_=0, to_=100, textvariable=self.margin_value, width=5).grid(row=1, column=5, padx=5, pady=5, sticky="w")

        for i in range(6):
            watermark_config_frame.grid_columnconfigure(i, weight=1)


        # Sección de Gestión de Marcas de Agua Guardadas
        presets_frame = ttk.LabelFrame(main_frame, text="Marcas de Agua Guardadas", padding="10")
        presets_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        ttk.Label(presets_frame, text="Seleccionar Marca:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.watermark_combobox = ttk.Combobox(presets_frame,
                                                textvariable=tk.StringVar(),
                                                values=self.watermark_presets,
                                                state="readonly",
                                                width=40)
        self.watermark_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.watermark_combobox.bind("<<ComboboxSelected>>", self.on_preset_selected)

        button_frame = ttk.Frame(presets_frame)
        button_frame.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Guardar Nueva", command=self.save_new_watermark).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Editar", command=self.edit_selected_watermark).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Borrar", command=self.delete_selected_watermark).pack(side=tk.LEFT, padx=2)

        # Sección de Posición de la Marca de Agua
        position_frame = ttk.LabelFrame(main_frame, text="Posición de la Marca de Agua", padding="10")
        position_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        # Radiobuttons para posiciones principales
        ttk.Radiobutton(position_frame, text="Arriba Izquierda", variable=self.watermark_position, value="top_left", command=self.update_center_offset_combobox_state).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Radiobutton(position_frame, text="Arriba Derecha", variable=self.watermark_position, value="top_right", command=self.update_center_offset_combobox_state).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ttk.Radiobutton(position_frame, text="Posición Aleatoria", variable=self.watermark_position, value="random", command=self.update_center_offset_combobox_state).grid(row=0, column=2, padx=5, pady=2, sticky="w")
        
        ttk.Radiobutton(position_frame, text="Abajo Izquierda", variable=self.watermark_position, value="bottom_left", command=self.update_center_offset_combobox_state).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Radiobutton(position_frame, text="Abajo Derecha", variable=self.watermark_position, value="bottom_right", command=self.update_center_offset_combobox_state).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Radiobutton(position_frame, text="Centro", variable=self.watermark_position, value="center_options", command=self.update_center_offset_combobox_state).grid(row=2, column=0, padx=5, pady=2, sticky="w")

        # Combobox para opciones de centro
        self.center_options_combobox = ttk.Combobox(position_frame,
                                                    textvariable=self.center_offset_option,
                                                    values=["center", "center_offset_up", "center_offset_down", "center_offset_left", "center_offset_right"],
                                                    state="disabled",
                                                    width=25)
        self.center_options_combobox.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        
        # Ajuste de padx para acercar "Desplazamiento Centro (px):" a su spinbox
        ttk.Label(position_frame, text="Desplazamiento Centro (px):").grid(row=2, column=2, padx=(10, 2), pady=5, sticky="w")
        self.center_offset_px_spinbox = ttk.Spinbox(position_frame, from_=0, to_=200, textvariable=self.center_offset_px, width=5)
        self.center_offset_px_spinbox.grid(row=2, column=3, padx=(2, 5), pady=5, sticky="w")


        # Botón de Procesar y Etiqueta de Carga (AHORA EN LA MISMA FILA)
        # Ajustamos main_frame para 2 columnas en esta fila
        main_frame.grid_columnconfigure(0, weight=1) # Columna para el botón
        main_frame.grid_columnconfigure(1, weight=1) # Columna para la etiqueta de carga

        process_button = ttk.Button(main_frame, text="Aplicar Marca de Agua", command=self.start_processing_thread)
        process_button.grid(row=5, column=0, pady=20, sticky="e", padx=(0,5))
        
        self.loading_label = ttk.Label(main_frame, text="", font=("Arial", 12, "bold"), foreground="blue")
        self.loading_label.grid(row=5, column=1, pady=20, sticky="w", padx=(5,0))
        self.animation_dots = ["", ".", "..", "..."]
        self.animation_index = 0
        self.loading_animation_active = False

        # Las columnas 0 y 1 del main_frame ya se configuraron arriba para la nueva disposición
        input_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)
        presets_frame.grid_columnconfigure(1, weight=1)
        position_frame.grid_columnconfigure(0, weight=1)
        position_frame.grid_columnconfigure(1, weight=1)
        position_frame.grid_columnconfigure(2, weight=1)
        position_frame.grid_columnconfigure(3, weight=1)


    def update_center_offset_combobox_state(self):
        """Habilita/deshabilita el combobox de opciones de centro y el spinbox de desplazamiento si no es centro o random."""
        current_position = self.watermark_position.get()
        if current_position == "center_options":
            self.center_options_combobox.config(state="readonly")
            self.center_offset_px_spinbox.config(state="normal")
            if not self.center_offset_option.get():
                self.center_offset_option.set("center")
        elif current_position == "random":
            self.center_options_combobox.config(state="disabled")
            self.center_offset_option.set("center")
            self.center_offset_px_spinbox.config(state="disabled")
        else:
            self.center_options_combobox.config(state="disabled")
            self.center_offset_option.set("center")
            self.center_offset_px_spinbox.config(state="disabled")


    def browse_input_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_folder_path.set(folder_selected)

    def browse_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder_path.set(folder_selected)

    def load_watermark_presets(self):
        if os.path.exists(self.watermark_presets_file):
            try:
                with open(self.watermark_presets_file, 'r', encoding='utf-8') as f:
                    self.watermark_presets = json.load(f)
            except json.JSONDecodeError:
                messagebox.showwarning("Error al cargar", "El archivo de presets está corrupto o vacío. Se iniciará con una lista vacía.")
                self.watermark_presets = []
        self.update_combobox_values()

    def save_watermark_presets(self):
        try:
            with open(self.watermark_presets_file, 'w', encoding='utf-8') as f:
                json.dump(self.watermark_presets, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error al guardar", f"No se pudieron guardar los presets: {e}")

    def on_closing(self):
        self.save_watermark_presets()
        self.save_app_settings()
        self.master.destroy()

    def update_combobox_values(self):
        self.watermark_combobox['values'] = self.watermark_presets
        current_selection = self.watermark_combobox.get()
        if current_selection not in self.watermark_presets:
            self.watermark_combobox.set('')
        
        if self.watermark_presets and not self.watermark_combobox.get():
             self.watermark_combobox.set(self.watermark_presets[0])
             self.watermark_text.set(self.watermark_presets[0])

    def on_preset_selected(self, event=None):
        selected_text = self.watermark_combobox.get()
        if selected_text:
            self.watermark_text.set(selected_text)

    def save_new_watermark(self):
        text_to_save = self.watermark_text.get().strip()
        if not text_to_save:
            messagebox.showwarning("Advertencia", "El texto de la marca de agua no puede estar vacío para guardar.")
            return
        if text_to_save not in self.watermark_presets:
            self.watermark_presets.append(text_to_save)
            self.watermark_presets.sort()
            self.update_combobox_values()
            self.watermark_combobox.set(text_to_save)
            messagebox.showinfo("Guardado", f"Marca de agua '{text_to_save}' guardada.")
            self.save_watermark_presets()
        else:
            messagebox.showinfo("Información", "Esta marca de agua ya existe.")

    def edit_selected_watermark(self):
        selected_text = self.watermark_combobox.get()
        new_text = self.watermark_text.get().strip()

        if not selected_text:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una marca de agua para editar.")
            return
        if not new_text:
            messagebox.showwarning("Advertencia", "El nuevo texto no puede estar vacío.")
            return
        if new_text == selected_text:
            messagebox.showinfo("Información", "El texto no ha cambiado.")
            return
        if new_text in self.watermark_presets and new_text != selected_text:
            messagebox.showwarning("Advertencia", "Ya existe una marca de agua con este nuevo texto.")
            return

        try:
            index = self.watermark_presets.index(selected_text)
            self.watermark_presets[index] = new_text
            self.watermark_presets.sort()
            self.update_combobox_values()
            self.watermark_combobox.set(new_text)
            messagebox.showinfo("Edición", f"Marca de agua editada a '{new_text}'.")
            self.save_watermark_presets()
        except ValueError:
            messagebox.showerror("Error", "La marca de agua seleccionada no se encontró en la lista.")

    def delete_selected_watermark(self):
        selected_text = self.watermark_combobox.get()
        if not selected_text:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una marca de agua para borrar.")
            return
        
        if messagebox.askyesno("Confirmar Borrado", f"¿Estás seguro de que quieres borrar '{selected_text}'?"):
            try:
                self.watermark_presets.remove(selected_text)
                self.update_combobox_values()
                self.watermark_text.set("")
                self.watermark_combobox.set('')
                if self.watermark_presets:
                    self.watermark_combobox.set(self.watermark_presets[0])
                    self.watermark_text.set(self.watermark_presets[0])

                messagebox.showinfo("Borrado", f"Marca de agua '{selected_text}' borrada.")
                self.save_watermark_presets()
            except ValueError:
                messagebox.showerror("Error", "La marca de agua seleccionada no se encontró en la lista.")

    def get_font(self, font_size):
        """
        Intenta cargar la fuente Poppins. Si no está disponible localmente, usará la predeterminada.
        """
        # Determina la ruta base para la fuente
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
        font_full_path = os.path.join(base_path, self.font_name)

        if os.path.exists(font_full_path):
            try:
                return ImageFont.truetype(font_full_path, font_size)
            except IOError:
                print(f"Error al cargar la fuente en {font_full_path}. Usando la fuente predeterminada de Pillow.")
                return ImageFont.load_default()
        else:
            print(f"No se encontró la fuente Poppins descargada en {font_full_path}. Usando la fuente predeterminada de Pillow.")
            return ImageFont.load_default()


    def add_watermark_to_image(self, image_path, output_folder, watermark_text, font_size, 
                                water_position, margin, center_offset_value, center_offset_option_selected, 
                                stroke_width):
        """
        Añade una marca de agua de texto a una imagen individual en la posición especificada.
        Aplica la orientación EXIF y guarda la salida como JPG.
        """
        try:
            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img)
                img = img.convert("RGBA")

                draw = ImageDraw.Draw(img)

                font = self.get_font(font_size)

                fill_color = (255, 255, 255, 255) # Blanco opaco
                stroke_color = (0, 0, 0, 255)   # Negro opaco

                bbox = draw.textbbox((0,0), watermark_text, font=font, stroke_width=stroke_width)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                img_width, img_height = img.size
                
                x, y = 0.0, 0.0

                if water_position == "top_left":
                    x = margin
                    y = margin
                elif water_position == "top_right":
                    x = img_width - text_width - margin
                    y = margin
                elif water_position == "bottom_left":
                    x = margin
                    y = img_height - text_height - margin
                elif water_position == "bottom_right":
                    x = img_width - text_width - margin
                    y = img_height - text_height - margin
                elif water_position == "random":
                    effective_max_x = img_width - text_width - margin
                    effective_max_y = img_height - text_height - margin

                    x_min = margin
                    y_min = margin

                    x = random.randint(x_min if x_min <= effective_max_x else 0, effective_max_x if effective_max_x >= 0 else 0)
                    y = random.randint(y_min if y_min <= effective_max_y else 0, effective_max_y if effective_max_y >= 0 else 0)


                elif water_position == "center_options":
                    base_x = (img_width - text_width) / 2
                    base_y = (img_height - text_height) / 2
                    
                    if center_offset_option_selected == "center":
                        x = base_x
                        y = base_y
                    elif center_offset_option_selected == "center_offset_up":
                        x = base_x
                        y = base_y - center_offset_value
                    elif center_offset_option_selected == "center_offset_down":
                        x = base_x
                        y = base_y + center_offset_value
                    elif center_offset_option_selected == "center_offset_left":
                        x = base_x - center_offset_value
                        y = base_y
                    elif center_offset_option_selected == "center_offset_right":
                        x = base_x + center_offset_value
                        y = base_y
                
                x = int(max(0, min(x, img_width - text_width)))
                y = int(max(0, min(y, img_height - text_height)))

                draw.text((x, y), watermark_text, font=font, fill=fill_color,
                          stroke_width=stroke_width, stroke_fill=stroke_color)

                img = img.convert('RGB')
                
                output_filename = os.path.splitext(os.path.basename(image_path))[0] + ".jpg"
                final_output_path = os.path.join(output_folder, output_filename)
                
                img.save(final_output_path, quality=90)
                return True
        except Exception as e:
            print(f"Error al procesar la imagen {image_path}: {e}")
            return False

    def start_processing_thread(self):
        """Inicia el proceso de imágenes en un hilo separado y muestra la animación de carga."""
        input_folder = self.input_folder_path.get()
        output_folder = self.output_folder_path.get()
        watermark_text = self.watermark_text.get()
        font_size = self.font_size.get()
        position = self.watermark_position.get()
        margin = self.margin_value.get()
        stroke_width = self.stroke_width.get()
        
        center_offset_value = self.center_offset_px.get()
        center_offset_option_selected = self.center_offset_option.get()


        if not input_folder:
            messagebox.showerror("Error", "Por favor, selecciona una carpeta de entrada.")
            return
        if not output_folder:
            messagebox.showerror("Error", "Por favor, selecciona una carpeta de salida.")
            return
        if not watermark_text:
            messagebox.showwarning("Advertencia", "El texto de la marca de agua está vacío. Se aplicará una marca de agua vacía.")
            
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Mostrar animación de carga
        self.loading_animation_active = True
        self.animate_loading_dots()

        # Deshabilitar botones mientras se procesa
        for widget in self.master.winfo_children():
            if isinstance(widget, (ttk.Frame)):
                for child_widget in widget.winfo_children():
                    if hasattr(child_widget, 'config') and 'state' in child_widget.config():
                        child_widget.config(state="disabled")
            elif hasattr(widget, 'config') and 'state' in widget.config():
                widget.config(state="disabled")
        
        # Iniciar el procesamiento en un hilo separado
        self.processing_thread = threading.Thread(target=self._process_images_threaded, 
                                                 args=(input_folder, output_folder, watermark_text, font_size,
                                                       position, margin, center_offset_value, center_offset_option_selected,
                                                       stroke_width))
        self.processing_thread.start()

    def animate_loading_dots(self):
        """Actualiza el texto de la animación de carga."""
        if self.loading_animation_active:
            current_dots = self.animation_dots[self.animation_index]
            self.loading_label.config(text=f"Cargando{current_dots}")
            self.animation_index = (self.animation_index + 1) % len(self.animation_dots)
            self.master.after(300, self.animate_loading_dots)

    def _process_images_threaded(self, input_folder, output_folder, watermark_text, font_size, 
                                 position, margin, center_offset_value, center_offset_option_selected, 
                                 stroke_width):
        """Método de procesamiento de imágenes que se ejecuta en un hilo separado."""
        supported_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.jfif', '.webp') 
        processed_count = 0
        skipped_count = 0
        
        # Recopilar todos los archivos en la carpeta de entrada
        all_files_in_input_folder = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]
        
        # Contar solo los archivos compatibles para un conteo más preciso del "total" a procesar
        total_potential_files = 0
        for filename in all_files_in_input_folder:
            if filename.lower().endswith(supported_extensions):
                total_potential_files += 1

        if total_potential_files == 0:
            # Si no hay archivos compatibles, considera esto como un error en sí mismo
            final_message_type = "no_images_processed"
        else:
            for filename in all_files_in_input_folder:
                if filename.lower().endswith(supported_extensions):
                    image_path = os.path.join(input_folder, filename)
                    if self.add_watermark_to_image(image_path, output_folder, watermark_text, font_size,
                                                   position, margin, center_offset_value, center_offset_option_selected,
                                                   stroke_width):
                        processed_count += 1
                    else:
                        skipped_count += 1
                else:
                    # Contabilizar archivos no compatibles también como saltados
                    skipped_count += 1

            # Determinar el estado final para el mensaje y el icono
            if processed_count == total_potential_files and skipped_count == 0:
                final_message_type = "success" # Todas procesadas sin errores
            elif processed_count > 0 and skipped_count > 0:
                final_message_type = "partial_success" # Algunas procesadas, otras no
            elif processed_count == 0 and skipped_count > 0:
                final_message_type = "no_images_processed" # Ninguna procesada, solo errores/incompatibles
            else:
                final_message_type = "unknown_error" # Fallback para cualquier otro caso inesperado
        
        self.master.after(0, self.stop_processing_ui, processed_count, skipped_count, 
                          final_message_type, output_folder)

    def play_sound(self, sound_file):
        """Reproduce un archivo de sonido usando pygame.mixer."""
        if not self.mixer_initialized:
            print(f"Intento de reproducir '{sound_file}', pero pygame mixer no está inicializado.")
            return # No hacer nada si el mezclador no se inicializó

        # Determina la ruta base para los archivos de sonido
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(os.path.abspath(__file__))
        sound_filepath = os.path.join(base_path, sound_file)

        if os.path.exists(sound_filepath):
            try:
                sound = pygame.mixer.Sound(sound_filepath)
                sound.play()
                print(f"Reproduciendo sonido: {sound_file}")
            except pygame.error as e:
                print(f"Error al reproducir el sonido '{sound_file}': {e}")
        else:
            print(f"Advertencia de Sonido: El archivo de sonido '{sound_file}' no se encontró en la ruta: {sound_filepath}.")

    def show_custom_success_message(self, processed_count, skipped_count, output_folder):
        """Muestra un mensaje de éxito personalizado con un check (✔)."""
        top = tk.Toplevel(self.master)
        top.title("Proceso Completado")
        top.transient(self.master)
        top.grab_set()

        screen_width = top.winfo_screenwidth()
        screen_height = top.winfo_screenheight()

        top_width = 480
        top_height = 280 
        
        top_x = (screen_width // 2) - (top_width // 2)
        top_y = (screen_height // 2) - (top_height // 2)
        top.geometry(f'{top_width}x{top_height}+{top_x}+{top_y}')
        top.resizable(False, False)
        top.attributes('-topmost', True)

        frame = ttk.Frame(top, padding="20")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="✔", font=("Arial", 48, "bold"), foreground="green").pack(pady=(0, 5)) 
        
        message = f"Proceso de marca de agua finalizado con éxito.\n\n" \
                  f"Imágenes procesadas: {processed_count}\n" \
                  f"Imágenes saltadas (no compatibles/error): {skipped_count}\n" \
                  f"Revisa la carpeta: {os.path.abspath(output_folder)}"
        
        ttk.Label(frame, text=message, font=("Arial", 10), wraplength=top_width - 40, justify=tk.CENTER).pack(pady=(5, 15))
        
        ttk.Button(frame, text="OK", command=top.destroy).pack(pady=(0,0))
        
        self.master.wait_window(top)

    def show_custom_error_message(self, processed_count, skipped_count, output_folder, main_message):
        """Muestra un mensaje de error personalizado con una 'X'."""
        top = tk.Toplevel(self.master)
        top.title("Error de Procesamiento")
        top.transient(self.master)
        top.grab_set()

        screen_width = top.winfo_screenwidth()
        screen_height = top.winfo_screenheight()

        top_width = 480
        top_height = 280
        
        top_x = (screen_width // 2) - (top_width // 2)
        top_y = (screen_height // 2) - (top_height // 2)
        top.geometry(f'{top_width}x{top_height}+{top_x}+{top_y}')
        top.resizable(False, False)
        top.attributes('-topmost', True)

        frame = ttk.Frame(top, padding="20")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="❌", font=("Arial", 48, "bold"), foreground="red").pack(pady=(0, 5)) 
        
        message = f"{main_message}\n\n" \
                  f"Imágenes procesadas: {processed_count}\n" \
                  f"Imágenes saltadas (no compatibles/error): {skipped_count}\n" \
                  f"Revisa la carpeta: {os.path.abspath(output_folder)}"
        
        ttk.Label(frame, text=message, font=("Arial", 10), wraplength=top_width - 40, justify=tk.CENTER).pack(pady=(5, 15))
        
        ttk.Button(frame, text="OK", command=top.destroy).pack(pady=(0,0))
        
        self.master.wait_window(top)

    def stop_processing_ui(self, processed_count, skipped_count, final_message_type, output_folder):
        """Detiene la animación, muestra el resultado y re-habilita la UI."""
        self.loading_animation_active = False
        self.loading_label.config(text="") # Ocultar la etiqueta de carga

        for widget in self.master.winfo_children():
            if isinstance(widget, (ttk.Frame)):
                for child_widget in widget.winfo_children():
                    if hasattr(child_widget, 'config') and 'state' in child_widget.config():
                        child_widget.config(state="normal")
            elif hasattr(widget, 'config') and 'state' in widget.config():
                widget.config(state="normal")
        
        self.update_center_offset_combobox_state()

        if final_message_type == "success": # Éxito total
            self.play_sound(SOUND_FILE) # Reproducir sonido de éxito
            self.show_custom_success_message(processed_count, skipped_count, output_folder)
        else: # Si hubo errores (parciales o totales)
            main_error_message = ""
            if final_message_type == "partial_success":
                main_error_message = "Algunas imágenes se crearon satisfactoriamente y otras no."
            elif final_message_type == "no_images_processed":
                main_error_message = "No se pudo procesar ninguna imagen."
            else: # Caso de error desconocido o general
                main_error_message = "Se produjo un error inesperado durante el procesamiento."
            
            self.play_sound(ERROR_SOUND_FILE) # Reproducir sonido de error
            self.show_custom_error_message(processed_count, skipped_count, output_folder, main_error_message)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageWatermarkerApp(root)
    root.mainloop()
