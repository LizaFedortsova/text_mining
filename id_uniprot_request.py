import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Кеш для уже найденных ID
UNIPROT_CACHE = {}

def get_uniprot_id(gene_symbol):
    """Получаем UniProt ID для гена с обработкой ошибок"""
    if gene_symbol in UNIPROT_CACHE:
        return UNIPROT_CACHE[gene_symbol]
    
    # Пропускаем строки, которые явно не являются названиями белков
    if gene_symbol.startswith(('HALLMARK_', 'http://', 'https://')):
        UNIPROT_CACHE[gene_symbol] = "Skipped"
        return "Skipped"
    
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"gene:{gene_symbol} AND organism_id:9606",
        "format": "json",
        "fields": "accession,gene_names",
        "size": 1
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data['results']:
            uniprot_id = data['results'][0]['primaryAccession']
            UNIPROT_CACHE[gene_symbol] = uniprot_id
            return uniprot_id
        
    except Exception as e:
        print(f"Ошибка для {gene_symbol}: {str(e)}")
    
    UNIPROT_CACHE[gene_symbol] = "Not found"
    return "Not found"

def process_genes_from_file(filename):
    """Читаем гены из файла и обрабатываем их"""
    with open(filename, 'r', encoding='utf-8') as f:
        # Читаем все строки, удаляем пустые и разделяем по пробелам/табам
        genes = []
        for line in f:
            line = line.strip()
            if line:  # Пропускаем пустые строки
                # Разделяем строку на отдельные элементы
                genes.extend(line.split())
    
    print(f"Найдено {len(genes)} элементов для обработки")
    
    # Удаляем дубликаты, сохраняя порядок
    seen = set()
    unique_genes = [g for g in genes if not (g in seen or seen.add(g))]
    print(f"После удаления дубликатов осталось {len(unique_genes)} уникальных элементов")
    
    return genes, unique_genes

def save_aligned_columns(data, filename):
    """Сохраняем данные с выровненными колонками"""
    # Определяем максимальную ширину для каждой колонки
    max_input_len = max(len(str(item[0])) for item in data)
    max_input_len = max(max_input_len, len("Input"))
    
    max_uniprot_len = max(len(str(item[1])) for item in data)
    max_uniprot_len = max(max_uniprot_len, len("UniProt_ID"))
    
    # Формируем строку формата
    line_format = f"{{:<{max_input_len}}}  {{:<{max_uniprot_len}}}\n"
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Заголовок
        f.write(line_format.format("Input", "UniProt_ID"))
        # Разделитель
        f.write(line_format.format("-" * max_input_len, "-" * max_uniprot_len))
        # Данные
        for item in data:
            f.write(line_format.format(item[0], item[1]))

def main():
    # Запрашиваем файл у пользователя
    input_file = input("Введите путь к файлу с названиями белков: ")
    
    try:
        # Получаем гены из файла
        all_genes, unique_genes = process_genes_from_file(input_file)
    except FileNotFoundError:
        print(f"Ошибка: файл '{input_file}' не найден")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла: {str(e)}")
        return
    
    start_time = time.time()
    
    # Обрабатываем гены
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_uniprot_id, gene): gene for gene in unique_genes}
        
        for future in as_completed(futures):
            gene = futures[future]
            try:
                results[gene] = future.result()
            except Exception as e:
                results[gene] = f"Error: {str(e)}"
            time.sleep(0.2)  # Ограничение скорости
    
    # Подготавливаем данные для сохранения
    output_data = [(gene, results.get(gene, 'Unknown')) for gene in all_genes]
    
    # Сохраняем результаты с выровненными колонками
    output_file = "uniprot_results_aligned.txt"
    save_aligned_columns(output_data, output_file)

    print(f"\nОбработка заняла {time.time()-start_time:.2f} секунд")
    print(f"Результаты сохранены в файл {output_file}")

if __name__ == "__main__":
    main()