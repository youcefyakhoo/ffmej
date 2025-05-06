from flask import Flask, request, send_file, jsonify
import os
import subprocess
import tempfile

app = Flask(__name__)

# Ruta para renderizar el video
@app.route('/render', methods=['POST'])
def render_video():
    # Obtener datos de la solicitud
    data = request.json
    ruta_imagen = data.get("ruta_imagen")
    ruta_salida = data.get("ruta_salida")

    # Validar que se proporcionó una imagen
    if not ruta_imagen:
        return jsonify({"error": "Se necesita una URL de imagen"}), 400
    
    # Crear un archivo temporal para el video generado
    output_video_path = "/tmp/" + ruta_salida

    # Ejecutar FFmpeg para crear el video a partir de la imagen
    try:
        # Ejecutar FFmpeg para generar el video de 5 segundos
        subprocess.run([
            'ffmpeg', '-y', '-loop', '1', '-framerate', '25', '-t', '5', '-i', ruta_imagen,
            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-t', '5', output_video_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Error al ejecutar FFmpeg", "details": str(e)}), 500

    # Verificar si el archivo fue generado correctamente
    if not os.path.exists(output_video_path):
        return jsonify({"error": "No se pudo generar el video"}), 500

    # Enviar el archivo de video como respuesta para su descarga
    return send_file(output_video_path, as_attachment=True, download_name=ruta_salida, mimetype='video/mp4')
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)




