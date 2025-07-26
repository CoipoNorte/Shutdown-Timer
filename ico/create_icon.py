from PIL import Image, ImageDraw
import os

def create_shutdown_icon():
    """Crear ícono de shutdown timer en varios tamaños"""
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        # Crear imagen con fondo transparente
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Calcular dimensiones
        padding = size // 8
        circle_bounds = [padding, padding, size-padding, size-padding]
        
        # Círculo exterior con gradiente
        for i in range(3):
            offset = i * 2
            color = (31 + i*10, 83 + i*10, 141 + i*10)
            draw.ellipse([padding+offset, padding+offset, 
                         size-padding-offset, size-padding-offset], 
                         fill=color)
        
        # Borde blanco
        draw.ellipse(circle_bounds, outline=(255, 255, 255), width=max(1, size//32))
        
        # Símbolo de power
        line_width = max(2, size // 16)
        center_x = size // 2
        
        # Línea vertical
        line_y1 = size // 4
        line_y2 = size // 2
        draw.rectangle([center_x - line_width//2, line_y1, 
                       center_x + line_width//2, line_y2], 
                       fill=(255, 255, 255))
        
        # Arco
        arc_padding = size // 4
        arc_bounds = [arc_padding, arc_padding, size-arc_padding, size-arc_padding]
        
        # Dibujar el arco con múltiples líneas para hacerlo más grueso
        for i in range(line_width):
            draw.arc([arc_bounds[0]-i, arc_bounds[1]-i, 
                     arc_bounds[2]+i, arc_bounds[3]+i], 
                     start=45, end=315, fill=(255, 255, 255), width=1)
        
        images.append(img)

    # Guardar como .ico
    images[0].save('shutdown_timer.ico', format='ICO', sizes=[(s, s) for s in sizes])
    print("✓ Ícono creado: shutdown_timer.ico")

if __name__ == "__main__":
    create_shutdown_icon()