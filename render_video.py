from flask import Flask, request, jsonify
import subprocess
import os
import urllib.request  # Para descargar la imagen si es necesario
from uuid import uuid4  # Para generar nombres de archivos únicos

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render_video():
    data = request.get_json()
    url_imagen = data.get('ruta_imagen')  # URL de la imagen
    nombre_salida = data.get('ruta_salida')  # nombre del archivo de salida (ej: "video.mp4")

    if not url_imagen or not nombre_salida:
        return jsonify({'error': 'Faltan argumentos: ruta_imagen (URL) y ruta_salida'}), 400

    try:
        nombre_archivo_imagen = f"temp_imagen_{uuid4()}.png"
        ruta_imagen = f'/tmp/{nombre_archivo_imagen}'
        urllib.request.urlretrieve(url_imagen, ruta_imagen)
    except Exception as e:
        return jsonify({'error': f'Error al descargar la imagen: {e}'}), 500

    ruta_salida = f'/tmp/{nombre_salida}'

    if not os.path.exists(ruta_imagen):
        return jsonify({'error': f'No se encontró la imagen descargada: {ruta_imagen}'}), 400

    comando = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-framerate", "2",  # framerate bajo
        "-i", ruta_imagen,
        "-c:v", "libx264",
        "-t", "5",  # duración en segundos
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-movflags", "+faststart",
        ruta_salida
    ]

    try:
        subprocess.run(comando, check=True, capture_output=True, text=True)
        return jsonify({'video_path': ruta_salida}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error al ejecutar FFmpeg: {e.stderr}'}), 500
    finally:
        try:
            os.remove(ruta_imagen)
        except OSError as e:
            print(f"Error al eliminar archivo temporal: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
