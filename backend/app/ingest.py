from datasets import load_dataset
import sys
import os
from sentence_transformers import (
    SentenceTransformer,
)  
from opensearchpy import OpenSearch, NotFoundError
import uuid
import ast  
from . import config  

class SBERTEmbedder:
    def __init__(self, model_name="snunlp/KR-SBERT-V40K-klueNLI-augSTS"):
        self.model = SentenceTransformer(model_name)
        print(f"SBERT Embedder initialized with model: {model_name}")

    def encode(self, texts, batch_size=32, show_progress_bar=True):
        print(f"Encoding {len(texts)} texts...")
        return self.model.encode(
            texts, batch_size=batch_size, show_progress_bar=show_progress_bar
        )
print("Loading dataset...")
dataset = load_dataset("binjang/NIKL-korean-english-dictionary", split="train")
print("Dataset loaded.")
print(f"Dataset columns: {dataset.column_names}")

texts = [item.get("Form") for item in dataset if item and item.get("Form")]
texts = [text for text in texts if text]
print(f"Number of texts to embed: {len(texts)}")

embedder = SBERTEmbedder()
vectors = embedder.encode(texts)

vector_dimension = 768  
if vectors is not None and vectors.size > 0:
    print(
        f"Generated {len(vectors)} vectors. Shape of first vector: {vectors[0].shape}"
    )
    vector_dimension = vectors[0].shape[0]
else:
    print(
        f"Warning: No vectors were generated (texts list might be empty or embedding failed). Defaulting dimension to {vector_dimension}."
    )
    if not texts:
        print("Error: No valid 'Form' data found in dataset to embed. Aborting.")
        sys.exit(1)

client = OpenSearch(
    hosts=[{"host": "localhost", "port": config.OPENSEARCH_PORT}],
    http_auth=(config.OPENSEARCH_USER, config.OPENSEARCH_PASSWORD),
    use_ssl=False,
    verify_certs=False,
    timeout=60,
)
print("Connected to OpenSearch.")

index_name = config.OPENSEARCH_INDEX_NAME  

try:
    if client.indices.exists(index=index_name):
        print(f"Deleting existing index: {index_name}...")
        client.indices.delete(index=index_name)
        print(f"Index {index_name} deleted.")
except NotFoundError:
    print(f"Index {index_name} not found, no need to delete.")
except Exception as e:
    print(f"Error deleting index {index_name}: {e}")


print(f"Creating new index: {index_name}...")
try:
    client.indices.create(
        index=index_name,
        body={
            "settings": {
                "index.knn": True,
                "index.knn.space_type": "cosinesimil",
            },
            "mappings": {
                "properties": {
                    "form": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": vector_dimension,
                    },  
                    "korean_definition": {"type": "text"},
                    "english_definition": {"type": "text"},
                    "usages": {"type": "text"},  
                }
            },
        },
    )
    print(f"Index {index_name} created successfully.")
except Exception as e:
    print(f"Error creating index {index_name}: {e}")
    sys.exit(f"Failed to create index. Aborting.")


print(f"Indexing documents...")
indexed_count = 0
valid_items_for_indexing = [item for item in dataset if item and item.get("Form")]

if len(valid_items_for_indexing) != len(vectors):
    print(
        f"Warning: Mismatch in item count ({len(valid_items_for_indexing)}) and vector count ({len(vectors)}). Indexing up to the smaller count."
    )
num_to_process = min(len(valid_items_for_indexing), len(vectors))


for i in range(num_to_process):
    item = valid_items_for_indexing[i]
    vec = vectors[i].tolist()  
    raw_usages_data = item.get("Usages")  
    processed_usages = []  

    if isinstance(raw_usages_data, list):
        for sub_item in raw_usages_data:
            if isinstance(sub_item, list):
                processed_usages.extend(map(str, sub_item))
            else:
                processed_usages.append(str(sub_item))
    elif isinstance(raw_usages_data, str):
        stripped_usages = raw_usages_data.strip()
        if stripped_usages.startswith("[") and stripped_usages.endswith("]"):
            try:
                evaluated_data = ast.literal_eval(stripped_usages)
                if isinstance(evaluated_data, (list, tuple)):
                    for sub_item in evaluated_data:
                        if isinstance(sub_item, (list, tuple)):  
                            processed_usages.extend(map(str, sub_item))
                        else:
                            processed_usages.append(str(sub_item))
                else:  
                    processed_usages.append(
                        str(evaluated_data)
                    )  
            except (ValueError, SyntaxError):
                print(
                    f"Warning: Could not parse usages string for form '{item.get('Form')}': '{raw_usages_data}'. Storing as a single string in the list."
                )
                if stripped_usages:
                    processed_usages.append(stripped_usages)
        elif stripped_usages:  
            processed_usages.append(stripped_usages)

    doc = {
        "form": item.get(
            "Form"
        ),  
        "embedding": vec,
        "korean_definition": item.get("Korean Definition", ""),
        "english_definition": item.get("English Definition", ""),
        "usages": (
            processed_usages if processed_usages else None
        ),
    }


    try:
        client.index(index=index_name, id=str(uuid.uuid4()), body=doc) 
        indexed_count += 1
    except Exception as e_doc:
        print(f"ERROR indexing document for form '{item.get('Form')}': {e_doc}")

print(f"{indexed_count} documents were successfully indexed into '{index_name}'.")
