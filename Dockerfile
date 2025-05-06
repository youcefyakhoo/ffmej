FROM n8nio/n8n  # Usa la imagen oficial de n8n como base

# Instalar FFmpeg
RUN apt-get update
RUN apt-get install -y ffmpeg

# Copiar archivos del proyecto al contenedor
COPY . /app      # Copia todo el directorio actual a /app en el contenedor
WORKDIR /app     # Establece /app como el directorio de trabajo

# Hacer el script de Python ejecutable
RUN chmod +x render_video.py