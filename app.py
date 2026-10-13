import os
import json
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from sarvamai import SarvamAI

# --------------------------------------------------
# 1. LOAD CONFIGURATION
# --------------------------------------------------

load_dotenv()

API_KEY = os.getenv("SARVAM_API_KEY")

st.set_page_config(
    page_title="VoiceNote AI",
    page_icon="🎙️",
    layout="centered"
)

LANGUAGES = {
    "Auto-detect language": "unknown",
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Tamil": "ta-IN",
}

# Store results across Streamlit reruns
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "timestamps" not in st.session_state:
    st.session_state.timestamps = {}

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "uploaded_signature" not in st.session_state:
    st.session_state.uploaded_signature = None


# --------------------------------------------------
# 2. PAGE INTERFACE
# --------------------------------------------------

st.title("🎙️ VoiceNote AI")
st.write("Convert audio into text with timestamps and AI summaries.")

st.divider()

selected_language = st.selectbox(
    "Choose the audio language",
    list(LANGUAGES.keys())
)

show_timestamps = st.checkbox(
    "Include sentence/phrase timestamps",
    value=True
)

uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["mp3", "wav", "m4a", "aac", "flac", "ogg", "mp4", "webm"]
)


# --------------------------------------------------
# 3. HANDLE UPLOADED FILE
# --------------------------------------------------

if uploaded_file is not None:

    st.audio(uploaded_file)

    st.write(
        f"**File:** {uploaded_file.name}  \n"
        f"**Size:** {uploaded_file.size / (1024 * 1024):.2f} MB"
    )

    # Reset old results when a different file is uploaded
    signature = f"{uploaded_file.name}:{uploaded_file.size}"

    if st.session_state.uploaded_signature != signature:
        st.session_state.transcript = ""
        st.session_state.timestamps = {}
        st.session_state.summary = ""
        st.session_state.uploaded_signature = signature

    # --------------------------------------------------
    # 4. TRANSCRIBE AUDIO USING SARVAM BATCH API
    # --------------------------------------------------

    if st.button("Transcribe Audio", type="primary"):

        if not API_KEY or not API_KEY.strip():
            st.error(
                "API key not found. Check your .env file "
                "for SARVAM_API_KEY."
            )

        else:
            temp_path = None
            output_dir = None

            try:
                client = SarvamAI(
                    api_subscription_key=API_KEY
                )

                extension = Path(uploaded_file.name).suffix or ".mp3"

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=extension
                ) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name

                with st.spinner("Uploading audio to Sarvam AI..."):

                    job = client.speech_to_text_job.create_job(
                        model="saaras:v4",
                        mode="transcribe",
                        language_code=LANGUAGES[selected_language],
                        with_timestamps=show_timestamps
                    )

                    job.upload_files(file_paths=[temp_path])
                    job.start()

                with st.spinner(
                    "Transcribing audio. This may take a few minutes..."
                ):
                    job.wait_until_complete(
                        poll_interval=5,
                        timeout=1800
                    )

                file_results = job.get_file_results()

                failed_files = file_results.get("failed", [])
                successful_files = file_results.get("successful", [])

                if failed_files:
                    st.error("Sarvam could not transcribe the file.")

                    for failed in failed_files:
                        st.write(
                            failed.get("error_message", str(failed))
                        )

                elif not successful_files:
                    st.error("No successful transcription result was returned.")

                else:
                    output_dir = tempfile.mkdtemp(
                        prefix="voicenote_output_"
                    )

                    job.download_outputs(output_dir=output_dir)

                    json_files = list(
                        Path(output_dir).glob("*.json")
                    )

                    if not json_files:
                        st.error("No JSON transcription result was found.")

                    else:
                        with open(
                            json_files[0],
                            "r",
                            encoding="utf-8"
                        ) as result_file:
                            result = json.load(result_file)

                        # Save results so they survive Streamlit reruns
                        st.session_state.transcript = (
                            result.get("transcript", "")
                        )

                        st.session_state.timestamps = (
                            result.get("timestamps") or {}
                        )

                        st.session_state.summary = ""

                        if st.session_state.transcript:
                            st.success("Transcription completed!")
                        else:
                            st.warning(
                                "The result did not contain a transcript. "
                                "Check the raw API result below."
                            )

                        with st.expander("View raw API result"):
                            st.json(result)

            except Exception as error:
                st.error("Transcription failed.")
                st.code(str(error))

            finally:
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass


# --------------------------------------------------
# 5. DISPLAY TRANSCRIPT
# --------------------------------------------------

transcript = st.session_state.transcript

if transcript:

    st.divider()
    st.subheader("📝 Transcription")

    st.text_area(
        "Recognized text",
        value=transcript,
        height=250,
        key="transcript_display"
    )

    st.download_button(
        "Download Transcript (.txt)",
        data=transcript,
        file_name="transcription.txt",
        mime="text/plain"
    )

    # --------------------------------------------------
    # 6. LLM-POWERED AI SUMMARY
    # --------------------------------------------------

    st.divider()
    st.subheader("✨ AI Summary")

    st.write(
        "Generate a concise summary of your audio transcript "
        "using Sarvam's large language model."
    )

    if st.button("Generate AI Summary", type="primary"):

        if not API_KEY or not API_KEY.strip():
            st.error("Sarvam API key not found in .env.")

        else:
            try:
                client = SarvamAI(
                    api_subscription_key=API_KEY
                )

                with st.spinner("The LLM is summarizing your transcript..."):

                    response = client.chat.completions(
                        model="sarvam-105b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You are a helpful summarization assistant. "
                                    "Summarize the transcript accurately. "
                                    "Preserve the important facts, names, "
                                    "decisions, and conclusions. "
                                    "Do not invent information. "
                                    "If part of the transcript is unclear, "
                                    "do not guess what was said."
                                )
                            },
                            {
                                "role": "user",
                                "content": (
                                    "Summarize the following audio transcript. "
                                    "Use a clear structure with a short overview, "
                                    "main points in bullet form, and a conclusion. "
                                    "Keep the summary concise but informative.\n\n"
                                    + transcript
                                )
                            }
                        ],
                        temperature=0.2,
                        max_tokens=1500,
                        reasoning_effort=None
                    )

                    summary = (
                        response.choices[0].message.content or ""
                    ).strip()

                    st.session_state.summary = summary

                if summary:
                    st.success("AI summary generated!")
                else:
                    st.warning("The LLM returned an empty summary.")

            except Exception as error:
                st.error("AI summary generation failed.")
                st.code(str(error))

    # Show a previously generated summary after reruns
    if st.session_state.summary:

        st.markdown("### Summary")

        st.markdown(st.session_state.summary)

        st.download_button(
            "Download AI Summary (.txt)",
            data=st.session_state.summary,
            file_name="audio_summary.txt",
            mime="text/plain",
            key="download_summary"
        )

    # --------------------------------------------------
    # 7. DISPLAY SENTENCE/PHRASE TIMESTAMPS
    # --------------------------------------------------

    if show_timestamps:

        st.divider()
        st.subheader("⏱️ Sentence/Phrase Timestamps")

        timestamps = st.session_state.timestamps or {}

        if isinstance(timestamps, dict):

            entries = timestamps.get("entries", [])

            if entries:
                for entry in entries:
                    start = entry.get("start_time_seconds")
                    end = entry.get("end_time_seconds")
                    text = entry.get("transcript", "")

                    if start is not None and end is not None:
                        st.write(
                            f"**{float(start):.2f}s – "
                            f"{float(end):.2f}s:** {text}"
                        )
                    elif text:
                        st.write(text)

            else:
                chunks = (
                    timestamps.get("chunks")
                    or timestamps.get("words")
                    or []
                )

                starts = timestamps.get("start_time_seconds", [])
                ends = timestamps.get("end_time_seconds", [])

                if chunks and starts and ends:
                    for chunk, start, end in zip(chunks, starts, ends):
                        st.write(
                            f"**{float(start):.2f}s – "
                            f"{float(end):.2f}s:** {chunk}"
                        )
                else:
                    st.info(
                        "No separate timestamp entries were found "
                        "in the returned result."
                    )

        elif isinstance(timestamps, list) and timestamps:
            for entry in timestamps:
                st.write(entry)

        else:
            st.info(
                "No timestamp data was returned for this recording."
            )

else:
    st.info("Upload an audio file and click Transcribe Audio to begin.")


# --------------------------------------------------
# 8. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "VoiceNote AI | Powered by Sarvam AI | "
    "Speech-to-Text + LLM Summarization"
)
