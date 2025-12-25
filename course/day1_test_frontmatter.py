"""
Test script to understand frontmatter parsing.
"""
import frontmatter

# Example: Reading a markdown file with frontmatter
with open('day1_example.md', 'r', encoding='utf-8') as f:
    post = frontmatter.load(f)

# Access metadata
print("=" * 60)
print("Frontmatter Metadata:")
print("=" * 60)
print(f"Title: {post.metadata.get('title', 'N/A')}")
print(f"Author: {post.metadata.get('author', 'N/A')}")
print(f"Date: {post.metadata.get('date', 'N/A')}")
print(f"Tags: {post.metadata.get('tags', [])}")
print(f"Difficulty: {post.metadata.get('difficulty', 'N/A')}")

print()
print("=" * 60)
print("Content (without frontmatter):")
print("=" * 60)
print(post.content)

print()
print("=" * 60)
print("Complete Dictionary (metadata + content):")
print("=" * 60)
data = post.to_dict()
print(f"Keys: {list(data.keys())}")
print(f"\nFull data structure:")
for key, value in data.items():
    if key == 'content':
        print(f"  {key}: {value[:100]}... (truncated)")
    else:
        print(f"  {key}: {value}")

