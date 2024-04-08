# Imagen base de Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos y directorios necesarios al contenedor
COPY requirements.txt .
COPY spa.traineddata .
COPY VegaChat.py .
COPY AzureOD_SystemBar.onnx .
COPY data/ ./data/
COPY storage/ ./storage/


# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Mueve spa.traineddata a la ubicación necesaria
# RUN mv ./spa.traineddata /usr/share/tesseract-ocr/4.00/tessdata
RUN mv ./spa.traineddata /usr/share/tesseract-ocr/5/tessdata


# Comando para ejecutar la aplicación
CMD ["python", "./VegaChat.py"]