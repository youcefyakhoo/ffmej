FROM n8nio/n8n

# Instalar FFmpeg
RUN apt-get update
RUN apt-get install -y ffmpeg

# Copiar archivos del proyecto al contenedor
COPY . /app
WORKDIR /app

# Hacer el script de Python ejecutable
RUN chmod +x render_video.py

# Asegurarnos de que n8n esté en el PATH (esto podría no ser necesario,
# pero lo incluimos por precaución)
ENV PATH="/usr/local/bin:$PATH"

# Comando para iniciar n8n (este se usará si ejecutas el contenedor localmente)
# CMD ["n8n", "start", "--port", "5678"]