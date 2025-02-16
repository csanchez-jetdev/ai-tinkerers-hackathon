from dotenv import load_dotenv
import os
from typing import Optional
from pathlib import Path
from huggingface_hub import InferenceClient
from pydantic import BaseModel, Field
from loguru import logger
import asyncio

load_dotenv()

class TranscriptionConfig(BaseModel):
    """Configuration settings for speech recognition"""
    model_name: str = Field(
        default="openai/whisper-large-v3",
        description="HuggingFace Whisper model to use for speech recognition"
    )

class Transcription(BaseModel):
    """Model for transcription results"""
    text: str

class AudioTranscriptionError(Exception):
    """Custom exception for audio transcription errors"""
    pass

class AudioPreprocessor:
    """Service class for preprocessing audio files using speech recognition"""

    def __init__(self, config: Optional[TranscriptionConfig] = None):
        self.api_key = os.getenv('HUGGING_FACE_API_KEY')
        if not self.api_key:
            raise ValueError("HUGGING_FACE_API_KEY environment variable is not set")

        self.config = config or TranscriptionConfig()
        self.client = InferenceClient(api_key=self.api_key)

    def validate_audio_file(self, file_path: str) -> Path:
        """Validate the audio file exists and is accessible"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        supported_extensions = {'.mp3', '.wav', '.ogg', '.flac', '.m4a', '.webm'}
        if path.suffix.lower() not in supported_extensions:
            raise ValueError(f"Unsupported audio format. Supported formats: {supported_extensions}")

        return path

    async def process_audio(self, file_path: str) -> str:
        """
        Preprocess audio file by transcribing it to text

        Args:
            file_path: Path to the audio file

        Returns:
            str: Transcribed text from the audio file

        Raises:
            AudioTranscriptionError: If transcription fails
            FileNotFoundError: If audio file is not found
            ValueError: If audio format is not supported
        """
        try:
            path = self.validate_audio_file(file_path)
            logger.info(f"Preprocessing audio file: {path.name}")

            response = self.client.automatic_speech_recognition(
                audio=path,
                model=self.config.model_name
            )

            logger.success(f"Successfully transcribed {path.name}")
            return response.text

        except Exception as e:
            logger.exception(f"Audio preprocessing failed: {str(e)}")
            raise AudioTranscriptionError(f"Failed to preprocess audio: {str(e)}") from e

async def process_audio_files(file_paths: list[str], config: Optional[TranscriptionConfig] = None) -> dict[str, str]:
    """
    Process multiple audio files in parallel

    Args:
        file_paths: List of paths to audio files
        config: Optional configuration for the preprocessor

    Returns:
        dict: Mapping of file paths to their transcribed text
    """
    preprocessor = AudioPreprocessor(config)
    tasks = [preprocessor.process_audio(file_path) for file_path in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return {
        file_path: result if not isinstance(result, Exception) else str(result)
        for file_path, result in zip(file_paths, results)
    }

async def main():
    # Example usage
    config = TranscriptionConfig(
        model_name="openai/whisper-large-v3-turbo",
    )

    files_to_process = ["./src/extract/sources/medecin.mp3"]
    results = await process_audio_files(files_to_process, config)

    for file_path, text in results.items():
        logger.debug(f"File: {file_path}")
        logger.info(f"Transcription: {text}\n")

if __name__ == "__main__":
    asyncio.run(main())