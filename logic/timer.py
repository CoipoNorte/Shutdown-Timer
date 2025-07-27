import threading
import time
from datetime import datetime, timedelta
from tkinter import messagebox
from system.shutdown import shutdown_computer
import sys

class TimerLogic:
    def __init__(self, app):
        self.app = app
        self.timer_running = False
        self.remaining_time = 0

    def adjust_time(self, unit, increment):
        try:
            if unit == 'hours':
                current = int(self.app.hours_var.get() or 0)
                new_value = max(0, min(99, current + increment))
                self.app.hours_var.set(str(new_value))
            else:
                current = int(self.app.minutes_var.get() or 0)
                new_value = max(0, min(59, current + increment))
                self.app.minutes_var.set(str(new_value))
        except ValueError:
            pass

    def start_timer(self):
        try:
            hours = int(self.app.hours_var.get() or 0)
            minutes = int(self.app.minutes_var.get() or 0)
            if hours == 0 and minutes == 0:
                messagebox.showerror("Error", "Por favor ingresa un tiempo válido")
                return
            if hours > 99 or minutes > 59:
                messagebox.showerror("Error", "Valores máximos: 99 horas, 59 minutos")
                return
            total_seconds = (hours * 3600) + (minutes * 60)
            self.remaining_time = total_seconds
            self.timer_running = True
            self.app.start_button.configure(state="disabled")
            self.app.cancel_button.configure(state="normal")
            self.app.hours_spinbox.configure(state="disabled")
            self.app.minutes_spinbox.configure(state="disabled")
            shutdown_time = datetime.now() + timedelta(seconds=total_seconds)
            self.app.status_label.configure(
                text=f"Apagado programado para: {shutdown_time.strftime('%H:%M:%S')}",
                text_color="#3b8ed0"
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
            self.app.time_display.configure(text=time_format)
            if self.remaining_time <= 60:
                self.app.time_display.configure(text_color="#ef476f")
            elif self.remaining_time <= 300:
                self.app.time_display.configure(text_color="#3b8ed0")
            else:
                self.app.time_display.configure(text_color="#43aa8b")
            time.sleep(1)
            self.remaining_time -= 1
        if self.timer_running and self.remaining_time == 0:
            shutdown_computer(self.app.force_shutdown.get())

    def cancel_timer(self, icon=None, item=None):
        def restore_widgets():
            self.timer_running = False
            self.remaining_time = 0
            self.app.start_button.configure(state="normal")
            self.app.cancel_button.configure(state="disabled")
            self.app.hours_spinbox.configure(state="normal")
            self.app.minutes_spinbox.configure(state="normal")
            self.app.time_display.configure(text="00:00:00", text_color="#43aa8b")
            self.app.status_label.configure(text="Cancelado", text_color="#f5f6fa")
        self.app.save_and_restore_position(restore_widgets)

    def quit_app(self, icon=None, item=None):
        if self.timer_running:
            if not self.app.root.winfo_viewable():
                self.app.root.deiconify()
            if messagebox.askyesno("Confirmar", "Hay un temporizador activo. ¿Deseas salir de todos modos?"):
                self.timer_running = False
                if self.app.tray_icon:
                    self.app.tray_icon.stop()
                self.app.root.quit()
                sys.exit()
        else:
            if self.app.tray_icon:
                self.app.tray_icon.stop()
            self.app.root.quit()
            sys.exit()