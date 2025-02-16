from dotenv import load_dotenv
import os
from typing import Optional
from pathlib import Path
from huggingface_hub import InferenceClient
from smolagents import Tool
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
    language: Optional[str] = None
    duration: Optional[float] = None

class AudioTranscriptionError(Exception):
    """Custom exception for audio transcription errors"""
    pass

class SpeechRecognitionService:
    """Service class for handling speech recognition operations using Whisper"""

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

    async def transcribe(self, file_path: str) -> Transcription:
        """
        Transcribe audio file to text using Whisper

        Args:
            file_path: Path to the audio file

        Returns:
            Transcription object containing the results

        Raises:
            AudioTranscriptionError: If transcription fails
            FileNotFoundError: If audio file is not found
            ValueError: If audio format is not supported
        """
        try:
            path = self.validate_audio_file(file_path)

            logger.info(f"Starting transcription of {path.name} using Whisper")

            response = self.client.automatic_speech_recognition(
                audio=path,
                model=self.config.model_name
            )

            text = response.text
            language = None
            duration = None

            logger.success(f"Successfully transcribed {path.name}")

            return Transcription(
                text=text,
                language=language,
                duration=duration
            )

        except Exception as e:
            logger.exception(f"Transcription failed: {str(e)}")
            raise AudioTranscriptionError(f"Failed to transcribe audio: {str(e)}") from e

class SpeechRecognitionTool(Tool):
    """Tool for speech recognition using Whisper through HuggingFace"""

    name = "speech_recognition"
    description = "Uses Whisper model to extract text from an audio file."
    inputs = {
        "file_path": {
            "type": "string",
            "description": "The path to the audio file to be processed.",
        }
    }
    output_type = "object"  # Changed from Transcription class to string type
    output_description = "A transcription object containing the extracted text, language, and duration"

    def __init__(self, config: Optional[TranscriptionConfig] = None, **kwargs):
        super().__init__(**kwargs)
        self.service = SpeechRecognitionService(config)

    async def forward(
        self,
        file_path: str,
    ) -> Transcription:
        """
        Process the audio file and return transcription

        Args:
            file_path: Path to the audio file

        Returns:
            Transcription object containing the results
        """
        return await self.service.transcribe(file_path)

async def main():
    config = TranscriptionConfig(
        model_name="openai/whisper-large-v3-turbo",
    )

    tool = SpeechRecognitionTool(config=config)
    result = await tool.forward("./src/extract/sources/medecin.mp3")
    print(f"Transcription: {result.text}")

if __name__ == "__main__":
    asyncio.run(main())