import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from bioblend.galaxy import GalaxyInstance
import os
import threading

DEFAULT_OUTPUT_DIR = os.path.expanduser("~/")

class GalaxyDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Galaxy downloader")
        self.root.geometry("1280x720")
        self.root.resizable(True, True)
        self.root.configure(bg="#f5f7fa")  

        self.gi = None
        self.histories = []
        self.selected_histories = []
        self.output_dir = DEFAULT_OUTPUT_DIR

        # Style
        style = ttk.Style(root)
        style.theme_use('clam')

        # Colors and fonts 
        style.configure('TLabel', font=('Segoe UI', 9), background="#f5f7fa")
        style.configure('TButton', font=('Segoe UI Semibold', 9), background="#4a90e2", foreground="white")
        style.map('TButton',
            foreground=[('pressed', 'white'), ('active', 'white')],
            background=[('pressed', '#357ABD'), ('active', '#357ABD')]
        )
        style.configure('TEntry', font=('Segoe UI', 11))
        style.configure('TLabelFrame', background="#f5f7fa", font=('Segoe UI Semibold', 12))

        self.info_label = ttk.Label(root, text=(
            "⚠️ Make sure you have alredy installed 'bioblend' in the environment you are running this tool.\n"
            "You can install it with: pip install bioblend\n"
        ), foreground='#d9534f', justify='center', background="#f5f7fa", wraplength=580)
        self.info_label.pack(padx=15, pady=12)

        frame_conn = ttk.LabelFrame(root, text="Galaxy conecction")
        frame_conn.pack(fill="x", padx=20, pady=(0, 10))

        ttk.Label(frame_conn, text="URL of the galaxy server you are using:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.url_entry = ttk.Entry(frame_conn, width=48)
        self.url_entry.insert(0, "")    
        self.url_entry.grid(row=0, column=1, padx=8, pady=6)

        ttk.Label(frame_conn, text="your API Key:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.api_entry = ttk.Entry(frame_conn, width=48, show="*")
        self.api_entry.grid(row=1, column=1, padx=8, pady=6)

        self.connect_btn = ttk.Button(frame_conn, text="Connect", command=self.connect_galaxy)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=12, ipadx=10)

        frame_filter = ttk.LabelFrame(root, text="Search filter")
        frame_filter.pack(fill="x", padx=20, pady=10)

        ttk.Label(frame_filter, text="Text to search for e.g checkV:").grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self.filter_entry = ttk.Entry(frame_filter, width=54)
        self.filter_entry.grid(row=0, column=1, padx=8, pady=8)

        frame_output = ttk.LabelFrame(root, text="Output route")
        frame_output.pack(fill="x", padx=20, pady=10)

        self.output_dir_label = ttk.Label(frame_output, text=self.output_dir, font=('Segoe UI', 10, 'italic'), foreground='#31708f')
        self.output_dir_label.pack(side="left", padx=10, pady=8, fill="x", expand=True)

        self.select_output_btn = ttk.Button(frame_output, text="Select folder...", command=self.select_output_dir)
        self.select_output_btn.pack(side="right", padx=10, pady=8, ipadx=6)

        self.frame_histories = ttk.LabelFrame(root, text="Histories")
        self.frame_histories.pack(fill="both", expand=True, padx=20, pady=12)

        self.histories_listbox = tk.Listbox(self.frame_histories, selectmode="extended", font=('Segoe UI', 11), bg="white", bd=1, relief="solid", highlightthickness=0)
        self.histories_listbox.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)

        scrollbar = ttk.Scrollbar(self.frame_histories, orient="vertical", command=self.histories_listbox.yview)
        scrollbar.pack(side="right", fill="y", padx=(0,8), pady=8)
        self.histories_listbox.config(yscrollcommand=scrollbar.set)

        frame_actions = ttk.Frame(root, style='TFrame')
        frame_actions.pack(fill="x", padx=20, pady=10)

        self.download_selected_btn = ttk.Button(frame_actions, text="Download selected", command=self.start_download)
        self.download_selected_btn.pack(side="left", padx=15, ipadx=8)

        self.download_all_btn = ttk.Button(frame_actions, text="Download all", command=self.download_all)
        self.download_all_btn.pack(side="left", padx=15, ipadx=8)

        self.status = tk.StringVar()
        self.status.set("Waiting for connection...")
        self.status_label = ttk.Label(root, textvariable=self.status, relief="sunken", anchor="w", background="#e9ecef", font=('Segoe UI', 10))
        self.status_label.pack(fill="x", padx=20, pady=(0,12), ipady=5)

    def select_output_dir(self):
        selected_dir = filedialog.askdirectory(initialdir=self.output_dir, title="Select output directory")
        if selected_dir:
            self.output_dir = selected_dir
            self.output_dir_label.config(text=self.output_dir)

    def connect_galaxy(self):
        url = self.url_entry.get().strip()
        api_key = self.api_entry.get().strip()
        if not url or not api_key:
            messagebox.showwarning("Empty fields", "Please enter your URL and API key.")
            return
        self.status.set("Conecting to galaxy...")
        self.connect_btn.config(state="disabled")
        try:
            self.gi = GalaxyInstance(url=url, key=api_key)
            self.histories = self.gi.histories.get_histories()
            self.histories_listbox.delete(0, tk.END)
            for hist in self.histories:
                self.histories_listbox.insert(tk.END, hist['name'])
            self.status.set(f"Conectado. {len(self.histories)} Histories found.")
        except Exception as e:
            messagebox.showerror("Connection error", f"Couldn't connect to Galaxy:\n{e}")
            self.status.set("Connection error.")
        finally:
            self.connect_btn.config(state="normal")

    def start_download(self):
        selected_indices = self.histories_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Select at least one story to download.")
            return
        self.selected_histories = [self.histories[i] for i in selected_indices]
        self._start_threaded_download()

    def download_all(self):
        if not self.histories:
            messagebox.showwarning("Warning", "No histories available for download.")
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
            messagebox.showwarning("Warning", "Write a search filter before download.")
            self._enable_buttons()
            return

        os.makedirs(self.output_dir, exist_ok=True)
        self.status.set("Initiating download...")

        try:
            for hist in self.selected_histories:
                hist_name = hist['name'].replace(" ", "_")
                hist_dir = os.path.join(self.output_dir, hist_name)
                os.makedirs(hist_dir, exist_ok=True)

                datasets = self.gi.histories.show_history(hist['id'], contents=True)
                for ds in datasets:
                    if search_filter in ds['name'].lower():
                        try:
                            # Verifica estado antes de descargar
                            details = self.gi.datasets.show_dataset(ds['id'])
                            state = details.get("state", "unknown")
                            if state != "ok":
                                self.status.set(f"⏭️ Skipping {ds['name']} (estado: {state})")
                                continue

                            ext = details.get('file_ext', 'dat')
                            filename = f"{ds['name'].replace(' ', '_')}.{ext}"
                            file_path = os.path.join(hist_dir, filename)

                            self.status.set(f"⬇️ Downloading: {ds['name']} (Historia: {hist_name})")
                            self.gi.datasets.download_dataset(
                                ds['id'], 
                                file_path=file_path, 
                                use_default_filename=False
                            )
                        except Exception as e:
                            self.status.set(f"⚠️ Error en {ds['name']}: {e}")
                            continue  # 🔑 salta a la siguiente
            self.status.set("✅ Downloading complete.")
            messagebox.showinfo("Finished", "Completed. Files with error were skipped.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during download:\n{e}")
            self.status.set("Error during download.")
        finally:
            self._enable_buttons()

if __name__ == "__main__":
    root = tk.Tk()
    app = GalaxyDownloaderApp(root)
    root.mainloop()
