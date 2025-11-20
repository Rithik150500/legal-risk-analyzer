"""
Data Room Preprocessing and Indexing System

This module handles the conversion of documents to PDFs and creates
the indexed data room structure with page-level and document-level summaries.

Process:
1. Convert all files in a folder to PDF using LibreOffice
2. Extract each page as an image
3. Use GPT to summarize each page
4. Combine page summaries and create document-level summary
5. Build the final data room index
"""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import base64
from pdf2image import convert_from_path
from PIL import Image
import io


class DataRoomIndexer:
    """
    Handles the indexing of documents in a data room.
    
    This class orchestrates the entire preprocessing pipeline:
    - Document conversion to PDF
    - Page extraction as images
    - AI-powered summarization at page and document level
    - Index generation
    """
    
    def __init__(
        self,
        input_folder: str,
        output_folder: str,
        summarization_model: str = "gpt-4o-mini",  # or "gpt-5-nano" when available
        dpi: int = 200
    ):
        """
        Initialize the data room indexer.
        
        Args:
            input_folder: Path to folder containing documents to index
            output_folder: Path where processed files and index will be saved
            summarization_model: Model to use for summarization
            dpi: DPI for page image extraction (higher = better quality, larger files)
        """
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.summarization_model = summarization_model
        self.dpi = dpi
        
        # Create output directories
        self.pages_folder = self.output_folder / "pages"
        self.pdfs_folder = self.output_folder / "pdfs"
        self.pages_folder.mkdir(parents=True, exist_ok=True)
        self.pdfs_folder.mkdir(parents=True, exist_ok=True)
    
    def convert_to_pdf(self, file_path: Path) -> Path:
        """
        Convert a file to PDF using LibreOffice.
        
        Args:
            file_path: Path to the file to convert
            
        Returns:
            Path to the converted PDF file
        """
        # Check if already PDF
        if file_path.suffix.lower() == '.pdf':
            # Copy to pdfs folder
            output_path = self.pdfs_folder / file_path.name
            import shutil
            shutil.copy2(file_path, output_path)
            return output_path
        
        # Determine LibreOffice command based on OS
        import platform
        system = platform.system()
        
        if system == 'Windows':
            # Try common Windows paths for soffice.exe
            possible_paths = [
                r'C:\Program Files\LibreOffice\program\soffice.exe',
                r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
            ]
            libreoffice_cmd = None
            for path in possible_paths:
                if Path(path).exists():
                    libreoffice_cmd = path
                    break
            
            if not libreoffice_cmd:
                # Try using PATH (command is 'soffice' on Windows)
                libreoffice_cmd = 'soffice'
        else:
            # Linux/Mac use 'libreoffice' command
            libreoffice_cmd = 'libreoffice'
        
        # Convert using LibreOffice
        try:
            result = subprocess.run([
                libreoffice_cmd,
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(self.pdfs_folder),
                str(file_path)
            ], check=True, capture_output=True, text=True)
            
            # Return path to converted PDF
            pdf_name = file_path.stem + '.pdf'
            return self.pdfs_folder / pdf_name
            
        except subprocess.CalledProcessError as e:
            print(f"Error converting {file_path}: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise
        except FileNotFoundError:
            print("LibreOffice not found. Please install LibreOffice:")
            print("  Ubuntu/Debian: sudo apt-get install libreoffice")
            print("  macOS: brew install --cask libreoffice")
            print("  Windows: winget install TheDocumentFoundation.LibreOffice")
            print("           Or download from https://www.libreoffice.org/")
            print(f"\nOS Detected: {system}")
            if system == 'Windows':
                print("\nSearched the following paths:")
                for path in possible_paths:
                    exists = "✓ Found" if Path(path).exists() else "✗ Not found"
                    print(f"  {exists}: {path}")
            raise
    
    def extract_pages_as_images(self, pdf_path: Path, doc_id: str) -> List[Path]:
        """
        Extract each page of a PDF as an image.
        
        Args:
            pdf_path: Path to the PDF file
            doc_id: Unique identifier for this document
            
        Returns:
            List of paths to extracted page images
        """
        # Create document-specific folder
        doc_pages_folder = self.pages_folder / doc_id
        doc_pages_folder.mkdir(exist_ok=True)
        
        # Convert PDF pages to images
        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=self.dpi,
                fmt='png'
            )
        except Exception as e:
            print(f"Error extracting pages from {pdf_path}: {e}")
            raise
        
        # Save each page
        page_paths = []
        for i, image in enumerate(images, start=1):
            page_path = doc_pages_folder / f"page_{i:03d}.png"
            image.save(page_path, 'PNG')
            page_paths.append(page_path)
        
        return page_paths
    
    def image_to_base64(self, image_path: Path) -> str:
        """Convert image to base64 string for API transmission."""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def summarize_page_with_ai(self, image_path: Path, page_num: int) -> str:
        """
        Use AI to generate a summary of a page image.
        
        Args:
            image_path: Path to the page image
            page_num: Page number
            
        Returns:
            Summary text describing the page content
        """
        # In production, this would call your AI API
        # For this example, we'll show the structure
        
        prompt = f"""Analyze this document page (page {page_num}) and provide a concise summary.

Focus on:
- Main topics or sections covered
- Key information (dates, parties, amounts, obligations)
- Document type indicators (contract clauses, financial data, etc.)
- Any critical legal terms or conditions

Provide a 1-2 sentence summary that captures the essential content of this page."""
        
        # Example using OpenAI API (uncomment and configure in production)
        """
        import openai
        
        # Read and encode image
        image_base64 = self.image_to_base64(image_path)
        
        response = openai.chat.completions.create(
            model=self.summarization_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=200
        )
        
        return response.choices[0].message.content
        """
        
        # Placeholder for demonstration
        return f"[Summary of page {page_num} - to be generated by AI model]"
    
    def summarize_document_with_ai(self, page_summaries: List[str]) -> str:
        """
        Use AI to create a document-level summary from page summaries.
        
        Args:
            page_summaries: List of summaries for each page
            
        Returns:
            Overall document summary
        """
        combined_summaries = "\n\n".join([
            f"Page {i+1}: {summary}"
            for i, summary in enumerate(page_summaries)
        ])
        
        prompt = f"""Based on these page-by-page summaries, provide a comprehensive 2-3 sentence summary of the entire document.

Focus on:
- Document type and purpose
- Main parties involved (if applicable)
- Key terms, obligations, or information
- Overall significance

Page summaries:
{combined_summaries}

Provide a clear, concise summary of the entire document."""
        
        # Example using OpenAI API (uncomment and configure in production)
        """
        import openai
        
        response = openai.chat.completions.create(
            model=self.summarization_model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=250
        )
        
        return response.choices[0].message.content
        """
        
        # Placeholder for demonstration
        return "[Document summary to be generated by AI model]"
    
    def process_document(self, file_path: Path, doc_id: str) -> Dict[str, Any]:
        """
        Process a single document through the full pipeline.
        
        Args:
            file_path: Path to the document file
            doc_id: Unique identifier for this document
            
        Returns:
            Dictionary containing the full document structure with summaries
        """
        print(f"\nProcessing {file_path.name}...")
        
        # Step 1: Convert to PDF
        print("  Converting to PDF...")
        pdf_path = self.convert_to_pdf(file_path)
        
        # Step 2: Extract pages as images
        print("  Extracting pages...")
        page_paths = self.extract_pages_as_images(pdf_path, doc_id)
        print(f"  Extracted {len(page_paths)} pages")
        
        # Step 3: Summarize each page
        print("  Summarizing pages...")
        pages_data = []
        for i, page_path in enumerate(page_paths, start=1):
            print(f"    Summarizing page {i}/{len(page_paths)}...")
            page_summary = self.summarize_page_with_ai(page_path, i)
            
            pages_data.append({
                "page_num": i,
                "summdesc": page_summary,
                "page_image": str(page_path)  # or base64 encoding if needed
            })
        
        # Step 4: Create document-level summary
        print("  Creating document summary...")
        page_summaries = [p["summdesc"] for p in pages_data]
        doc_summary = self.summarize_document_with_ai(page_summaries)
        
        # Step 5: Build document structure
        document = {
            "doc_id": doc_id,
            "original_file": str(file_path),
            "pdf_file": str(pdf_path),
            "summdesc": doc_summary,
            "pages": pages_data
        }
        
        print(f"  ✓ Completed {file_path.name}")
        return document
    
    def build_data_room_index(self) -> Dict[str, Any]:
        """
        Process all documents in the input folder and build the complete data room index.
        
        Returns:
            Complete data room index structure
        """
        print("=" * 70)
        print("Starting Data Room Indexing Process")
        print("=" * 70)
        print(f"Input folder: {self.input_folder}")
        print(f"Output folder: {self.output_folder}")
        print(f"Summarization model: {self.summarization_model}")
        
        # Find all documents in input folder
        supported_extensions = [
            '.pdf', '.docx', '.doc', '.xlsx', '.xls', 
            '.pptx', '.ppt', '.txt', '.rtf', '.odt'
        ]
        
        documents = []
        doc_counter = 1
        
        for file_path in self.input_folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                doc_id = f"doc_{doc_counter:03d}"
                try:
                    document = self.process_document(file_path, doc_id)
                    documents.append(document)
                    doc_counter += 1
                except Exception as e:
                    print(f"  ✗ Failed to process {file_path.name}: {e}")
                    continue
        
        # Build final index
        data_room_index = {
            "metadata": {
                "total_documents": len(documents),
                "created_at": str(Path.ctime(self.output_folder)),
                "model_used": self.summarization_model
            },
            "documents": documents
        }
        
        # Save index to JSON
        index_path = self.output_folder / "data_room_index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(data_room_index, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 70)
        print("Data Room Indexing Complete!")
        print("=" * 70)
        print(f"Total documents processed: {len(documents)}")
        print(f"Index saved to: {index_path}")
        
        return data_room_index
    
    def load_index(self, index_path: Path = None) -> Dict[str, Any]:
        """Load a previously created data room index."""
        if index_path is None:
            index_path = self.output_folder / "data_room_index.json"
        
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Example usage of the data room indexer."""
    
    # Configure paths
    input_folder = "/path/to/your/documents"  # Folder with Word, Excel, PDF files
    output_folder = "/path/to/output/dataroom"  # Where to save processed files
    
    # Create indexer
    indexer = DataRoomIndexer(
        input_folder=input_folder,
        output_folder=output_folder,
        summarization_model="gpt-4o-mini",  # Use "gpt-5-nano" when available
        dpi=200  # Image quality for page extraction
    )
    
    # Build the index
    data_room_index = indexer.build_data_room_index()
    
    # The index is now ready to use with the Legal Risk Analysis Agent
    print("\nData room index structure:")
    print(json.dumps({
        "metadata": data_room_index["metadata"],
        "documents": [
            {
                "doc_id": doc["doc_id"],
                "summdesc": doc["summdesc"],
                "pages_count": len(doc["pages"])
            }
            for doc in data_room_index["documents"]
        ]
    }, indent=2))


if __name__ == "__main__":
    main()
