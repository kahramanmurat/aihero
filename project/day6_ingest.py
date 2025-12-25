"""
Day 6: Clean ingestion module
Combines Day 1-3: Download, chunk, and index GitHub repository data.
"""
import io
import zipfile
import requests
import frontmatter
from typing import List, Dict, Any, Optional, Callable
from minsearch import Index


def read_repo_data(repo_owner: str, repo_name: str, branch: str = 'main') -> List[Dict[str, Any]]:
    """
    Download and parse all markdown files from a GitHub repository.
    
    Args:
        repo_owner: GitHub username or organization
        repo_name: Repository name
        branch: Branch name (default: 'main')
    
    Returns:
        List of dictionaries containing file content and metadata
    """
    url = f'https://codeload.github.com/{repo_owner}/{repo_name}/zip/refs/heads/{branch}'
    resp = requests.get(url)
    
    if resp.status_code != 200:
        raise Exception(f"Failed to download repository: {resp.status_code}")
    
    repository_data = []
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    
    for file_info in zf.infolist():
        filename = file_info.filename.lower()
        
        if not (filename.endswith('.md') or filename.endswith('.mdx')):
            continue
        
        try:
            with zf.open(file_info) as f_in:
                content = f_in.read().decode('utf-8', errors='ignore')
                post = frontmatter.loads(content)
                data = post.to_dict()
                
                # Strip the first part of the path (zip archive name)
                _, filename_repo = file_info.filename.split('/', maxsplit=1)
                data['filename'] = filename_repo
                repository_data.append(data)
        except Exception as e:
            print(f"Error processing {file_info.filename}: {e}")
            continue
    
    zf.close()
    return repository_data


def sliding_window(seq: str, size: int, step: int) -> List[Dict[str, Any]]:
    """
    Split a sequence into overlapping chunks using sliding window approach.
    
    Args:
        seq: The text sequence to chunk
        size: Size of each chunk in characters
        step: Step size (overlap = size - step)
    
    Returns:
        List of dictionaries with 'start' position and 'content'
    """
    if size <= 0 or step <= 0:
        raise ValueError("size and step must be positive")
    
    n = len(seq)
    result = []
    for i in range(0, n, step):
        batch = seq[i:i+size]
        result.append({'start': i, 'content': batch})
        if i + size > n:
            break
    
    return result


def chunk_documents(
    docs: List[Dict[str, Any]], 
    size: int = 2000, 
    step: int = 1000
) -> List[Dict[str, Any]]:
    """
    Chunk documents using sliding window approach.
    
    Args:
        docs: List of document dictionaries with 'content' key
        size: Size of each chunk in characters
        step: Step size for sliding window
    
    Returns:
        List of chunked documents
    """
    chunks = []
    
    for doc in docs:
        doc_copy = doc.copy()
        doc_content = doc_copy.pop('content', '')
        
        if not doc_content:
            continue
        
        doc_chunks = sliding_window(doc_content, size=size, step=step)
        for chunk in doc_chunks:
            chunk.update(doc_copy)
        chunks.extend(doc_chunks)
    
    return chunks


def index_data(
    repo_owner: str,
    repo_name: str,
    filter: Optional[Callable] = None,
    chunk: bool = False,
    chunking_params: Optional[Dict[str, int]] = None,
) -> Index:
    """
    Complete pipeline: Download, optionally filter, optionally chunk, and index data.
    
    Args:
        repo_owner: GitHub username or organization
        repo_name: Repository name
        filter: Optional function to filter documents
        chunk: Whether to chunk documents
        chunking_params: Parameters for chunking (size, step)
    
    Returns:
        Minsearch Index instance
    """
    # Step 1: Download repository
    docs = read_repo_data(repo_owner, repo_name)
    
    # Step 2: Filter (if provided)
    if filter is not None:
        docs = [doc for doc in docs if filter(doc)]
    
    # Step 3: Chunk (if requested)
    if chunk:
        if chunking_params is None:
            chunking_params = {'size': 2000, 'step': 1000}
        docs = chunk_documents(docs, **chunking_params)
    
    # Step 4: Index
    index = Index(
        text_fields=["content", "filename"],
    )
    
    index.fit(docs)
    return index

