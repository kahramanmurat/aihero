"""
Day 1: Ingest and Index Your Data
Download and process data from GitHub repositories.
"""
import io
import zipfile
import requests
import frontmatter
from typing import List, Dict, Any


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
    prefix = 'https://codeload.github.com' 
    url = f'{prefix}/{repo_owner}/{repo_name}/zip/refs/heads/{branch}'
    
    print(f"Downloading repository: {repo_owner}/{repo_name} from {url}")
    resp = requests.get(url)
    
    if resp.status_code != 200:
        raise Exception(f"Failed to download repository: {resp.status_code}")

    repository_data = []
    zf = zipfile.ZipFile(io.BytesIO(resp.content))
    
    for file_info in zf.infolist():
        filename = file_info.filename
        filename_lower = filename.lower()

        # Process both .md and .mdx files
        if not (filename_lower.endswith('.md') or filename_lower.endswith('.mdx')):
            continue
    
        try:
            with zf.open(file_info) as f_in:
                content = f_in.read().decode('utf-8', errors='ignore')
                post = frontmatter.loads(content)
                data = post.to_dict()
                data['filename'] = filename
                repository_data.append(data)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
    
    zf.close()
    return repository_data


def main():
    """Example usage of the repository data reader."""
    print("=" * 60)
    print("Day 1: GitHub Repository Data Ingestion")
    print("=" * 60)
    print()
    
    # Example 1: DataTalks.Club FAQ
    print("📥 Downloading DataTalks.Club FAQ...")
    dtc_faq = read_repo_data('DataTalksClub', 'faq')
    print(f"✅ Downloaded {len(dtc_faq)} FAQ documents")
    
    if dtc_faq:
        print(f"\n📄 Sample document:")
        print(f"   Filename: {dtc_faq[0].get('filename', 'N/A')}")
        print(f"   Keys: {list(dtc_faq[0].keys())}")
        if 'content' in dtc_faq[0]:
            content_preview = dtc_faq[0]['content'][:100] + "..." if len(dtc_faq[0]['content']) > 100 else dtc_faq[0]['content']
            print(f"   Content preview: {content_preview}")
    
    print()
    print("-" * 60)
    print()
    
    # Example 2: Evidently AI Docs
    print("📥 Downloading Evidently AI documentation...")
    try:
        evidently_docs = read_repo_data('evidentlyai', 'docs')
        print(f"✅ Downloaded {len(evidently_docs)} documentation files")
        
        if evidently_docs:
            print(f"\n📄 Sample document:")
            print(f"   Filename: {evidently_docs[0].get('filename', 'N/A')}")
            print(f"   Keys: {list(evidently_docs[0].keys())}")
    except Exception as e:
        print(f"❌ Error downloading Evidently docs: {e}")
    
    print()
    print("=" * 60)
    print("✅ Day 1 complete! Data ingestion pipeline is ready.")
    print("=" * 60)


if __name__ == '__main__':
    main()

