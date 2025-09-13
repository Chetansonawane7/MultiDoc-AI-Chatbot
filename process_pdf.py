import pdfplumber
import os

def parse_text_into_sections(text):
    """
    Parses a block of text to identify and separate sections.
    This is a simple rule-based parser. A line is considered a header if it is
    short and written in ALL CAPS. This works well for resumes and some papers.
    You might need to adjust these rules for different document formats.
    """
    sections = {}
    current_header = "introduction" # A default key for any text before the first header
    sections[current_header] = ""
    
    for line in text.split('\n'):
        line_stripped = line.strip()
        
        # This is our rule for identifying a header.
        # It checks if the line is uppercase, has fewer than 5 words, and is not empty.
        if line_stripped.isupper() and len(line_stripped.split()) < 5 and len(line_stripped) > 1:
            current_header = line_stripped
            sections[current_header] = ""
        else:
            # If the line is not a header, append it to the text of the current section.
            if current_header in sections:
                sections[current_header] += line + "\n"

    # Clean up empty sections
    sections = {header: content.strip() for header, content in sections.items() if content.strip()}
    return sections

def extract_structured_data(pdf_path):
    """
    Extracts structured sections and tables from a PDF using pdfplumber.
    It first extracts all text and tables, then parses the text into sections.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return None, None

    all_text = ""
    tables = []
    
    print(f"Processing '{pdf_path}'...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Concatenate text from all pages
                page_text = page.extract_text()
                if page_text:
                    all_text += page_text + "\n"
                
                # Extract tables from each page and add them to our list
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)

        # After getting all text, parse it into structured sections
        structured_sections = parse_text_into_sections(all_text)
        
        print("Processing complete.")
        return structured_sections, tables
        
    except Exception as e:
        print(f"An error occurred while processing the PDF: {e}")
        return None, None

# --- Main execution block ---
if __name__ == "__main__":
    # IMPORTANT: Change this variable to the name of your PDF file.
    # The PDF file should be in the same folder as this Python script.
    pdf_file_path = "sample.pdf" 
    
    sections, extracted_tables = extract_structured_data(pdf_file_path)
    
    if sections:
        print("\n--- ✅ DETECTED SECTIONS ---")
        for header, content in sections.items():
            print(f"--- HEADER: {header} ---")
            # Print the first 200 characters of each section's content
            print(content[:200].strip() + "...") 
            print("-" * (len(header) + 16))
            print()

    if extracted_tables:
        print("\n--- ✅ DETECTED TABLES ---")
        # Print the first detected table as an example
        print("Showing the first table found:")
        for row in extracted_tables[0]:
            print([str(cell).strip() for cell in row]) # Clean up cell content for printing
    elif sections: # Only print this if we found sections but no tables
        print("\n--- ❌ NO TABLES DETECTED ---")