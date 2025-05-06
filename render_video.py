import subprocess
import sys
import os

def render_video(ruta_imagen, ruta_audio, ruta_salida):
    if not os.path.exists(ruta_imagen):
        print(f"Error: No se encontró la imagen: {ruta_imagen}")
        return 1  # Código de error
    if not os.path.exists(ruta_audio):
        print(f"Error: No se encontró el audio: {ruta_audio}")
        return 1  # Código de error

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
        print(f"Video generado en: {ruta_salida}")
        return 0  # Código de éxito
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar FFmpeg: {e.stderr}")
        return e.returncode

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python render_video.py <ruta_imagen> <ruta_audio> <ruta_salida>")
        sys.exit(1)

    ruta_imagen = sys.argv[1]
    ruta_audio = sys.argv[2]
    ruta_salida = sys.argv[3]

    exit_code = render_video(ruta_imagen, ruta_audio, ruta_salida)
    sys.exit(exit_code)


