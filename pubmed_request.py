from Bio import Entrez
import pandas as pd

# Настройки для Entrez
Entrez.email = "liza.fedortsova.2004@gmail.com"  # Обязательно укажите свой email
API_KEY = "Y8ea35688214338214ed27aa45bbac927ff08"  # Для увеличения лимита запросов

# Шаг 1: Поиск публикаций по MeSH-терминам
def search_pubmed(query, retmax=1000):
    handle = Entrez.esearch(db="pubmed", 
                          term=query, 
                          retmax=retmax,
                          api_key=API_KEY)
    results = Entrez.read(handle)
    handle.close()
    return results["IdList"]

# Шаг 2: Получение полных данных статей
def fetch_articles(pmids):
    handle = Entrez.efetch(db="pubmed",
                          id=",".join(pmids),
                          rettype="medline",
                          retmode="text",
                          api_key=API_KEY)
    data = handle.read()
    handle.close()
    return data

# Основные запросы
hh_query = """
((MYC OR "c-Myc" OR "MYC protein" OR "MYC targets") 
AND ("target" OR "regulation" OR "binding" OR "activation" OR "repression")) 
AND ("Protein Interaction Maps"[Mesh] OR "Protein Binding"[Mesh])
AND ("Neoplasms"[Mesh] OR "Neoplastic Processes"[Mesh])
NOT ("Review"[Publication Type] OR "Case Reports"[Publication Type])
"""

# Выполнение поиска
pmids = search_pubmed(hh_query)
articles_data = fetch_articles(pmids[:100])  # Ограничение для примера

# Сохранение результатов
with open("hh_interactions_articles.txt", "w", encoding="utf-8") as f:
    f.write(articles_data)

print(f"Получено {len(pmids)} статей. Первые 100 сохранены.")