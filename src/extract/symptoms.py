import os

from smolagents import CodeAgent, LiteLLMModel
from typing import  Optional
from pydantic import BaseModel
import yaml
import importlib.resources
from dotenv import load_dotenv

load_dotenv()

CLAUDE_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Shared data models
class Symptom(BaseModel):
    description: str
    severity: Optional[str] = None
    duration: Optional[str] = None

# Configure the model
model = LiteLLMModel(
    model_id="claude-3-5-sonnet-20241022",
    api_key=CLAUDE_API_KEY
)

# Créer des templates de prompt personnalisés pour l'analyse diagnostique
diagnostic_system_prompt = (
    "You are a medical diagnostic analyzer specializing in:\n"
    "1. Extracting symptoms from a medical transcript\n"
    "2. Identifying the disease(s) from which the patient may be suffering.\n"
    "3. Providing confidence levels for your analysis.\n\n"
    "Always format your output according to the MedicalAnalysis schema with proper symptoms detailing."
)

# Charger les templates de prompt par défaut et remplacer le prompt système
default_prompt_templates = yaml.safe_load(
    importlib.resources.files("smolagents.prompts").joinpath("toolcalling_agent.yaml").read_text()
)
default_prompt_templates["system"] = diagnostic_system_prompt

# Agent 1: Medical Diagnostic Agent (sans outil, on utilise directement le prompt)
diagnostic_agent = CodeAgent(
    tools=[],  # On fournit une liste vide puisque nous n'utilisons pas d'outil spécifique
    model=model,
    prompt_templates=default_prompt_templates,
)