from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Section:
    level: int
    number: str
    title: str
    content: str
    subsections: List['Section']

class MedicalDocumentSplitter:
    def __init__(self, max_chunk_size=2000, min_chunk_size=100):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        
        # Fallback splitter for oversized sections
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=min_chunk_size,
            length_function=len,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        self.section_patterns = [
            r'^(\d+\.)\s+(.+)$',
            r'^(\d+\.\d+\.)\s+(.+)$',
            r'^(\d+\.\d+\.\d+\.)\s+(.+)$'
        ]
    def _identify_section_level(self, line: str) -> tuple:
        """Identify section level and return (level, number, title) if it's a section header"""
        for level, pattern in enumerate(self.section_patterns):
            match = re.match(pattern, line.strip())
            if match:
                return (level, match.group(1), match.group(2))
        return None

    def _split_into_sections(self, text: str) -> List[Section]:
        """Split text into hierarchical sections"""
        lines = text.split('\n')
        root_sections = []
        current_sections = [None, None, None]  # Track current section at each level
        current_content = []

        def save_current_content():
            if current_sections[2] and current_content:
                current_sections[2].content = '\n'.join(current_content)
            elif current_sections[1] and current_content:
                current_sections[1].content = '\n'.join(current_content)
            elif current_sections[0] and current_content:
                current_sections[0].content = '\n'.join(current_content)
            current_content.clear()

        for line in lines:
            section_info = self._identify_section_level(line)
            
            if section_info:
                level, number, title = section_info
                save_current_content()
                
                new_section = Section(
                    level=level,
                    number=number,
                    title=title,
                    content="",
                    subsections=[]
                )

                # Update section hierarchy
                if level == 0:
                    root_sections.append(new_section)
                    current_sections = [new_section, None, None]
                elif level == 1 and current_sections[0]:
                    current_sections[0].subsections.append(new_section)
                    current_sections[1] = new_section
                    current_sections[2] = None
                elif level == 2 and current_sections[1]:
                    current_sections[1].subsections.append(new_section)
                    current_sections[2] = new_section
            else:
                current_content.append(line)

        save_current_content()
        return root_sections

    def _split_content(self, content: str) -> List[str]:
        """Split content into chunks using base splitter"""
        if not content.strip():
            return []
        return self.base_splitter.split_text(content)

    def _section_to_chunks(self, section: Section, include_headers: bool = True) -> List[str]:
        """Convert a section and its subsections into chunks"""
        chunks = []
        
        # Process current section
        if section.content.strip():
            section_header = f"{section.number} {section.title}"
            content_chunks = self._split_content(section.content)
            
            for i, chunk in enumerate(content_chunks):
                if include_headers:
                    # Add section information to each chunk
                    chunk = f"[Section: {section_header}]\n{chunk}"
                chunks.append(chunk)

        # Process subsections recursively
        for subsection in section.subsections:
            chunks.extend(self._section_to_chunks(subsection, include_headers))

        return chunks

    def split_text(self, text: str) -> List[str]:
        """Main method to split text into chunks while respecting section hierarchy"""
        # First, split into sections
        sections = self._split_into_sections(text)
        
        # Then process each section
        chunks = []
        for section in sections:
            chunks.extend(self._section_to_chunks(section))
            
        return chunks

