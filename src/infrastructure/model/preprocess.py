import json
import re
import string
from typing import Dict, List, Tuple
import unicodedata
import fitz
import layoutparser as lp
from nltk.tokenize import sent_tokenize

class MedicalTextPreprocessor:
    def __init__(self):
        # Enhanced patterns for medical content
        self.preserve_patterns = [
            r'\d+\.?\d*\s*(?:mg|mcg|ml|kg|mmol|mmHg|μg|ng|g|%)',  # Units
            r'class [I|V]+[a-zA-Z]?',  # Classification patterns
            r'grade [1-4]',  # Medical grades
            r'stage [A-D]',  # Disease stages
            r'type [1-2]',  # Disease types
            r'level of evidence [A-C]',  # Evidence levels
            r'recommendation class [I|IIa|IIb|III]'  # Recommendation classes
        ]

        # Load medical abbreviations
        self.load_abbreviations()

    def load_abbreviations(self):
        """Load and validate medical abbreviations from JSON file"""
        try:
            with open('abbreviations.json', 'r') as file:
                self.abbrev_dict = {}
                for line in file:
                    if line.strip():
                        try:
                            entry = json.loads(line.strip().rstrip(','))
                            for abbr, full_form in entry.items():
                                clean_abbr = abbr.replace('.', '').upper()
                                self.abbrev_dict[clean_abbr] = full_form
                                if '.' in abbr:
                                    self.abbrev_dict[abbr] = full_form
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            print("Warning: abbreviations.json not found. Proceeding without abbreviations.")
            self.abbrev_dict = {}

    def process_pdf(self, pdf_path: str) -> str:
        """Process PDF with layout analysis, only pages 14-90"""
        doc = fitz.open(pdf_path)
        model = lp.Detectron2LayoutModel('lp://PubLayNet/mask_rcnn_R_50_FPN_3x/config')

        processed_text = []
        # Only process pages 14-90
        for page_num in range(13, 90):  # 0-based indexing
            if page_num >= len(doc):
                break

            page = doc[page_num]
            # Get page text with positioning
            blocks = page.get_text("dict")["blocks"]
            # Use layout parser for structure
            layout = model.detect(page.get_pixmap())
            # Merge layout information with text
            processed_text.append(self._merge_layout_text(layout, blocks))

        raw_text = "\n".join(processed_text)
        return self.clean_text(raw_text)

    def _merge_layout_text(self, layout, blocks):
        """Merge layout information with text blocks"""
        merged_text = []

        for layout_elem in layout:
            # Get text blocks that fall within this layout element
            elem_blocks = [
                block for block in blocks
                if self._block_in_element(block, layout_elem)
            ]

            if layout_elem.type == "Title":
                # Process titles
                text = " ".join(block["text"] for block in elem_blocks)
                merged_text.append(f"\n## {text}\n")

            elif layout_elem.type == "Text":
                # Process regular text
                text = " ".join(block["text"] for block in elem_blocks)
                merged_text.append(text)

            elif layout_elem.type == "Table":
                # Mark table regions for later processing
                text = " ".join(block["text"] for block in elem_blocks)
                merged_text.append(f"\n[TABLE]\n{text}\n[/TABLE]\n")

        return "\n".join(merged_text)

    def _block_in_element(self, block, layout_elem):
        """Check if a text block falls within a layout element"""
        block_bbox = fitz.Rect(block["bbox"])
        elem_bbox = layout_elem.block.coordinates

        return (block_bbox.x0 >= elem_bbox[0] and
                block_bbox.y0 >= elem_bbox[1] and
                block_bbox.x1 <= elem_bbox[2] and
                block_bbox.y1 <= elem_bbox[3])

    def clean_text(self, text: str) -> str:
        """Enhanced text cleaning with medical context preservation"""
        # Store preserved entities
        preserved = []
        for pattern in self.preserve_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                preserved.append((match.span(), match.group()))

        # Basic cleaning
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')

        # Remove PDF artifacts and formatting
        text = re.sub(r'(?<=\w)-\s+(?=\w)', '', text)  # Remove hyphenation
        text = re.sub(r'\f', ' ', text)  # Remove form feeds
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Remove page numbers
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)  # Remove citation brackets
        text = re.sub(r'\((?:\d{4}(?:;\s*)?)+\)', '', text)  # Remove year citations

        # Fix spacing
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
        text = re.sub(r'(?<=\d)(?=[A-Za-z])|(?<=[A-Za-z])(?=\d)', ' ', text)

        # Restore preserved entities
        for (start, end), entity in preserved:
            text = text[:start] + entity + text[end:]

        # Final cleaning
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = re.sub(r'\s*([.,!?])', r'\1 ', text)  # Fix punctuation spacing
        text = re.sub(r'\s+', ' ', text).strip()  # Final whitespace cleanup

        return text
