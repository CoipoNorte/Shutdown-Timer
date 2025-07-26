import os
import subprocess
import time
import platform

def clear_icon_cache():
    if platform.system() != "Windows":
        print("❌ Este script solo funciona en sistemas Windows.")
        return

    try:
        print("🛑 Deteniendo el Explorador de Windows...")
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], check=True)

        # Rutas donde se guarda la caché de íconos
        icon_cache_paths = [
            os.path.expanduser("~\\AppData\\Local\\IconCache.db"),
            os.path.expanduser("~\\AppData\\Local\\Microsoft\\Windows\\Explorer")
        ]

        print("🧽 Eliminando archivos de caché de íconos...")
        for path in icon_cache_paths:
            if os.path.isdir(path):
                for file in os.listdir(path):
                    if file.startswith("iconcache") or file.endswith(".db"):
                        try:
                            os.remove(os.path.join(path, file))
                            print(f"🗑️ Eliminado: {file}")
                        except Exception as e:
                            print(f"⚠️ No se pudo eliminar {file}: {e}")
            elif os.path.isfile(path):
                try:
                    os.remove(path)
                    print(f"🗑️ Eliminado: {os.path.basename(path)}")
                except Exception as e:
                    print(f"⚠️ No se pudo eliminar {path}: {e}")

        time.sleep(2)
        print("🔄 Reiniciando el Explorador de Windows...")
        subprocess.run(["start", "explorer"], shell=True)

        print("✅ Caché de íconos limpiada y Explorador reiniciado.")

    except Exception as e:
        print(f"💥 Error inesperado: {e}")

if __name__ == "__main__":
    clear_icon_cache()
