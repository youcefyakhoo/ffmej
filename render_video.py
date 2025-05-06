from flask import Flask, request, send_file, jsonify
import subprocess
import os
import urllib.request
from uuid import uuid4

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render_video():
    data = request.get_json()
    url_imagen = data.get('ruta_imagen')
    url_audio = data.get('ruta_audio')  # opcional
    nombre_salida = data.get('ruta_salida', 'video_salida.mp4')

    if not url_imagen:
        return jsonify({'error': 'Falta la URL de la imagen'}), 400

    nombre_imagen = f'temp_imagen_{uuid4()}.png'
    ruta_imagen = f'/tmp/{nombre_imagen}'
    ruta_salida = f'/tmp/{nombre_salida}'

    try:
        urllib.request.urlretrieve(url_imagen, ruta_imagen)
    except Exception as e:
        return jsonify({'error': f'Error al descargar la imagen: {e}'}), 500

    ruta_audio_archivo = None
    if url_audio:
        try:
            nombre_audio = f'temp_audio_{uuid4()}.mp3'
            ruta_audio_archivo = f'/tmp/{nombre_audio}'
            urllib.request.urlretrieve(url_audio, ruta_audio_archivo)
        except Exception as e:
            return jsonify({'error': f'Error al descargar el audio: {e}'}), 500

    # Construcción del comando FFmpeg
    comando = [
        "ffmpeg", "-y", "-loop", "1", "-t", "5", "-i", ruta_imagen,
    ]
    if ruta_audio_archivo:
        comando.extend(["-i", ruta_audio_archivo])
    comando.extend([
        "-c:v", "libx264", "-c:a", "aac", "-shortest", ruta_salida
    ])

    try:
        subprocess.run(comando, check=True, capture_output=True, text=True)
        return send_file(ruta_salida, mimetype='video/mp4', as_attachment=True, download_name=nombre_salida)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error al ejecutar FFmpeg: {e.stderr}'}), 500
    finally:
        try:
            os.remove(ruta_imagen)
            if ruta_audio_archivo:
                os.remove(ruta_audio_archivo)
        except Exception as e:
            print(f"Error al limpiar archivos temporales: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
