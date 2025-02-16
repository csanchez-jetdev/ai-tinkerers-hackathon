from smolagents import ToolCallingAgent, LiteLLMModel, tool
from typing import List, Dict, Optional
from pydantic import BaseModel
import yaml
import importlib.resources
import json
from dotenv import load_dotenv
import os

load_dotenv()

CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')

class ConversationSummary(BaseModel):
    main_complaint: str
    key_points: List[str]
    doctor_recommendations: List[str]
    follow_up: Optional[str] = None

# Configure the model
model = LiteLLMModel(
    model_id="claude-3-5-sonnet-20241022",
    api_key=CLAUDE_API_KEY
)


# Créer des templates de prompt personnalisés pour l'agent de résumé de conversation
summary_system_prompt = (
    "You are a medical conversation summarizer specializing in:\n"
    "1. Extracting key points from doctor-patient conversations\n"
    "2. Identifying main patient complaints and doctor's recommendations\n"
    "3. Noting important follow-up information\n\n"

    "Strictly format your output according to the ConversationSummary schema with clear, concise points. Don't add new keys to the dictionnary."
)

# Charger les templates de prompt par défaut et remplacer le prompt système pour l'agent de résumé
default_summary_templates = yaml.safe_load(
    importlib.resources.files("smolagents.prompts").joinpath("toolcalling_agent.yaml").read_text()
)
default_summary_templates["system"] = summary_system_prompt


# Agent 2: Conversation Summary Agent (on conserve l'usage du tool)
@tool
def summarize_medical_conversation(transcript: str) -> Dict:
    """
    Creates a structured summary of a doctor-patient conversation.
    Args:
        transcript: The medical conversation transcript
    Returns:
        Dictionary containing the conversation summary
    """
    # Implémenter la logique de résumé ici
    pass

summary_agent = ToolCallingAgent(
    tools=[summarize_medical_conversation],
    model=model,
    prompt_templates=default_summary_templates,
)


def get_conversation_summary(transcript: str) -> ConversationSummary:
    """Obtenir le résumé structuré de la conversation."""
    result = summary_agent.run(f"""
    Provide a concise one-paragraph summary of this medical conversation. 
    Focus on the key points: main complaint, findings, and treatment plan.
    Return the summary as a JSON object in this format:
    {{
        "summary": "<your one-paragraph summary here>"
    }}

    Based on this medical transcript:
    {transcript}
    """)
    
    try:
        # Convertir le texte en dictionnaire
        result_dict = json.loads(str(result))
        return ConversationSummary(**result_dict)
    except (json.JSONDecodeError, ValueError) as e:
        # Si le parsing échoue, créer un résultat par défaut
        return ConversationSummary(
            main_complaint="Not specified",
            key_points=[],
            doctor_recommendations=[],
            follow_up=None
        )
