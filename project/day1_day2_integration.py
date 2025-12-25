"""
Integration example: Day 1 + Day 2
Download GitHub repository data and chunk it for AI processing.
"""
from day1_ingest import read_repo_data
from day2_chunking import (
    chunk_documents_sliding_window,
    chunk_documents_by_sections,
    chunk_documents_by_paragraphs
)


def process_repo_with_chunking(
    repo_owner: str,
    repo_name: str,
    chunk_method: str = 'sliding_window',
    chunk_size: int = 2000,
    chunk_step: int = 1000
):
    """
    Complete pipeline: Download repo data and chunk it.
    
    Args:
        repo_owner: GitHub username or organization
        repo_name: Repository name
        chunk_method: 'sliding_window', 'sections', or 'paragraphs'
        chunk_size: Size for sliding window (if applicable)
        chunk_step: Step for sliding window (if applicable)
    
    Returns:
        List of chunked documents
    """
    print("=" * 60)
    print(f"Processing {repo_owner}/{repo_name}")
    print("=" * 60)
    print()
    
    # Step 1: Download and parse repository
    print("📥 Step 1: Downloading repository...")
    docs = read_repo_data(repo_owner, repo_name)
    print(f"✅ Downloaded {len(docs)} documents")
    print()
    
    # Step 2: Chunk the documents
    print(f"📦 Step 2: Chunking documents using {chunk_method}...")
    
    if chunk_method == 'sliding_window':
        chunks = chunk_documents_sliding_window(
            docs, 
            chunk_size=chunk_size, 
            chunk_step=chunk_step
        )
    elif chunk_method == 'sections':
        chunks = chunk_documents_by_sections(docs, level=2)
    elif chunk_method == 'paragraphs':
        chunks = chunk_documents_by_paragraphs(docs)
    else:
        raise ValueError(f"Unknown chunk method: {chunk_method}")
    
    print(f"✅ Created {len(chunks)} chunks")
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Summary:")
    print("=" * 60)
    print(f"   Original documents: {len(docs)}")
    print(f"   Chunks created: {len(chunks)}")
    print(f"   Average chunks per document: {len(chunks) / len(docs):.1f}")
    print()
    
    return chunks


def main():
    """Example usage of the integrated pipeline."""
    print("=" * 60)
    print("Day 1 + Day 2 Integration Example")
    print("=" * 60)
    print()
    
    # Example: Process DataTalks.Club FAQ
    try:
        chunks = process_repo_with_chunking(
            repo_owner='DataTalksClub',
            repo_name='faq',
            chunk_method='sliding_window',
            chunk_size=1000,
            chunk_step=500
        )
        
        # Show sample chunk
        if chunks:
            print("📄 Sample chunk:")
            print("-" * 60)
            sample = chunks[0]
            print(f"   Method: {sample.get('chunk_method', 'N/A')}")
            print(f"   Filename: {sample.get('filename', 'N/A')}")
            if 'chunk' in sample:
                print(f"   Content preview: {sample['chunk'][:150]}...")
            elif 'section' in sample:
                print(f"   Section preview: {sample['section'][:150]}...")
            print()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("=" * 60)
    print("✅ Integration complete!")
    print("=" * 60)
    print()
    print("💡 Next steps:")
    print("   - Index chunks into a search engine (Day 3)")
    print("   - Use chunks for RAG (Retrieval-Augmented Generation)")
    print("   - Build an AI agent that can answer questions about the repo")


if __name__ == '__main__':
    main()

