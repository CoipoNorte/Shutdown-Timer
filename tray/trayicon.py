import threading
import pystray
from PIL import Image, ImageDraw

class TrayIcon:
    def __init__(self, app):
        self.app = app
        self.icon = None
        self.setup_tray_icon()

    def create_tray_icon(self):
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(image)
        draw.ellipse([10, 10, 54, 54], fill="#3b8ed0", outline='white', width=2)
        draw.line([32, 20, 32, 35], fill='white', width=4)
        draw.arc([24, 24, 40, 40], start=45, end=315, fill='white', width=3)
        return image

    def setup_tray_icon(self):
        menu = pystray.Menu(
            pystray.MenuItem("Mostrar", self.app.show_window),
            pystray.MenuItem("Cancelar temporizador", self.app.timer_logic.cancel_timer),
            pystray.MenuItem("Salir", self.app.quit_app)
        )
        image = self.create_tray_icon()
        self.icon = pystray.Icon("shutdown_timer", image, "Shutdown Timer", menu)
        icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        icon_thread.start()

    def stop(self):
        if self.icon:
            self.icon.stop()