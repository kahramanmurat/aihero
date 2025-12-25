"""
Day 2: Chunking and Intelligent Processing for Data
Split large documents into smaller, manageable chunks for AI processing.
"""
import re
from typing import List, Dict, Any, Optional
from tqdm.auto import tqdm


def sliding_window(seq: str, size: int, step: int) -> List[Dict[str, Any]]:
    """
    Split a sequence into overlapping chunks using sliding window approach.
    
    Args:
        seq: The text sequence to chunk
        size: Size of each chunk in characters
        step: Step size (overlap = size - step)
    
    Returns:
        List of dictionaries with 'start' position and 'chunk' content
    """
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")

    n = len(seq)
    result = []
    for i in range(0, n, step):
        chunk = seq[i:i+size]
        result.append({'start': i, 'chunk': chunk})
        if i + size >= n:
            break

    return result


def split_by_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs.
    
    Args:
        text: Text to split
    
    Returns:
        List of paragraphs
    """
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in paragraphs if p.strip()]


def split_markdown_by_level(text: str, level: int = 2) -> List[str]:
    """
    Split markdown text by a specific header level.
    
    Args:
        text: Markdown text as a string
        level: Header level to split on (1 for #, 2 for ##, etc.)
    
    Returns:
        List of sections as strings
    """
    # This regex matches markdown headers
    # For level 2, it matches lines starting with "## "
    header_pattern = r'^(#{' + str(level) + r'} )(.+)$'
    pattern = re.compile(header_pattern, re.MULTILINE)

    # Split and keep the headers
    parts = pattern.split(text)
    
    sections = []
    for i in range(1, len(parts), 3):
        # We step by 3 because regex.split() with
        # capturing groups returns:
        # [before_match, group1, group2, after_match, ...]
        # here group1 is "## ", group2 is the header text
        header = parts[i] + parts[i+1]  # "## " + "Title"
        header = header.strip()

        # Get the content after this header
        content = ""
        if i+2 < len(parts):
            content = parts[i+2].strip()

        if content:
            section = f'{header}\n\n{content}'
        else:
            section = header
        sections.append(section)
    
    return sections


def chunk_documents_sliding_window(
    documents: List[Dict[str, Any]], 
    chunk_size: int = 2000, 
    chunk_step: int = 1000
) -> List[Dict[str, Any]]:
    """
    Chunk documents using sliding window approach.
    
    Args:
        documents: List of document dictionaries with 'content' key
        chunk_size: Size of each chunk in characters
        chunk_step: Step size for sliding window
    
    Returns:
        List of chunked documents
    """
    chunks = []
    
    for doc in documents:
        doc_copy = doc.copy()
        doc_content = doc_copy.pop('content', '')
        
        if not doc_content:
            continue
            
        chunk_list = sliding_window(doc_content, chunk_size, chunk_step)
        for chunk in chunk_list:
            chunk_doc = doc_copy.copy()
            chunk_doc['chunk'] = chunk['chunk']
            chunk_doc['chunk_start'] = chunk['start']
            chunk_doc['chunk_method'] = 'sliding_window'
            chunks.append(chunk_doc)
    
    return chunks


def chunk_documents_by_sections(
    documents: List[Dict[str, Any]], 
    level: int = 2
) -> List[Dict[str, Any]]:
    """
    Chunk documents by markdown sections (headers).
    
    Args:
        documents: List of document dictionaries with 'content' key
        level: Header level to split on (1 for #, 2 for ##, etc.)
    
    Returns:
        List of chunked documents
    """
    chunks = []
    
    for doc in documents:
        doc_copy = doc.copy()
        doc_content = doc_copy.pop('content', '')
        
        if not doc_content:
            continue
        
        sections = split_markdown_by_level(doc_content, level=level)
        for section in sections:
            section_doc = doc_copy.copy()
            section_doc['section'] = section
            section_doc['chunk_method'] = f'section_level_{level}'
            chunks.append(section_doc)
    
    return chunks


def chunk_documents_by_paragraphs(
    documents: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Chunk documents by paragraphs.
    
    Args:
        documents: List of document dictionaries with 'content' key
    
    Returns:
        List of chunked documents
    """
    chunks = []
    
    for doc in documents:
        doc_copy = doc.copy()
        doc_content = doc_copy.pop('content', '')
        
        if not doc_content:
            continue
        
        paragraphs = split_by_paragraphs(doc_content)
        for paragraph in paragraphs:
            para_doc = doc_copy.copy()
            para_doc['paragraph'] = paragraph
            para_doc['chunk_method'] = 'paragraph'
            chunks.append(para_doc)
    
    return chunks


def intelligent_chunking(
    text: str, 
    llm_func: Optional[callable] = None,
    prompt_template: Optional[str] = None
) -> List[str]:
    """
    Use LLM to intelligently chunk text into logical sections.
    
    Args:
        text: Text to chunk
        llm_func: Function that takes a prompt and returns LLM response
        prompt_template: Template for the chunking prompt
    
    Returns:
        List of sections
    """
    if llm_func is None:
        raise ValueError("llm_func must be provided for intelligent chunking")
    
    if prompt_template is None:
        prompt_template = """
Split the provided document into logical sections
that make sense for a Q&A system.

Each section should be self-contained and cover
a specific topic or concept.

<DOCUMENT>
{document}
</DOCUMENT>

Use this format:

## Section Name

Section content with all relevant details

---

## Another Section Name

Another section content

---
""".strip()
    
    prompt = prompt_template.format(document=text)
    response = llm_func(prompt)
    sections = response.split('---')
    sections = [s.strip() for s in sections if s.strip()]
    return sections


def chunk_documents_intelligent(
    documents: List[Dict[str, Any]],
    llm_func: callable,
    show_progress: bool = True
) -> List[Dict[str, Any]]:
    """
    Chunk documents using intelligent LLM-based chunking.
    
    Args:
        documents: List of document dictionaries with 'content' key
        llm_func: Function that takes a prompt and returns LLM response
        show_progress: Whether to show progress bar
    
    Returns:
        List of chunked documents
    """
    chunks = []
    iterator = tqdm(documents) if show_progress else documents
    
    for doc in iterator:
        doc_copy = doc.copy()
        doc_content = doc_copy.pop('content', '')
        
        if not doc_content:
            continue
        
        try:
            sections = intelligent_chunking(doc_content, llm_func=llm_func)
            for section in sections:
                section_doc = doc_copy.copy()
                section_doc['section'] = section
                section_doc['chunk_method'] = 'intelligent_llm'
                chunks.append(section_doc)
        except Exception as e:
            print(f"Error processing document {doc.get('filename', 'unknown')}: {e}")
            continue
    
    return chunks


def main():
    """Example usage of chunking functions."""
    print("=" * 60)
    print("Day 2: Chunking and Intelligent Processing")
    print("=" * 60)
    print()
    
    # Example text for demonstration
    sample_text = """
# Introduction

This is the introduction section.

## Getting Started

This is a getting started section with some content.

## Advanced Topics

This section covers advanced topics.

### Subsection 1

Details about subsection 1.

### Subsection 2

Details about subsection 2.

## Conclusion

This is the conclusion.
""".strip()
    
    print("📄 Sample Document:")
    print(f"   Length: {len(sample_text)} characters")
    print()
    
    # Test 1: Sliding Window
    print("1️⃣ Sliding Window Chunking (size=100, step=50):")
    print("-" * 60)
    chunks = sliding_window(sample_text, size=100, step=50)
    print(f"   Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3], 1):  # Show first 3
        print(f"   Chunk {i} (start={chunk['start']}): {chunk['chunk'][:50]}...")
    print()
    
    # Test 2: Paragraph Splitting
    print("2️⃣ Paragraph Splitting:")
    print("-" * 60)
    paragraphs = split_by_paragraphs(sample_text)
    print(f"   Found {len(paragraphs)} paragraphs")
    for i, para in enumerate(paragraphs[:3], 1):  # Show first 3
        print(f"   Paragraph {i}: {para[:50]}...")
    print()
    
    # Test 3: Section Splitting
    print("3️⃣ Section Splitting (level 2):")
    print("-" * 60)
    sections = split_markdown_by_level(sample_text, level=2)
    print(f"   Found {len(sections)} sections")
    for i, section in enumerate(sections, 1):
        print(f"   Section {i}: {section[:60]}...")
    print()
    
    print("=" * 60)
    print("✅ Day 2 chunking functions are ready!")
    print("=" * 60)
    print()
    print("💡 Next steps:")
    print("   - Use chunk_documents_sliding_window() for simple chunking")
    print("   - Use chunk_documents_by_sections() for section-based chunking")
    print("   - Use chunk_documents_intelligent() for LLM-based chunking")
    print("   - Combine with data from day1_ingest.py")


if __name__ == '__main__':
    main()

