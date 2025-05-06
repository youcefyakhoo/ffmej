from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render_video():
    data = request.get_json()
    ruta_imagen = data.get('ruta_imagen')
    ruta_audio = data.get('ruta_audio')
    ruta_salida = data.get('ruta_salida')

    if not ruta_imagen or not ruta_audio or not ruta_salida:
        return jsonify({'error': 'Faltan argumentos: ruta_imagen, ruta_audio, ruta_salida'}), 400

    if not os.path.exists(ruta_imagen):
        return jsonify({'error': f'No se encontró la imagen: {ruta_imagen}'}), 400
    if not os.path.exists(ruta_audio):
        return jsonify({'error': f'No se encontró el audio: {ruta_audio}'}), 400

    comando = [
        "ffmpeg",
        "-loop", "1",
        "-i", ruta_imagen,
        "-i", ruta_audio,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "experimental",
        "-b:a", "192k",
        "-shortest",
        ruta_salida
    ]
    try:
        subprocess.run(comando, check=True, capture_output=True, text=True)
        return jsonify({'video_path': ruta_salida}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': f'Error al ejecutar FFmpeg: {e.stderr}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)