import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from bioblend.galaxy import GalaxyInstance
import os
import threading
from PIL import Image, ImageTk
import base64
from io import BytesIO


# ===== CONFIGURACIÓN POR DEFECTO =====
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/")

class GalaxyDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Galaxy Downloader")
        self.root.geometry("1280x720")
        self.root.resizable(True, True)
        self.root.configure(bg="#f5f7fa")
        
        logo_b64 = """
iVBORw0KGgoAAAANSUhEUgAAAkEAAACoCAYAAADn0DrOAAAABGdBTUEAALGPC/xhBQAAACBjSFJN
AAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAbmVYSWZNTQAqAAAACAADARIA
AwAAAAEAAQAAATEAAgAAABEAAAAyh2kABAAAAAEAAABEAAAAAEFkb2JlIEltYWdlUmVhZHkAAAAD
oAEAAwAAAAEAAQAAoAIABAAAAAEAAAJBoAMABAAAAAEAAACoAAAAAGNdZiIAAAKkaVRYdFhNTDpj
b20uYWRvYmUueG1wAAAAAAA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4Onht
cHRrPSJYTVAgQ29yZSA1LjQuMCI+CiAgIDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53
My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+CiAgICAgIDxyZGY6RGVzY3JpcHRpb24g
cmRmOmFib3V0PSIiCiAgICAgICAgICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20v
dGlmZi8xLjAvIgogICAgICAgICAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4
aWYvMS4wLyIKICAgICAgICAgICAgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8x
LjAvIj4KICAgICAgICAgPHRpZmY6T3JpZW50YXRpb24+MTwvdGlmZjpPcmllbnRhdGlvbj4KICAg
ICAgICAgPGV4aWY6Q29sb3JTcGFjZT4xPC9leGlmOkNvbG9yU3BhY2U+CiAgICAgICAgIDxleGlm
OlBpeGVsWERpbWVuc2lvbj42MjI8L2V4aWY6UGl4ZWxYRGltZW5zaW9uPgogICAgICAgICA8ZXhp
ZjpQaXhlbFlEaW1lbnNpb24+MjE0PC9leGlmOlBpeGVsWURpbWVuc2lvbj4KICAgICAgICAgPHht
cDpDcmVhdG9yVG9vbD5BZG9iZSBJbWFnZVJlYWR5PC94bXA6Q3JlYXRvclRvb2w+CiAgICAgIDwv
cmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgo/JOxmAAAlNUlEQVR4
Ae2d8XXbxtLFY5/8/7GDIBU8pgKvKzBTgeEKTFdguALLFYiuQEwFRCowXwXCq8BMBf7uVbDyaLQA
AZIgQfLOOWPMzM7Ozv4ACWtKcX75RSICIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiAC
IiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiAC
IiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiAC
IiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiACIiAC
IiACIiACItCXwAtMmECnfScqXwRaCKwxtmkZ15AIiIAIiIAInJzAr+iAB6DVyTtRA5dE4DU2U17S
hrQXERABERCByyPw8vK2pB2JgAiIgAiIgAiIwHYCOgRtZ6QMERABERABERCBCySgQ9AF3lRtSQRE
QAREQAREYDsB/k5QSvgL0xIR6ErgR9dE5YmACIiACIjAWAjok6Cx3An1IQIiIAIiIAIicFQCOgQd
FbcWEwEREAEREAERGAsBHYLGcifUhwiIgAiIgAiIwFEJ6BB0VNxaTAREQAREQAREYCwEdAgay51Q
HyIgAiIgAiIgAkcloEPQUXFrMREQAREQAREQgbEQ0CFoLHdCfYiACIiACIiACByVgA5BR8WtxURA
BERABERABMZCQIegsdwJ9SECIiACIiACInBUAjoEHRW3FhMBERABERABERgLAR2CxnIn1IcIiIAI
iIAIiMBRCegQdFTcWkwEREAEREAERGAsBHQIGsudUB8iIAIiIAIiIAJHJaBD0FFxazEREAEREAER
EIGxENAhaCx3Qn2IgAiIgAiIgAgclYAOQUfFrcVEQAREQAREQATGQmBsh6AcYH4MoPMOwL+7de87
zNk1pXBr7bvnIXvddY+aJwIiIAIiIAKjJjC2Q1A2EK1Jh7o+Z6he2MqrDv30Scn6JCtXBERABERA
BETgl1/GdgjSPREBERABERABERCBoxDQIegomLWICIiACIiACIjA2Aj8OraGEv1UiFH3kfU+kweY
+2VLzZAY5x42iThDY9tfQ5sKi4AIiIAIiMC4CAS0438x91QdFoleGDuGeAb0TyWpXsKpmumwru93
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
AzbYq1XXidXgAAAAAElFTkSuQmCC        """
        logo_data = base64.b64decode(logo_b64)
        logo_img = Image.open(BytesIO(logo_data))
        logo_img = logo_img.resize((500, 150), Image.LANCZOS)
        self.logo_tk = ImageTk.PhotoImage(logo_img)
 
        header_frame = tk.Frame(root, bg="#f5f7fa")
        header_frame.pack(pady=(25, 25))

        self.gi = None
        self.histories = []
        self.selected_histories = []
        self.output_dir = DEFAULT_OUTPUT_DIR
        # Logo
        logo_label = tk.Label(header_frame, image=self.logo_tk, bg="#f5f7fa")
        logo_label.pack(side="left", padx=(10, 20))
        
        # Título principal
        title_label = tk.Label(
            header_frame,
            text="Galaxy Downloader",
            font=("Times", 35, "bold"),
            fg="#2c3e50",
            bg="#f5f7fa"
        )
        title_label.pack(side="left")

        # Estilos
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TLabel', font=('Times', 9), background="#f5f7fa")
        style.configure('TButton', font=('Times', 9), background="#4a90e2", foreground="white")
        style.map('TButton',
            foreground=[('pressed', 'black'), ('active', 'white')],
            background=[('pressed', '#357ABD'), ('active', '#357ABD')]
        )
        style.configure('TEntry', font=('Arial', 11))
        style.configure('TLabelFrame', background="#f5f7fa", font=('Segoe UI Semibold', 12))

        
        # Mensaje inicial
        self.info_label = ttk.Label(root, text=(
            "⚠️ Asegúrate de tener instalado 'bioblend' en el entorno donde ejecutes esta aplicación.\n"
            "Puedes instalarlo con: pip install bioblend\n"
            "Ejecuta esta app en ese entorno para que funcione correctamente."
        ), foreground='#d9534f', justify='center', background="#f5f7fa", wraplength=580)
        self.info_label.pack(padx=15, pady=12)

        # Frame conexión
        frame_conn = ttk.LabelFrame(root, text="Conexión a Galaxy")
        frame_conn.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Label(frame_conn, text="URL del servidor utilizado:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.url_entry = ttk.Entry(frame_conn, width=48)
        self.url_entry.insert(0, "")    
        self.url_entry.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(frame_conn, text="API Key:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.api_entry = ttk.Entry(frame_conn, width=48, show="*")
        self.api_entry.grid(row=1, column=1, padx=8, pady=6)

        self.connect_btn = ttk.Button(frame_conn, text="Conectar", command=self.connect_galaxy)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=12, ipadx=10)

        # Frame filtro
        frame_filter = ttk.LabelFrame(root, text="Filtro de búsqueda")
        frame_filter.pack(fill="x", padx=20, pady=10)

        ttk.Label(frame_filter, text="Texto a buscar (ej. 'checkv completeness'):").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.filter_entry = ttk.Entry(frame_filter, width=54)
        self.filter_entry.grid(row=0, column=1, padx=8, pady=8)

        # Frame output dir
        frame_output = ttk.LabelFrame(root, text="Carpeta de salida")
        frame_output.pack(fill="x", padx=20, pady=10)

        self.output_dir_label = ttk.Label(frame_output, text=self.output_dir, font=('Segoe UI', 10, 'italic'), foreground='#31708f')
        self.output_dir_label.pack(side="left", padx=10, pady=8, fill="x", expand=True)

        self.select_output_btn = ttk.Button(frame_output, text="Seleccionar carpeta...", command=self.select_output_dir)
        self.select_output_btn.pack(side="right", padx=10, pady=8, ipadx=6)

        # Frame lista historias
        self.frame_histories = ttk.LabelFrame(root, text="Historias")
        self.frame_histories.pack(fill="both", expand=True, padx=20, pady=12)

        self.histories_listbox = tk.Listbox(self.frame_histories, selectmode="extended", font=('Segoe UI', 11), bg="white", bd=1, relief="solid", highlightthickness=0)
        self.histories_listbox.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)

        scrollbar = ttk.Scrollbar(self.frame_histories, orient="vertical", command=self.histories_listbox.yview)
        scrollbar.pack(side="right", fill="y", padx=(0,8), pady=8)
        self.histories_listbox.config(yscrollcommand=scrollbar.set)

        # Botones acción
        frame_actions = ttk.Frame(root, style='TFrame')
        frame_actions.pack(fill="x", padx=20, pady=10)

        self.download_selected_btn = ttk.Button(frame_actions, text="Descargar seleccionadas", command=self.start_download)
        self.download_selected_btn.pack(side="left", padx=15, ipadx=8)

        self.download_all_btn = ttk.Button(frame_actions, text="Descargar todas", command=self.download_all)
        self.download_all_btn.pack(side="left", padx=15, ipadx=8)

        # Barra de estado
        self.status = tk.StringVar()
        self.status.set("Esperando conexión...")
        self.status_label = ttk.Label(root, textvariable=self.status, relief="sunken", anchor="w", background="#e9ecef", font=('Segoe UI', 10))
        self.status_label.pack(fill="x", padx=20, pady=(0,12), ipady=5)

    # ===== Funciones =====
    def select_output_dir(self):
        selected_dir = filedialog.askdirectory(initialdir=self.output_dir, title="Selecciona carpeta de salida")
        if selected_dir:
            self.output_dir = selected_dir
            self.output_dir_label.config(text=self.output_dir)

    def connect_galaxy(self):
        url = self.url_entry.get().strip()
        api_key = self.api_entry.get().strip()
        if not url or not api_key:
            messagebox.showwarning("Campos vacíos", "Por favor ingresa la URL y la API Key.")
            return
        self.status.set("Conectando a Galaxy...")
        self.connect_btn.config(state="disabled")
        try:
            self.gi = GalaxyInstance(url=url, key=api_key)
            self.histories = self.gi.histories.get_histories()
            self.histories_listbox.delete(0, tk.END)
            for hist in self.histories:
                self.histories_listbox.insert(tk.END, hist['name'])
            self.status.set(f"Conectado. {len(self.histories)} historias encontradas.")
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a Galaxy:\n{e}")
            self.status.set("Error en la conexión.")
        finally:
            self.connect_btn.config(state="normal")

    def start_download(self):
        selected_indices = self.histories_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Advertencia", "Selecciona al menos una historia para descargar.")
            return
        self.selected_histories = [self.histories[i] for i in selected_indices]
        self._start_threaded_download()

    def download_all(self):
        if not self.histories:
            messagebox.showwarning("Advertencia", "No hay historias cargadas para descargar.")
            return
        self.selected_histories = self.histories
        self._start_threaded_download()

    def _start_threaded_download(self):
        self.download_selected_btn.config(state="disabled")
        self.download_all_btn.config(state="disabled")
        threading.Thread(target=self.download_files, daemon=True).start()

    def download_files(self):
        search_filter = self.filter_entry.get().strip().lower()
        if not search_filter:
            self.root.after(0, lambda: messagebox.showwarning("Advertencia", "Escribe un filtro de búsqueda antes de descargar."))
            self._enable_buttons()
            return

        os.makedirs(self.output_dir, exist_ok=True)
        self.status.set("Iniciando descarga...")

        try:
            for hist in self.selected_histories:
                hist_name = hist['name'].replace(" ", "_")
                hist_dir = os.path.join(self.output_dir, hist_name)
                os.makedirs(hist_dir, exist_ok=True)

                datasets = self.gi.histories.show_history(hist['id'], contents=True)
                for ds in datasets:
                    if search_filter in ds['name'].lower():
                        try:
                            details = self.gi.datasets.show_dataset(ds['id'])
                            state = details.get("state", "unknown")
                            if state != "ok":
                                self.status.set(f"⏭️ Saltando {ds['name']} (estado: {state})")
                                continue

                            ext = details.get('file_ext', 'dat')
                            filename = f"{ds['name'].replace(' ', '_')}.{ext}"
                            file_path = os.path.join(hist_dir, filename)

                            self.status.set(f"⬇️ Descargando: {ds['name']} (Historia: {hist_name})")
                            self.gi.datasets.download_dataset(
                                ds['id'], 
                                file_path=file_path, 
                                use_default_filename=False
                            )
                        except Exception as e:
                            self.status.set(f"⚠️ Error en {ds['name']}: {e}")
                            continue
            self.status.set("✅ Descarga completada.")
            self.root.after(0, lambda: messagebox.showinfo("Finalizado", "Proceso completado. Archivos con error fueron saltados."))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Se produjo un error durante la descarga:\n{e}"))
            self.status.set("Error durante la descarga.")
        finally:
            self.selected_histories = []
            self._enable_buttons()

    def _enable_buttons(self):
        self.download_selected_btn.config(state="normal")
        self.download_all_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = GalaxyDownloaderApp(root)
    root.mainloop()
