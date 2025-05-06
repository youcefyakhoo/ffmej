from flask import Flask, request, jsonify
import subprocess
import os
import urllib.request  # Para descargar la imagen si es necesario
from uuid import uuid4  # Para generar nombres de archivos únicos

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render_video():
    data = request.get_json()
    url_imagen = data.get('ruta_imagen')  # Ahora esperamos una URL
    url_audio = data.get('ruta_audio')
    nombre_salida = data.get('ruta_salida')

    if not url_imagen or not nombre_salida:
        return jsonify({'error': 'Faltan argumentos: ruta_imagen (URL), ruta_salida (ruta_audio es opcional)'}), 400

    # Descargar la imagen
    try:
        nombre_archivo_imagen = f"temp_imagen_{uuid4()}.png"  # Nombre único
        ruta_imagen = f'/tmp/{nombre_archivo_imagen}'
        urllib.request.urlretrieve(url_imagen, ruta_imagen)
    except Exception as e:
        return jsonify({'error': f'Error al descargar la imagen: {e}'}), 500

    ruta_salida = f'/tmp/{nombre_salida}'
    ruta_audio = None
    if url_audio:
        try:
            nombre_archivo_audio = f"temp_audio_{uuid4()}.mp3" # Nombre único
            ruta_audio = f'/tmp/{nombre_archivo_audio}'
            urllib.request.urlretrieve(url_audio, ruta_audio)
        except Exception as e:
            return jsonify({'error': f'Error al descargar el audio: {e}'}), 500

    if not os.path.exists(ruta_imagen):
        return jsonify({'error': f'No se encontró la imagen descargada: {ruta_imagen}'}), 400
    if url_audio and not os.path.exists(ruta_audio):
        return jsonify({'error': f'No se encontró el audio descargado: {ruta_audio}'}), 400

    comando = [
        "ffmpeg",
        "-y",  # Sobrescribir archivos existentes
        "-loop", "1",
        "-i", ruta_imagen,
    ]
    if ruta_audio:
        comando.extend(["-i", ruta_audio])
    comando.extend([
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        "-b:a", "192k",
        "-shortest",
        ruta_salida
    ])

    try:
        subprocess.run(comando, check=True, capture_output=True, text=True)
        return jsonify({'video_path': ruta_salida}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error al ejecutar FFmpeg: {e.stderr}'}), 500
    finally:
        # Limpiar archivos temporales (importante!)
        try:
            os.remove(ruta_imagen)
            if ruta_audio:
                os.remove(ruta_audio)
        except OSError as e:
            print(f"Error al eliminar archivos temporales: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)