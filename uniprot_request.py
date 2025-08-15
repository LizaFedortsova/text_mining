import requests


def fetch_uniprot_entry(uniprot_id):
    """Fetch UniProt entry data for given ID."""
    url = f"https://www.uniprot.org/uniprotkb/{uniprot_id}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def parse_protein_names(data):
    """Extract protein names from UniProt data."""
    prot_desc = data.get("proteinDescription", {})
    rec_name = prot_desc.get("recommendedName", {})
    
    recommended = rec_name.get("fullName", {}).get("value", "N/A")
    short = ", ".join(n["value"] for n in rec_name.get("shortNames", []))
    
    alt_names = []
    for alt in prot_desc.get("alternativeNames", []):
        if "fullName" in alt:
            alt_names.append(alt["fullName"]["value"])
        alt_names.extend(n["value"] for n in alt.get("shortNames", []))
    
    return {
        "recommended": recommended,
        "short": short,
        "alternative": ", ".join(alt_names) if alt_names else "N/A"
    }


def parse_gene_names(data):
    """Extract gene names from UniProt data."""
    genes = []
    for gene in data.get("genes", []):
        if "geneName" in gene:
            genes.append(gene["geneName"]["value"])
        genes.extend(syn["value"] for syn in gene.get("synonyms", []))
    return ", ".join(genes) if genes else "N/A"


def parse_chains(data):
    """Extract protein chains from UniProt data."""
    chains = [
        c["description"] for c in data.get("comments", [])
        if c.get("type") == "chain" and "description" in c
    ]
    return ", ".join(chains) if chains else "N/A"


def get_uniprot_data(uniprot_id):
    """Get structured data for UniProt entry."""
    data = fetch_uniprot_entry(uniprot_id)
    if not data:
        return {
            "UniProt ID": uniprot_id,
            "Recommended Name": "Failed",
            "Short Names": "N/A",
            "Alternative Names": "N/A",
            "Gene Names": "N/A",
            "Chains": "N/A"
        }

    names = parse_protein_names(data)
    
    return {
        "UniProt ID": uniprot_id,
        "Recommended Name": names["recommended"],
        "Short Names": names["short"],
        "Alternative Names": names["alternative"],
        "Gene Names": parse_gene_names(data),
        "Chains": parse_chains(data)
    }


def calculate_column_widths(results, columns):
    """Calculate maximum width for each column."""
    widths = {}
    for col in columns:
        max_data = max(len(str(row[col])) for row in results)
        widths[col] = max(max_data, len(col))
    return widths


def save_as_table(results, filename, columns, sep="  "):
    """Save data as formatted text table."""
    widths = calculate_column_widths(results, columns)
    
    with open(filename, "w", encoding="utf-8") as f:
        # Write header
        header = sep.join(col.ljust(widths[col]) for col in columns)
        f.write(header + "\n")
        f.write("-" * len(header) + "\n")
        
        # Write rows
        for row in results:
            line = sep.join(
                str(row[col]).ljust(widths[col]) for col in columns
            )
            f.write(line + "\n")


def main():
    """Main execution function.""" 
    file_name = input('Введите путь к файлу, содержащему Protein IDs:')
    with open(file_name, 'r', encoding='UTF-8') as file_in:
        uniprot_ids = file_in.read().split() 
    # нужно чтобы принимал только первую колонку
    uniprot_ids = [uniprot_ids[i] for i in range(len(uniprot_ids)) if i % 2 == 1]
    columns = [
        "UniProt ID",
        "Recommended Name",
        "Short Names",
        "Alternative Names", 
        "Gene Names",
        "Chains"
    ]
    
    results = [get_uniprot_data(uid) for uid in uniprot_ids]
    save_as_table(results, "uniprot_data_table.txt", columns)
    print("Data saved to 'uniprot_data_table.txt'")


if __name__ == "__main__":
    main()