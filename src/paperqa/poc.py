import os

from llmclient import CommonLLMNames
from paperqa import Docs, Settings, ask
from dotenv import load_dotenv

load_dotenv()

# Examples of different cancer types to query
CANCER_TYPES = [
    "breast cancer",
    "lung cancer",
    "prostate cancer",
    "melanoma",
    "leukemia"
]

def main():

    settings = Settings(
        llm="claude-3-5-sonnet-20241022", summary_llm="claude-3-5-sonnet-20241022",
        embedding="st-multi-qa-MiniLM-L6-cos-v1",
        verbosity=3,
        disable_check=True
    )

    # Create query about the specific cancer type
    cancer_type = "breast cancer"
    query_text = f"What are the latest treatment approaches and clinical trials for {cancer_type}?"
    query_text = "What manufacturing challenges are unique to bispecific antibodies?"

    answer_response = ask(
        query=query_text,
        settings=settings,
        disable_check=True
    )
    print(answer_response)

    # Query for breast cancer as an example



if __name__ == "__main__":
    main()