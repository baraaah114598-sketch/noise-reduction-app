import streamlit as st
import noisereduce as nr
import librosa
import soundfile as sf
import tempfile
from pydub import AudioSegment
from pydub.utils import which
import os

# Fix ffmpeg path for Streamlit Cloud
AudioSegment.converter = which("ffmpeg")

st.set_page_config(page_title="🎧 Noise Reducer", layout="centered")

st.title("🎧 Noise Reduction App")
st.markdown("Upload an audio file to remove background noise.")

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
            noise_sample = y[0:int(sr * 1)]  # First 1 second = noise sample
            reduced = nr.reduce_noise(y=y, y_noise=noise_sample, sr=sr)

            # Save output
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

