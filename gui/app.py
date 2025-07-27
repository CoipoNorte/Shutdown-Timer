import customtkinter as ctk
from logic.timer import TimerLogic
from tray.trayicon import TrayIcon
import os

# Paleta de colores
BG = "#23272f"
ACCENT = "#3b8ed0"
TEXT = "#f5f6fa"
SUCCESS = "#43aa8b"
DANGER = "#ef476f"
SEPARATOR = "#2d3142"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ShutdownTimerApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        # Remover barra de título y bordes para look tipo widget
        self.root.overrideredirect(True)
        # Permitir mover la ventana arrastrando
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self._offsetx = 0
        self._offsety = 0
        # Intentar poner ícono de ventana (opcional)
        try:
            self.root.iconbitmap(os.path.join("assets", "shutdown_timer.ico"))
        except Exception:
            pass
        self.timer_logic = TimerLogic(self)
        self.tray_icon = None
        self.force_shutdown = ctk.BooleanVar(value=True)
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        self.setup_ui()
        self.center_window()

    def start_move(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def do_move(self, event):
        x = event.x_root - self._offsetx
        y = event.y_root - self._offsety
        self.root.geometry(f"+{x}+{y}")

    def save_and_restore_position(self, func, *args, **kwargs):
        # Guarda la posición actual
        self.root.update_idletasks()
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        # Ejecuta la función que puede mover la ventana
        func(*args, **kwargs)
        # Restaura la posición
        self.root.geometry(f"+{x}+{y}")

    def setup_ui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, corner_radius=18, fg_color=BG)
        main_frame.pack(fill="both", expand=True, padx=18, pady=18)
        # Separador superior
        ctk.CTkLabel(main_frame, text="", height=2, fg_color=SEPARATOR).pack(fill="x", pady=(0, 16))
        # Frame de tiempo
        time_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        time_frame.pack(pady=8)
        # Horas
        ctk.CTkLabel(time_frame, text="Horas", font=ctk.CTkFont(size=13), text_color=TEXT).grid(row=0, column=0, padx=6, pady=(0,2))
        self.hours_var = ctk.StringVar(value="0")
        hours_box = ctk.CTkFrame(time_frame, fg_color="transparent")
        hours_box.grid(row=1, column=0, padx=6)
        ctk.CTkButton(hours_box, text="–", width=28, height=32, font=ctk.CTkFont(size=18), command=lambda: self.timer_logic.adjust_time('hours', -1), fg_color=SEPARATOR, hover_color=ACCENT).pack(side="left")
        self.hours_spinbox = ctk.CTkEntry(hours_box, width=38, height=32, font=ctk.CTkFont(size=18, weight="bold"), textvariable=self.hours_var, justify="center", border_width=2, border_color=ACCENT)
        self.hours_spinbox.pack(side="left", padx=2)
        ctk.CTkButton(hours_box, text="+", width=28, height=32, font=ctk.CTkFont(size=18), command=lambda: self.timer_logic.adjust_time('hours', 1), fg_color=SEPARATOR, hover_color=ACCENT).pack(side="left")
        # Separador visual
        ctk.CTkLabel(time_frame, text="", width=10, fg_color="transparent").grid(row=1, column=1)
        # Minutos
        ctk.CTkLabel(time_frame, text="Minutos", font=ctk.CTkFont(size=13), text_color=TEXT).grid(row=0, column=2, padx=6, pady=(0,2))
        minutes_box = ctk.CTkFrame(time_frame, fg_color="transparent")
        minutes_box.grid(row=1, column=2, padx=6)
        ctk.CTkButton(minutes_box, text="–", width=28, height=32, font=ctk.CTkFont(size=18), command=lambda: self.timer_logic.adjust_time('minutes', -1), fg_color=SEPARATOR, hover_color=ACCENT).pack(side="left")
        self.minutes_var = ctk.StringVar(value="30")
        self.minutes_spinbox = ctk.CTkEntry(minutes_box, width=38, height=32, font=ctk.CTkFont(size=18, weight="bold"), textvariable=self.minutes_var, justify="center", border_width=2, border_color=ACCENT)
        self.minutes_spinbox.pack(side="left", padx=2)
        ctk.CTkButton(minutes_box, text="+", width=28, height=32, font=ctk.CTkFont(size=18), command=lambda: self.timer_logic.adjust_time('minutes', 1), fg_color=SEPARATOR, hover_color=ACCENT).pack(side="left")
        # Display del tiempo restante
        self.time_display = ctk.CTkLabel(main_frame, text="00:00:00", font=ctk.CTkFont(size=44, weight="bold"), text_color=SUCCESS)
        self.time_display.pack(pady=24)
        # Estado
        self.status_label = ctk.CTkLabel(main_frame, text="Inactivo", font=ctk.CTkFont(size=15), text_color=TEXT)
        self.status_label.pack(pady=(0, 12))
        # Checkbox forzar cierre
        force_checkbox = ctk.CTkCheckBox(main_frame, text="Forzar cierre de aplicaciones", variable=self.force_shutdown, font=ctk.CTkFont(size=13), corner_radius=5, border_color=ACCENT, fg_color=ACCENT, hover_color=ACCENT)
        force_checkbox.pack(pady=(0, 14))
        # Botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=6)
        self.start_button = ctk.CTkButton(button_frame, text="Iniciar", width=110, height=38, font=ctk.CTkFont(size=15, weight="bold"), command=self.timer_logic.start_timer, corner_radius=19, fg_color=ACCENT, text_color=BG, hover_color="#5fa8e6")
        self.start_button.grid(row=0, column=0, padx=10)
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", width=110, height=38, font=ctk.CTkFont(size=15, weight="bold"), command=self.timer_logic.cancel_timer, state="disabled", corner_radius=19, fg_color=DANGER, hover_color="#b3003c")
        self.cancel_button.grid(row=0, column=1, padx=10)
        minimize_button = ctk.CTkButton(main_frame, text="Minimizar a la bandeja", width=200, height=32, font=ctk.CTkFont(size=13), command=self.hide_window, corner_radius=16, fg_color=SEPARATOR, text_color=TEXT, hover_color="#444")
        minimize_button.pack(pady=(18, 0))

    def hide_window(self):
        self.root.withdraw()
        if self.tray_icon is None:
            self.tray_icon = TrayIcon(self)

    def show_window(self, icon=None, item=None):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def quit_app(self, icon=None, item=None):
        self.timer_logic.quit_app(icon, item)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def run(self):
        self.root.mainloop()