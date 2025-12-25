"""
Test script to demonstrate different chunking approaches.
This script uses data from Day 1 to test chunking methods.
"""
from day1_ingest import read_repo_data
from day2_chunking import (
    chunk_documents_sliding_window,
    chunk_documents_by_sections,
    chunk_documents_by_paragraphs
)


def test_chunking_methods():
    """Test different chunking methods on real data."""
    print("=" * 60)
    print("Day 2: Testing Chunking Methods")
    print("=" * 60)
    print()
    
    # Download a small repository for testing
    print("📥 Downloading test repository...")
    try:
        docs = read_repo_data('DataTalksClub', 'faq')
        print(f"✅ Downloaded {len(docs)} documents")
    except Exception as e:
        print(f"❌ Error downloading: {e}")
        return
    
    if not docs:
        print("❌ No documents to process")
        return
    
    # Find a document with substantial content
    test_doc = None
    for doc in docs:
        content = doc.get('content', '')
        if len(content) > 500:  # Find a document with some content
            test_doc = doc
            break
    
    if not test_doc:
        print("⚠️ No document with sufficient content found")
        return
    
    print(f"\n📄 Test Document:")
    print(f"   Title: {test_doc.get('title', 'N/A')}")
    print(f"   Filename: {test_doc.get('filename', 'N/A')}")
    print(f"   Content length: {len(test_doc.get('content', ''))} characters")
    print()
    
    # Test 1: Sliding Window
    print("1️⃣ Testing Sliding Window Chunking:")
    print("-" * 60)
    test_docs = [test_doc]
    chunks = chunk_documents_sliding_window(
        test_docs, 
        chunk_size=500, 
        chunk_step=250
    )
    print(f"   Created {len(chunks)} chunks")
    if chunks:
        print(f"   First chunk (start={chunks[0].get('chunk_start', 0)}):")
        chunk_content = chunks[0].get('chunk', '')[:100]
        print(f"   {chunk_content}...")
    print()
    
    # Test 2: Section-based (if markdown)
    print("2️⃣ Testing Section-based Chunking:")
    print("-" * 60)
    chunks = chunk_documents_by_sections(test_docs, level=2)
    print(f"   Created {len(chunks)} sections")
    if chunks:
        section_content = chunks[0].get('section', '')[:100]
        print(f"   First section:")
        print(f"   {section_content}...")
    print()
    
    # Test 3: Paragraph-based
    print("3️⃣ Testing Paragraph-based Chunking:")
    print("-" * 60)
    chunks = chunk_documents_by_paragraphs(test_docs)
    print(f"   Created {len(chunks)} paragraphs")
    if chunks:
        para_content = chunks[0].get('paragraph', '')[:100]
        print(f"   First paragraph:")
        print(f"   {para_content}...")
    print()
    
    # Compare results
    print("=" * 60)
    print("📊 Comparison:")
    print("=" * 60)
    print(f"   Original documents: {len(test_docs)}")
    print(f"   Sliding window chunks: {len(chunk_documents_sliding_window(test_docs, 500, 250))}")
    print(f"   Section-based chunks: {len(chunk_documents_by_sections(test_docs))}")
    print(f"   Paragraph-based chunks: {len(chunk_documents_by_paragraphs(test_docs))}")
    print()
    print("💡 Choose the method that best fits your use case:")
    print("   - Sliding window: Good for uniform chunk sizes")
    print("   - Section-based: Good for structured markdown docs")
    print("   - Paragraph-based: Good for narrative text")


if __name__ == '__main__':
    test_chunking_methods()

