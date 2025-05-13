from flask import Flask, request, jsonify
import whisper
import yt_dlp
import os
import uuid

app = Flask(__name__)
model = whisper.load_model("base")  # Usa "medium" o "large" si tienes más memoria

def descargar_audio(video_url, output_path):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

@app.route("/transcribir", methods=["POST"])
def transcribir():
    data = request.get_json()
    video_url = data.get("url")

    if not video_url:
        return jsonify({"error": "Falta el campo 'url'"}), 400

    audio_file = f"/tmp/{uuid.uuid4()}.mp3"

    try:
        descargar_audio(video_url, audio_file)
        result = model.transcribe(audio_file)
        os.remove(audio_file)
        return jsonify({"text": result["text"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ===== HEALTH CHECK =====
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "engine": "gTTS", "language": LANG})

# ===== MAIN =====
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
