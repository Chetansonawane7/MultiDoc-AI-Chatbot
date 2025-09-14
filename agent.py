import os
import google.generativeai as genai
from dotenv import load_dotenv # <-- IMPORT THE LIBRARY
from process_pdf import extract_structured_data
import fitz  # PyMuPDF


# --- Configuration ---
load_dotenv() # <-- LOAD VARIABLES FROM .env FILE

# Now os.environ can access the loaded variables
try:
    # os.environ.get() will now read the key loaded from the .env file
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Make sure it's set in your .env file.")
    genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error configuring API: {e}")
    exit()

# --- Helper Function to Format the PDF Data ---
def format_context_for_llm(sections, tables):
    """Formats the extracted PDF data into a single string for the LLM prompt."""
    context_str = ""
    
    if sections:
        context_str += "--- DOCUMENT SECTIONS ---\n"
        for header, content in sections.items():
            context_str += f"Section Title: {header}\nContent:\n{content}\n\n"
            
    if tables:
        context_str += "--- DOCUMENT TABLES ---\n"
        for i, table in enumerate(tables):
            table_str = "\n".join(["\t".join(map(str, row)) for row in table])
            context_str += f"Table {i+1}:\n{table_str}\n\n"
            
    return context_str

# --- The Core Q&A Function ---
def answer_query(query, document_context):
    """Sends the user's query and document context to the Gemini LLM."""

    # Check if user query is related to translation
    translation_keywords = ["translate", "translation", "convert", "from", "to", "language"]
    is_translation_request = any(word in query.lower() for word in translation_keywords)

    if is_translation_request:
        prompt = f"""
        You are a highly skilled language translation AI.
        The user has uploaded a PDF document, and your task is to translate its content from the source language to the target language specified in the user's query.
        Here is the extracted content of the document (sections and tables).

        --- DOCUMENT CONTENT ---
        {document_context}
        --- END OF DOCUMENT CONTENT ---

        User's Instruction: "{query}"

        TRANSLATED CONTENT:
        """
    else:
        prompt = f"""
        You are an expert AI assistant specialized in understanding and analyzing document contents.
        The user has uploaded a PDF document (sections and tables are extracted below).
        
        Based on the content and your general knowledge, answer the user's question. 
        If the answer is explicitly present in the context, use it.
        Otherwise, try to infer a reasonable answer from the context or mention if it is related to the document.
        If the document is irrelevant, you can answer based on your knowledge.

        --- DOCUMENT CONTEXT ---
        {document_context}
        --- END OF CONTEXT ---

        USER'S QUESTION: "{query}"

        ANSWER:
        """

    print("\n\nSending request to Google Gemini...")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest') 
        response = model.generate_content(prompt)
        print("...Response received.")
        return response.text.strip()
    except Exception as e:
        return f"An error occurred with the AI model: {e}"
    




# --- Main execution block ---
if __name__ == "__main__":
    pdf_file_path = "sample.pdf" 
    
    sections, tables = extract_structured_data(pdf_file_path)
    
    if sections or tables:
        full_context = format_context_for_llm(sections, tables)
        
        print("\nDocument loaded. You can now ask questions.")
        while True:
            user_query = input("\nAsk a question (or type 'exit' to quit): ")
            if user_query.lower() == 'exit':
                break
            
            llm_answer = answer_query(user_query, full_context)
            
            print("\n--- Answer ---")
            print(llm_answer)
            print("----------------")
    else:
        print(f"Could not extract any useful data from the PDF: {pdf_file_path}")