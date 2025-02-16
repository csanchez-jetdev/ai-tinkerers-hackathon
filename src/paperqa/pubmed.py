from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from Bio import Entrez
import json

@dataclass
class Paper:
    """Simple structure for paper information"""
    title: str
    authors: List[str]
    abstract: str
    journal: str
    publication_date: str
    pmid: str
    doi: Optional[str]
    url: str

class ResearchAgent:
    """Simple agent for searching and organizing research papers from PubMed"""

    def __init__(self, email: str):
        """
        Initialize the research agent

        Args:
            email: Email address for PubMed API access
        """
        self.email = email
        Entrez.email = email

    def search_papers(
        self,
        query: str,
        max_results: int = 10,
        date_from: str = None,
        date_to: str = None
    ) -> List[Paper]:
        """
        Search for papers matching the query

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            date_from: Start date in YYYY/MM/DD format
            date_to: End date in YYYY/MM/DD format

        Returns:
            List of Paper objects
        """
        # Add date restriction if specified
        if date_from and date_to:
            query += f" AND {date_from}:{date_to}[dp]"

        # Search PubMed
        search_handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="relevance"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()

        if not search_results["IdList"]:
            return []

        # Fetch paper details
        papers = []
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=search_results["IdList"],
            rettype="xml"
        )
        records = Entrez.read(fetch_handle)["PubmedArticle"]
        fetch_handle.close()

        # Process each paper
        for record in records:
            try:
                article = record["MedlineCitation"]["Article"]

                # Get authors
                authors = []
                if "AuthorList" in article:
                    for author in article["AuthorList"]:
                        if "LastName" in author and "ForeName" in author:
                            authors.append(f"{author['LastName']} {author['ForeName']}")

                # Get DOI
                doi = None
                if "ELocationID" in article:
                    for id in article["ELocationID"]:
                        if id.attributes["EIdType"] == "doi":
                            doi = str(id)

                # Create Paper object
                paper = Paper(
                    title=article["ArticleTitle"],
                    authors=authors,
                    abstract=self._get_abstract(article),
                    journal=article["Journal"]["Title"],
                    publication_date=self._get_publication_date(article),
                    pmid=record["MedlineCitation"]["PMID"],
                    doi=doi,
                    url=f"https://pubmed.ncbi.nlm.nih.gov/{record['MedlineCitation']['PMID']}/"
                )
                papers.append(paper)

            except KeyError as e:
                print(f"Warning: Skipping paper due to missing data: {e}")
                continue

        return papers

    def _get_abstract(self, article: Dict) -> str:
        """Extract abstract from article data"""
        if "Abstract" in article and "AbstractText" in article["Abstract"]:
            abstract_parts = []
            for part in article["Abstract"]["AbstractText"]:
                if hasattr(part, "attributes") and "Label" in part.attributes:
                    abstract_parts.append(f"{part.attributes['Label']}: {str(part)}")
                else:
                    abstract_parts.append(str(part))
            return "\n".join(abstract_parts)
        return "Abstract not available"

    def _get_publication_date(self, article: Dict) -> str:
        """Extract publication date from article data"""
        try:
            pub_date = article["Journal"]["JournalIssue"]["PubDate"]
            if "Year" in pub_date:
                month = pub_date.get("Month", "01")
                day = pub_date.get("Day", "01")
                return f"{pub_date['Year']}/{month}/{day}"
        except KeyError:
            pass
        return "Date not available"

    def save_results(
        self,
        papers: List[Paper],
        output_dir: str = "research_results",
        format: str = "json"
    ) -> None:
        """
        Save search results to files

        Args:
            papers: List of Paper objects
            output_dir: Directory to save results
            format: Output format ('json' or 'txt')
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            # Save as JSON
            output_file = output_path / f"papers_{timestamp}.json"
            papers_dict = [vars(paper) for paper in papers]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(papers_dict, f, indent=2)

        else:
            # Save as formatted text
            output_file = output_path / f"papers_{timestamp}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                for paper in papers:
                    f.write(f"Title: {paper.title}\n")
                    f.write(f"Authors: {', '.join(paper.authors)}\n")
                    f.write(f"Journal: {paper.journal}\n")
                    f.write(f"Publication Date: {paper.publication_date}\n")
                    f.write(f"PMID: {paper.pmid}\n")
                    if paper.doi:
                        f.write(f"DOI: {paper.doi}\n")
                    f.write(f"URL: {paper.url}\n")
                    f.write(f"Abstract:\n{paper.abstract}\n")
                    f.write("\n" + "="*80 + "\n\n")

# Example usage
if __name__ == "__main__":
    agent = ResearchAgent(email="clement.sanchez@jetdev.fr")

    # Search for papers
    papers = agent.search_papers(
        query="CRISPR gene editing cancer therapy",
        max_results=5,
        date_from="2023/01/01",
        date_to="2024/12/31"
    )

    # Save results
    agent.save_results(papers, format="json")
    agent.save_results(papers, format="txt")