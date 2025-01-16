import nltk
import numpy as np
from langchain_chroma import Chroma
from chromadb.config import Settings
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import logging
import os
from typing import List
import fitz
from transformers import pipeline

# Import our custom preprocessors
from text_splitter import MedicalDocumentSplitter


def process_medical_guide(pdf_path: str, show_samples: bool = True) -> List[str]:
    """Process medical guide PDF with NLP-based preprocessing and section-based splitting"""
    logging.info("Initializing NLP-based text processing...")

    # Initialize the NER pipeline (optional - can be removed if not needed)
    nlp_ner = pipeline("ner", model="dslim/bert-base-NER", device="cuda:0")

    logging.info("Extracting and processing PDF...")

    # Extract text from PDF
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(14, 90):
        page = doc.load_page(page_num)
        text += page.get_text("text")

    logging.info(f"Extracted text from {len(doc)} pages.")

    if show_samples:
        print("\nSample of raw extracted text (first 500 chars):")
        print("-" * 80)
        print(text[:500])
        print("-" * 80)

    # Clean text
    cleaned_text = basic_cleaning(text)

    if show_samples:
        print("\nSample of cleaned text (first 500 chars):")
        print("-" * 80)
        print(cleaned_text[:500])
        print("-" * 80)

    # Split text into sections
    logging.info("Initializing section-aware splitter...")
    splitter = MedicalDocumentSplitter(
        max_chunk_size=1500,
        min_chunk_size=100
    )

    logging.info("Splitting text into sections...")
    chunks = splitter.split_text(cleaned_text)

    if show_samples:
        print(f"\nTotal number of chunks: {len(chunks)}")
        print("\nSample chunks (last 10):")
        for i, chunk in enumerate(chunks[:-10]):
            print(f"\nChunk {i + 1}/{len(chunks)} (length: {len(chunk)} chars):")
            print("-" * 80)
            print(chunk)
            print("-" * 80)

    return chunks


def basic_cleaning(text: str) -> str:
    """Basic text cleaning function"""
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        cleaned_line = ' '.join(line.split())
        if cleaned_line:
            cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    pdf_path = "/mnt/c/users/stefan/pycharmprojects/Generative_Flashcards/medical_guides/ehab368.pdf"

    try:
        chunks = process_medical_guide(pdf_path)

        # Additional chunk statistics
        chunk_lengths = [len(chunk) for chunk in chunks]
        print(f"\nChunk Statistics:")
        print(f"Total chunks: {len(chunks)}")
        print(f"Average chunk length: {sum(chunk_lengths) / len(chunks):.2f} characters")
        print(f"Shortest chunk: {min(chunk_lengths)} characters")
        print(f"Longest chunk: {max(chunk_lengths)} characters")

        # Initialize Sentence Transformer
        embedding_model_name = "all-MiniLM-L6-v2"
        embedding_model = SentenceTransformer(embedding_model_name)

        # Create and index data
        persist_directory = "chroma_db"
        collection_name = "medical_guidelines"

        # Initialize Chroma client
        chroma_client = PersistentClient(path=persist_directory)

        # Manage collection
        try:
            collection = chroma_client.get_collection(name=collection_name)
            logging.info(f"Collection '{collection_name}' exists. Deleting it to replace.")
            chroma_client.delete_collection(name=collection_name)
        except Exception as e:
            logging.info(f"No existing collection found with name '{collection_name}', proceeding to create a new one.")

        collection = chroma_client.create_collection(name=collection_name)

        # Compute embeddings
        logging.info("Computing embeddings...")
        embeddings = embedding_model.encode(chunks)

        # Add data to database
        logging.info("Adding data to Chroma DB...")
        collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            ids=[f"id_{i}" for i in range(len(chunks))]
        )

        logging.info("Vector database created and stored on disk.")

    except Exception as e:
        logging.error(f"Error processing PDF: {str(e)}")
        raise