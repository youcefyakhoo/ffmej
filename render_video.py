from flask import Flask, request, send_file, jsonify
import os
import subprocess
import tempfile
import requests

app = Flask(__name__)

@app.route('/render', methods=['POST'])
def render_video():
    data = request.json
    ruta_imagen = data.get("ruta_imagen")  # Puede ser None
    ruta_audio = data.get("ruta_audio")    # Ahora obligatorio
    ruta_salida = data.get("ruta_salida", "output.mp4")

    if not ruta_audio:
        return jsonify({"error": "Se necesita una URL de audio"}), 400

    # Crear archivo temporal para video
    output_video_path = os.path.join("/tmp", ruta_salida)

    # Si no hay imagen, usar fondo negro como dummy
    if not ruta_imagen:
        dummy_img_path = os.path.join("/tmp", "black.png")
        subprocess.run([
            "convert", "-size", "1280x720", "xc:black", dummy_img_path
        ])
        ruta_imagen = dummy_img_path

    try:
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-framerate', '25', '-i', ruta_imagen,
            '-i', ruta_audio, '-shortest',
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k',
            output_video_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Error al ejecutar FFmpeg", "details": str(e)}), 500

    if not os.path.exists(output_video_path):
        return jsonify({"error": "No se pudo generar el video"}), 500

    return send_file(output_video_path, as_attachment=True, download_name=ruta_salida, mimetype='video/mp4')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
