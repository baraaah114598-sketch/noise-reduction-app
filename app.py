import streamlit as st
import torch
from df.enhance import enhance, init_df, load_audio, save_audio
import tempfile
import os

# Initialize DeepFilterNet model
model, df_state, _ = init_df()

st.set_page_config(page_title="🎧 AI Noise Reducer", layout="centered")
st.title("🎧 AI-Powered Noise Reduction")
st.markdown("Upload a WAV file and remove background noise instantly.")

uploaded_file = st.file_uploader("Choose an audio file", type=["wav"])

if uploaded_file is not None:
    with st.spinner("Processing your audio... ⏳"):
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        # Load and enhance
        audio, _ = load_audio(tmp_file_path, sr=df_state.sr())
        enhanced_audio = enhance(model, df_state, audio)

        # Save output
        enhanced_file_path = os.path.join(tempfile.gettempdir(), "enhanced_audio.wav")
        save_audio(enhanced_file_path, enhanced_audio, df_state.sr())

        st.success("✅ Done! Listen & download below:")
        st.audio(enhanced_file_path, format="audio/wav")
        st.download_button("⬇️ Download Enhanced Audio", enhanced_file_path)
