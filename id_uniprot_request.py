import requests
from typing import List, Dict, Optional, Union, Any
from typing_extensions import TypedDict

# Конфигурация (замените на свои данные)
UNIPROT_EMAIL = "liza.fedortsova.2004@gmail.com"
UNIPROT_API_KEY = "Y8ea35688214338214ed27aa45bbac927ff08"
OUTPUT_FILE = "uniprot_results.txt"


class ProteinResult(TypedDict):
    primaryAccession: str
    proteinDescription: Dict[str, Any]


def search_proteins(
    protein_names: List[str]
) -> Dict[str, Optional[str]]:
    """Поиск белков с использованием API UniProt."""
    results: Dict[str, Optional[str]] = {}
    base_url = "https://www.uniprot.org/uniprotkb/search"
    
    for name in protein_names:
        params: Dict[str, Union[str, int]] = {
            "query": (
                f'name:"{name}" AND '
                'organism:"Homo sapiens"'
            ),
            "format": "json",
            "fields": "accession,protein_name",
            "size": 1
        }
        
        headers: Dict[str, str] = {
            "User-Agent": (
                f"PythonUniProtBot/1.0 "
                f"({UNIPROT_EMAIL})"
            ),
            "From": UNIPROT_EMAIL,
            "Authorization": f"Bearer {UNIPROT_API_KEY}"
        }
        
        try:
            response = requests.get(
                base_url,
                params=params,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                protein: ProteinResult = data["results"][0]
                protein_id = protein["primaryAccession"]
                desc = protein["proteinDescription"]
                name_value = (
                    desc.get("recommendedName", {})
                    .get("fullName", {})
                    .get("value", "")
                )
                if protein_id and name_value:
                    results[name] = f"{protein_id}\t{name_value}"
                else:
                    results[name] = None
            else:
                results[name] = None
                
        except Exception as e:
            print(f"Ошибка при поиске {name}: {e}")
            results[name] = None
            
    return results


def save_results(results: Dict[str, Optional[str]]) -> None:
    """Сохраняет результаты в текстовый файл."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for protein, result in results.items():
            if result is not None:
                f.write(f"{result}\n")


if __name__ == "__main__":
    PROTEINS = [
        "insulin", 
        "myc", 
        "hemoglobin", 
        "actin", 
        "p53"
    ]
    
    search_results = search_proteins(PROTEINS)
    save_results(search_results)
    
    print(f"Результаты сохранены в {OUTPUT_FILE}")
    print(
        f"Использован API ключ: "
        f"{UNIPROT_API_KEY[:5]}...{UNIPROT_API_KEY[-5:]}"
    )
    print(f"Email: {UNIPROT_EMAIL}")