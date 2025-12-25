# AI Agents Crash Course

This folder contains implementations from the AI Agents crash course by Alexey Grigorev.

## Day 1: Ingest and Index Your Data

### Overview
Learn how to download and process data from GitHub repositories for building conversational AI agents.

### Files

- `day1_ingest.py` - Main implementation for downloading and parsing GitHub repositories
- `day1_test_frontmatter.py` - Test script to understand frontmatter parsing
- `day1_example.md` - Example markdown file with frontmatter

### Setup

The project uses `uv` as the package manager. Dependencies are already configured in `pyproject.toml`.

### Running Day 1 Examples

1. **Test frontmatter parsing:**
   ```bash
   uv run python day1_test_frontmatter.py
   ```

2. **Download and process GitHub repositories:**
   ```bash
   uv run python day1_ingest.py
   ```

### What You'll Learn

- How to download GitHub repositories as zip archives
- How to parse frontmatter metadata from markdown files
- How to extract content from .md and .mdx files
- How to process multiple repositories

### Example Repositories

- [DataTalks.Club FAQ](https://github.com/DataTalksClub/faq) - FAQ for DataTalks.Club courses
- [Evidently AI Docs](https://github.com/evidentlyai/docs) - Documentation for Evidently AI library

---

## Day 2: Chunking and Intelligent Processing

### Overview
Learn how to split large documents into smaller, manageable chunks for AI processing. This is essential for RAG (Retrieval-Augmented Generation) applications.

### Files

- `day2_chunking.py` - Main implementation with all chunking methods
- `day2_test_chunking.py` - Test script to compare different chunking approaches
- `day2_intelligent_chunking.py` - LLM-based intelligent chunking (requires OPENAI_API_KEY)

### Chunking Methods

1. **Simple Sliding Window** - Character-based chunking with overlap
   - Good for: Uniform chunk sizes, simple documents
   - Use: `chunk_documents_sliding_window()`

2. **Section-based Chunking** - Split by markdown headers
   - Good for: Structured markdown documentation
   - Use: `chunk_documents_by_sections()`

3. **Paragraph-based Chunking** - Split by paragraphs
   - Good for: Narrative text, literature
   - Use: `chunk_documents_by_paragraphs()`

4. **Intelligent LLM Chunking** - AI-powered semantic chunking
   - Good for: Complex documents, when quality is critical
   - Use: `chunk_documents_intelligent()` (requires API key)

### Running Day 2 Examples

1. **Test basic chunking functions:**
   ```bash
   uv run python day2_chunking.py
   ```

2. **Test chunking on real data:**
   ```bash
   uv run python day2_test_chunking.py
   ```

3. **Test intelligent chunking (requires OPENAI_API_KEY):**
   ```bash
   export OPENAI_API_KEY='your-api-key'
   uv run python day2_intelligent_chunking.py
   ```

### What You'll Learn

- Why chunking is necessary for large documents
- Different chunking strategies and when to use them
- How to implement sliding window chunking with overlap
- How to split documents by structure (sections, paragraphs)
- How to use LLMs for intelligent semantic chunking
- How to choose the right chunking approach for your use case

### Key Concepts

- **Token Limits**: LLMs have maximum input token limits
- **Overlap**: Important for preserving context at chunk boundaries
- **Sliding Window**: Overlapping chunks ensure continuity
- **Section Splitting**: Leverages document structure (markdown headers)
- **Intelligent Chunking**: Uses AI to create semantically meaningful chunks

### Best Practices

1. **Start Simple**: Begin with sliding window chunking
2. **Use Overlap**: Always include overlap between chunks (typically 50% of chunk size)
3. **Consider Structure**: Use section-based chunking for structured documents
4. **Evaluate Results**: Manually inspect chunks to ensure quality
5. **Cost vs Quality**: Only use intelligent chunking when necessary (it costs money)

### Next Steps

Tomorrow we'll cover indexing - inserting chunked data into a search engine for retrieval.

