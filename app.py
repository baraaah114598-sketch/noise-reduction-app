import streamlit as st
import noisereduce as nr
import librosa
import soundfile as sf
import tempfile
from pydub import AudioSegment
from pydub.utils import which
import os
import subprocess

# ---------------------------
# Ensure ffmpeg & ffprobe exist (for Streamlit Cloud)
# ---------------------------
if which("ffmpeg") is None or which("ffprobe") is None:
    try:
        st.info("Installing ffmpeg (first run only)... please wait ⏳")
        subprocess.run(["apt-get", "update"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["apt-get", "install", "-y", "ffmpeg"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        st.error(f"FFmpeg install failed: {e}")

# Set ffmpeg path for pydub
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

# ---------------------------
# Streamlit App UI
# ---------------------------
st.set_page_config(page_title="🎧 Noise Reducer", layout="centered")

st.title("🎧 Noise Reduction App")
st.markdown("Upload an audio file to automatically remove background noise.")

uploaded_file = st.file_uploader("Upload your audio file", type=["wav", "mp3"])

if uploaded_file is not None:
    with st.spinner("Processing your audio... please wait ⏳"):
        try:
            # Save uploaded file temporarily
            temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            audio = AudioSegment.from_file(uploaded_file)
            audio.export(temp_input.name, format="wav")

            # Load and reduce noise
            y, sr = librosa.load(temp_input.name, sr=None)
            noise_sample = y[0:int(sr * 1)]  # first 1 sec = noise profile
            reduced = nr.reduce_noise(y=y, y_noise=noise_sample, sr=sr)

            # Save cleaned output
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            sf.write(temp_output.name, reduced, sr)

            st.success("✅ Done! Listen below:")
            st.audio(temp_output.name)
            st.download_button(
                "⬇️ Download Cleaned Audio",
                open(temp_output.name, "rb"),
                file_name="cleaned_audio.wav",
            )

        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.info("Tip: Try uploading a WAV file if MP3 fails.")
