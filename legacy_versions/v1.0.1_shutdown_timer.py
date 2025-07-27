import sys
import customtkinter as ctk
import os
import threading
import time
from datetime import datetime, timedelta
import pystray
from PIL import Image, ImageDraw
from tkinter import messagebox
import json

# Ocultar consola en Windows
if sys.platform == "win32":
    import ctypes
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    SW_HIDE = 0
    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, SW_HIDE)

# Obtiene la ruta absoluta, compatible con PyInstaller y desarrollo.
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Paleta de colores
BG = "#23272f"
ACCENT = "#3b8ed0"
TEXT = "#f5f6fa"
DISABLED = "#7b7b7b"
SUCCESS = "#43aa8b"
DANGER = "#ef476f"
SEPARATOR = "#2d3142"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ShutdownTimerApp:
    def __init__(self):
        self.config_file = "shutdown_timer_config.json"
        self.load_config()
        self.root = ctk.CTk()
        self.root.title("Shutdown Timer")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        # self.root.iconbitmap("shutdown_timer.ico")
        try:
            self.root.iconbitmap(resource_path("shutdown_timer.ico"))
        except Exception:
            pass
        self.timer_running = False
        self.remaining_time = 0
        self.icon = None
        self.force_shutdown = ctk.BooleanVar(value=True)
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.setup_ui()
        self.center_window()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.theme = config.get('theme', 'dark')
        except:
            self.theme = 'dark'
        ctk.set_appearance_mode(self.theme)

    def save_config(self):
        config = {'theme': self.theme}
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass

    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root, corner_radius=18, fg_color=BG)
        main_frame.pack(fill="both", expand=True, padx=18, pady=18)

        # Título
        ctk.CTkLabel(
            main_frame, 
            text="Shutdown Timer",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=ACCENT
        ).pack(pady=(10, 0))

        # Separador
        ctk.CTkLabel(main_frame, text="", height=2, fg_color=SEPARATOR).pack(fill="x", pady=(8, 16))

        # Tiempo (centrado, botones a los lados)
        time_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        time_frame.pack(pady=8)

        # Horas
        ctk.CTkLabel(time_frame, text="Horas", font=ctk.CTkFont(size=13), text_color=TEXT).grid(row=0, column=0, padx=6, pady=(0,2))
        self.hours_var = ctk.StringVar(value="0")
        hours_box = ctk.CTkFrame(time_frame, fg_color="transparent")
        hours_box.grid(row=1, column=0, padx=6)
        ctk.CTkButton(hours_box, text="–", width=28, height=32, font=ctk.CTkFont(size=18), command=lambda: self.adjust_time('hours', -1), fg_color=SEPARATOR, hover_color=ACCENT).pack(side="left")
        self.hours_spinbox = ctk.CTkEntry(
            hours_box, width=38, height=32, font=ctk.CTkFont(size=18, weight="bold"),
            textvariable=self.hours_var, justify="center", border_width=2, border_color=ACCENT
        )
        self.hours_spinbox.pack(side="left", padx=2)
        ctk.CTkButton(hours_box, text="+", width=28, height=32, font=ctk.CTkFont(size=18), command=lambda: self.adjust_time('hours', 1), fg_color=SEPARATOR, hover_color=ACCENT).pack(side="left")

        # Separador visual
        ctk.CTkLabel(time_frame, text="", width=10, fg_color="transparent").grid(row=1, column=1)

        # Minutos
        ctk.CTkLabel(time_frame, text="Minutos", font=ctk.CTkFont(size=13), text_color=TEXT).grid(row=0, column=2, padx=6, pady=(0,2))
        minutes_box = ctk.CTkFrame(time_frame, fg_color="transparent")
        minutes_box.grid(row=1, column=2, padx=6)
        ctk.CTkButton(minutes_box, text="–", width=28, height=32, font=ctk.CTkFont(size=18), command=lambda: self.adjust_time('minutes', -1), fg_color=SEPARATOR, hover_color=ACCENT).pack(side="left")
        self.minutes_var = ctk.StringVar(value="30")
        self.minutes_spinbox = ctk.CTkEntry(
            minutes_box, width=38, height=32, font=ctk.CTkFont(size=18, weight="bold"),
            textvariable=self.minutes_var, justify="center", border_width=2, border_color=ACCENT
        )
        self.minutes_spinbox.pack(side="left", padx=2)
        ctk.CTkButton(minutes_box, text="+", width=28, height=32, font=ctk.CTkFont(size=18), command=lambda: self.adjust_time('minutes', 1), fg_color=SEPARATOR, hover_color=ACCENT).pack(side="left")

        # Display del tiempo restante
        self.time_display = ctk.CTkLabel(
            main_frame,
            text="00:00:00",
            font=ctk.CTkFont(size=44, weight="bold"),
            text_color=SUCCESS
        )
        self.time_display.pack(pady=24)

        # Estado
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Inactivo",
            font=ctk.CTkFont(size=15),
            text_color=TEXT
        )
        self.status_label.pack(pady=(0, 12))

        # Checkbox forzar cierre
        force_checkbox = ctk.CTkCheckBox(
            main_frame,
            text="Forzar cierre de aplicaciones",
            variable=self.force_shutdown,
            font=ctk.CTkFont(size=13),
            corner_radius=5,
            border_color=ACCENT,
            fg_color=ACCENT,
            hover_color=ACCENT
        )
        force_checkbox.pack(pady=(0, 14))

        # Botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=6)
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Iniciar",
            width=110,
            height=38,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_timer,
            corner_radius=19,
            fg_color=ACCENT,
            text_color=BG,
            hover_color="#5fa8e6"
        )
        self.start_button.grid(row=0, column=0, padx=10)
        self.cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            width=110,
            height=38,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.cancel_timer,
            state="disabled",
            corner_radius=19,
            fg_color=DANGER,
            hover_color="#b3003c"
        )
        self.cancel_button.grid(row=0, column=1, padx=10)

        # Minimizar a bandeja
        minimize_button = ctk.CTkButton(
            main_frame,
            text="Minimizar a la bandeja",
            width=200,
            height=32,
            font=ctk.CTkFont(size=13),
            command=self.hide_window,
            corner_radius=16,
            fg_color=SEPARATOR,
            text_color=TEXT,
            hover_color="#444"
        )
        minimize_button.pack(pady=(18, 0))

    def adjust_time(self, unit, increment):
        try:
            if unit == 'hours':
                current = int(self.hours_var.get() or 0)
                new_value = max(0, min(99, current + increment))
                self.hours_var.set(str(new_value))
            else:
                current = int(self.minutes_var.get() or 0)
                new_value = max(0, min(59, current + increment))
                self.minutes_var.set(str(new_value))
        except ValueError:
            pass

    def toggle_theme(self):
        if hasattr(self, 'theme_switch') and self.theme_switch.get():
            self.theme = "light"
        else:
            self.theme = "dark"
        ctk.set_appearance_mode(self.theme)
        self.save_config()

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_tray_icon(self):
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(image)
        draw.ellipse([10, 10, 54, 54], fill=ACCENT, outline='white', width=2)
        draw.line([32, 20, 32, 35], fill='white', width=4)
        draw.arc([24, 24, 40, 40], start=45, end=315, fill='white', width=3)
        return image

    def setup_tray_icon(self):
        menu = pystray.Menu(
            pystray.MenuItem("Mostrar", self.show_window),
            pystray.MenuItem("Cancelar temporizador", self.cancel_timer),
            pystray.MenuItem("Salir", self.quit_app)
        )
        image = self.create_tray_icon()
        self.icon = pystray.Icon("shutdown_timer", image, "Shutdown Timer", menu)
        icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        icon_thread.start()

    def hide_window(self):
        self.root.withdraw()
        if self.icon is None:
            self.setup_tray_icon()

    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self, icon=None, item=None):
        if self.timer_running:
            if not self.root.winfo_viewable():
                self.root.deiconify()
            if messagebox.askyesno("Confirmar", "Hay un temporizador activo. ¿Deseas salir de todos modos?"):
                self.timer_running = False
                if self.icon:
                    self.icon.stop()
                self.root.quit()
                sys.exit()
        else:
            if self.icon:
                self.icon.stop()
            self.root.quit()
            sys.exit()

    def start_timer(self):
        try:
            hours = int(self.hours_var.get() or 0)
            minutes = int(self.minutes_var.get() or 0)
            if hours == 0 and minutes == 0:
                messagebox.showerror("Error", "Por favor ingresa un tiempo válido")
                return
            if hours > 99 or minutes > 59:
                messagebox.showerror("Error", "Valores máximos: 99 horas, 59 minutos")
                return
            total_seconds = (hours * 3600) + (minutes * 60)
            self.remaining_time = total_seconds
            self.timer_running = True
            self.start_button.configure(state="disabled")
            self.cancel_button.configure(state="normal")
            self.hours_spinbox.configure(state="disabled")
            self.minutes_spinbox.configure(state="disabled")
            shutdown_time = datetime.now() + timedelta(seconds=total_seconds)
            self.status_label.configure(
                text=f"Apagado programado para: {shutdown_time.strftime('%H:%M:%S')}",
                text_color=ACCENT
            )
            timer_thread = threading.Thread(target=self.countdown)
            timer_thread.daemon = True
            timer_thread.start()
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa números válidos")

    def countdown(self):
        while self.remaining_time > 0 and self.timer_running:
            hours, remainder = divmod(self.remaining_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_format = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.time_display.configure(text=time_format)
            if self.remaining_time <= 60:
                self.time_display.configure(text_color=DANGER)
            elif self.remaining_time <= 300:
                self.time_display.configure(text_color=ACCENT)
            else:
                self.time_display.configure(text_color=SUCCESS)
            time.sleep(1)
            self.remaining_time -= 1
        if self.timer_running and self.remaining_time == 0:
            self.shutdown_computer()

    def cancel_timer(self, icon=None, item=None):
        self.timer_running = False
        self.remaining_time = 0
        self.start_button.configure(state="normal")
        self.cancel_button.configure(state="disabled")
        self.hours_spinbox.configure(state="normal")
        self.minutes_spinbox.configure(state="normal")
        self.time_display.configure(text="00:00:00", text_color=SUCCESS)
        self.status_label.configure(text="Cancelado", text_color=TEXT)

    def shutdown_computer(self):
        if sys.platform == "win32":
            if self.force_shutdown.get():
                os.system("shutdown /s /f /t 0")
            else:
                os.system("shutdown /s /t 0")
        elif sys.platform == "darwin":
            if self.force_shutdown.get():
                os.system("sudo shutdown -h now")
            else:
                os.system("osascript -e 'tell app \"System Events\" to shut down'")
        else:
            if self.force_shutdown.get():
                os.system("shutdown -h now")
            else:
                os.system("shutdown -h +0")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ShutdownTimerApp()
    app.run()