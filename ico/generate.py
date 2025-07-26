import os
from rembg import remove
from PIL import Image

# 🛠️ Paso 1: Detectar ruta del script y archivo
script_dir = os.path.dirname(os.path.abspath(__file__))
input_filename = "img_ico.png"
input_path = os.path.join(script_dir, input_filename)
transparent_filename = "img_ico_transparent.png"
output_ico_filename = "icon.ico"

# 🔍 Paso 2: Verificar existencia del archivo original
if not os.path.exists(input_path):
    print(f"❌ No se encontró el archivo '{input_filename}' en la carpeta del script.")
else:
    try:
        # ✂️ Paso 3: Eliminar fondo
        with open(input_path, "rb") as f:
            input_image = f.read()
        output_image = remove(input_image)

        transparent_path = os.path.join(script_dir, transparent_filename)
        with open(transparent_path, "wb") as f:
            f.write(output_image)
        print(f"✅ Imagen transparente guardada como '{transparent_filename}'.")

        # 🧙‍♂️ Paso 4: Convertir a .ico
        img = Image.open(transparent_path)
        ico_path = os.path.join(script_dir, output_ico_filename)
        img.save(ico_path, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128)])
        print(f"🪄 Archivo ICO generado como '{output_ico_filename}'.")

    except Exception as e:
        print("💥 Ocurrió un error:", e)
