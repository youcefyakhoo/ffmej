from flask import Flask, request, jsonify
import subprocess
import os
import urllib.request
from uuid import uuid4

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render_video():
    data = request.get_json()
    url_imagen = data.get('ruta_imagen')  # URL de la imagen
    url_audio = data.get('ruta_audio')    # URL del audio (opcional)
    nombre_salida = data.get('ruta_salida')  # nombre de archivo final, ej: 'video.mp4'

    if not url_imagen or not nombre_salida:
        return jsonify({'error': 'Faltan argumentos: ruta_imagen (URL), ruta_salida (audio es opcional)'}), 400

    # Descargar imagen
    try:
        nombre_archivo_imagen = f"temp_imagen_{uuid4()}.png"
        ruta_imagen = f'/tmp/{nombre_archivo_imagen}'
        urllib.request.urlretrieve(url_imagen, ruta_imagen)
    except Exception as e:
        return jsonify({'error': f'Error al descargar la imagen: {e}'}), 500

    ruta_salida = f'/tmp/{nombre_salida}'
    ruta_audio = None

    # Descargar audio si se proporciona
    if url_audio:
        try:
            nombre_archivo_audio = f"temp_audio_{uuid4()}.mp3"
            ruta_audio = f'/tmp/{nombre_archivo_audio}'
            urllib.request.urlretrieve(url_audio, ruta_audio)
        except Exception as e:
            return jsonify({'error': f'Error al descargar el audio: {e}'}), 500

    # Verificaciones
    if not os.path.exists(ruta_imagen):
        return jsonify({'error': f'Imagen no encontrada: {ruta_imagen}'}), 400
    if url_audio and not os.path.exists(ruta_audio):
        return jsonify({'error': f'Audio no encontrado: {ruta_audio}'}), 400

    # Comando ffmpeg
    comando = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", ruta_imagen
    ]

    if ruta_audio:
        comando.extend(["-i", ruta_audio])

    comando.extend([
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p"
    ])

    if ruta_audio:
        comando.extend([
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest"
        ])
    else:
        comando.extend(["-t", "10"])  # 10 segundos si no hay audio

    comando.append(ruta_salida)

    # Ejecutar FFmpeg
    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        return jsonify({'video_path': ruta_salida}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error al ejecutar FFmpeg: {e.stderr}'}), 500
    finally:
        try:
            os.remove(ruta_imagen)
            if ruta_audio:
                os.remove(ruta_audio)
        except Exception as e:
            print(f"Error al eliminar archivos temporales: {e}")

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
