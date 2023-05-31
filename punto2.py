import numpy as np
from PIL import Image, ImageOps
import PyPDF4
import io
import matplotlib.pyplot as plt
import subprocess

# Función para convertir un archivo PDF a PNG
def convert_pdf_to_png(pdf_file):
    pdf = PyPDF4.PdfFileReader(pdf_file)
    page = pdf.getPage(0)
    xObject = page['/Resources']['/XObject'].getObject()
    img_ref = list(xObject)[0]
    img = xObject[img_ref]
    img_data = img._data
    img = Image.open(io.BytesIO(img_data))
    return np.array(img)  # Convertir la imagen PIL a una matriz NumPy

# Función para convertir un archivo EPS a PNG utilizando GhostScript
def convert_eps_to_png(eps_file):
    output_file = 'eps_converted.png'
    resolution = 600  # Aumentar la resolución a 600 DPI
    gs_command = f"gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r{resolution} -sOutputFile={output_file} {eps_file}"
    subprocess.run(gs_command, shell=True, check=True)
    return output_file

# Cargar imágenes
png_image = Image.open('/content/PNG_transparency_demonstration_1.png')
pdf_image = convert_pdf_to_png('/content/aaaaaaaaaaaaa.pdf')
eps_image = Image.open(convert_eps_to_png('/content/6dvq_ojxh_210511.eps'))

# Obtener tensores y dimensiones
png_tensor = np.asarray(png_image)
pdf_tensor = np.asarray(pdf_image)
eps_tensor = np.asarray(eps_image)

# Mostrar dimensiones de los tensores
print(f'PNG Tensor: {png_tensor.shape}')
print(f'PDF Tensor: {pdf_tensor.shape}')
print(f'EPS Tensor: {eps_tensor.shape}')

# Función para redimensionar una imagen según una dimensión máxima
def resize_image(image, max_dimension):
    width, height = image.size
    scale_factor = max_dimension / max(height, width)
    new_width, new_height = int(scale_factor * width), int(scale_factor * height)
    return image.resize((new_width, new_height))

max_dimension = 1920  # Ajustar el tamaño máximo de la imagen en píxeles

# Mostrar imágenes originales
plt.imshow(png_image)
plt.title('PNG Image')
plt.show()

plt.imshow(pdf_image)
plt.title('PDF Image')
plt.show()

# Redimensionar la imagen EPS
eps_image_resized = resize_image(eps_image, max_dimension)

plt.imshow(eps_image_resized)
plt.title('EPS Image')
plt.show()

print("\n MODIFICADAS:")

# Función para dibujar líneas diagonales en una imagen
def draw_lines(tensor, line_thickness):
    height, width = tensor.shape[:2]
    diag_length = min(height, width)
    
    for b in range(line_thickness):
        for i in range(diag_length - b):
            # Diagonal principal
            tensor[i, i + b] = 0
            # Diagonal secundaria
            tensor[i, width - 1 - i - b] = 0
            # Si la imagen es a color (tiene 3 canales)
            if len(tensor.shape) == 3:
                tensor[i, i + b, 1:] = 255
                tensor[i, width - 1 - i - b, 1:] = 255
    return tensor

# Función para mostrar una imagen con su título
def show_image(tensor, title):
    if len(tensor.shape) == 3:
        plt.imshow(tensor)
    else:
        plt.imshow(tensor, cmap='gray')
    plt.title(title)
    plt.show()

line_thickness = 10

png_tensor = draw_lines(png_tensor, line_thickness)
pdf_tensor = draw_lines(pdf_tensor, line_thickness)
eps_tensor = draw_lines(eps_tensor, line_thickness)

# Mostrar imágenes modificadas
show_image(png_tensor, ' ')
show_image(pdf_tensor, ' ')
show_image(eps_tensor, ' ')