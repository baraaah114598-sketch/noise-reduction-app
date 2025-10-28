import streamlit as st
import noisereduce as nr
import librosa
import soundfile as sf
import tempfile
from pydub import AudioSegment
import os

st.set_page_config(page_title="🎧 Noise Reducer & Voice Isolator", layout="centered")

st.title("🎧 Noise Reduction & Voice Isolation App")
st.markdown("Upload an audio file and remove background noise or isolate vocals.")

uploaded_file = st.file_uploader("Upload your audio file", type=["wav", "mp3"])
voice_isolation = st.checkbox("🎙️ Enable Voice Isolation (Experimental - slower)")

if uploaded_file is not None:
    with st.spinner("Processing your audio..."):
        # Save input as a temporary .wav
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio = AudioSegment.from_file(uploaded_file)
        audio.export(temp_input.name, format="wav")

        # Load with librosa
        y, sr = librosa.load(temp_input.name, sr=None)

        # Step 1: Noise Reduction
        noise_part = y[0:int(sr * 1)]  # assume first 1 sec is noise
        reduced = nr.reduce_noise(y=y, y_noise=noise_part, sr=sr)

        # Step 2 (optional): Voice Isolation
        if voice_isolation:
            try:
                from spleeter.separator import Separator
                separator = Separator("spleeter:2stems")
                output_dir = tempfile.mkdtemp()
                separator.separate_to_file(temp_input.name, output_dir)
                vocals_path = os.path.join(output_dir, "input", "vocals.wav")
                y, sr = librosa.load(vocals_path, sr=None)
                reduced = nr.reduce_noise(y=y, y_noise=noise_part, sr=sr)
            except Exception as e:
                st.warning("Voice isolation failed. Make sure Spleeter is installed.")
                st.error(e)

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
