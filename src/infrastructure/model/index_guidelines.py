# import nltk
# import chromadb
# from chromadb.utils import embedding_functions
# from sentence_transformers import SentenceTransformer
# from langchain.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# import logging
# import os
#
# def load_pdf(path):
#     loader = PyPDFLoader(path)
#     return loader.load()
#
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#     nltk.download('punkt')
#     # 1. Load PDF
#     pdf_path = "/mnt/c/users/stefan/pycharmprojects/Generative_Flashcards/medical_guides/ehab368.pdf" #Put your pdf path here
#     documents = load_pdf(pdf_path)
#     if documents:
#         raw_text = " ".join([doc.page_content for doc in documents])  # concatenates all pages.
#     else:
#         print("no documents found, check path")
#         exit()
#
#     # 2. Initialize Text Splitter
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=100,
#         length_function=len
#     )
#
#     # 3. Chunk the text
#     chunks = text_splitter.split_text(raw_text)
#     logging.info(f"Number of chunks: {len(chunks)}")
#
#     # 4. Initialize Sentence Transformer
#     embedding_model_name = "all-MiniLM-L6-v2"
#     embedding_model = SentenceTransformer(embedding_model_name)
#
#     # 5. Create vector embeddings
#     embeddings = embedding_model.encode(chunks)
#
#     # 6. Create and index data
#     # Use custom embedding function for Chroma
#     chroma_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
#         model_name=embedding_model_name
#     )
#
#     # Create a chroma client
#     persist_directory = "chroma_db"  # Change if you want
#     chroma_client = chromadb.PersistentClient(path=persist_directory)
#
#     # Create a collection.
#     collection_name = "medical_guidelines"
#     try:
#         collection = chroma_client.create_collection(
#             name=collection_name,
#             embedding_function=chroma_ef
#         )
#     except:
#         logging.info("Using existing collection")
#         collection = chroma_client.get_collection(
#             name = collection_name,
#              embedding_function=chroma_ef
#         )
#     # add data to database.
#     collection.add(
#         embeddings=embeddings.tolist(),  # Convert numpy arrays to lists
#         documents=chunks,
#         ids=[f"id_{i}" for i in range(len(chunks))]  # create ids
#     )
#     logging.info("Vector database created and stored on disk.")