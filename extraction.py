import os
import PyPDF2

folder_path = r'G:\My Drive\Saved from Chrome' 

for filename in os.listdir(folder_path):
    if filename.endswith('.pdf'):
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            print(f"--- Processing: {filename} ({len(reader.pages)} pages) ---")
            
            file_text = ""
            for page in reader.pages:
                file_text += page.extract_text()
            
            # --- ADD THESE LINES TO SAVE THE DATA ---
            # This creates a new filename like "Report.txt" instead of "Report.pdf"
            output_filename = filename.replace('.pdf', '.txt')
            output_path = os.path.join(folder_path, output_filename)
            
            # This writes the text into a permanent file on your G: Drive
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(file_text)
            
            print(f"Done! Saved to: {output_filename}")