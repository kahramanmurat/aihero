# Day 6: Deployment Guide

## Overview

Day 6 focuses on cleaning up code and deploying your agent to the web using Streamlit Cloud.

## Project Structure

The Day 6 implementation is organized into clean, modular files:

- `day6_ingest.py` - Data ingestion and indexing (Days 1-3)
- `day6_search_tools.py` - Search tool implementation
- `day6_search_agent.py` - Agent creation and configuration
- `day6_logs.py` - Logging system (Day 5)
- `day6_main.py` - Command-line interface
- `day6_app.py` - Streamlit web interface

## Running Locally

### Command-Line Interface

```bash
python day6_main.py
```

### Streamlit Web Interface

```bash
streamlit run day6_app.py
```

## Deployment to Streamlit Cloud

### Step 1: Export Dependencies

```bash
uv export --no-dev > requirements.txt
```

Or manually ensure `requirements.txt` includes:
- streamlit
- pydantic-ai
- openai
- minsearch
- python-frontmatter
- requests

### Step 2: Push to GitHub

1. Commit all your code:
   ```bash
   git add .
   git commit -m "Day 6: Clean modular code and Streamlit UI"
   git push
   ```

2. Make sure your repository is public (or connect your GitHub account to Streamlit Cloud)

### Step 3: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Connect your GitHub repository
4. Select your repository and branch
5. Set the main file path: `day6_app.py`
6. Click "Deploy"

### Step 4: Configure Secrets

1. In Streamlit Cloud, go to your app settings
2. Click "Secrets"
3. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

### Step 5: Optional - Configure Log Directory

You can also set a custom log directory:
```
LOGS_DIRECTORY=/tmp/logs
```

## Customization

### Change Repository

Edit `day6_app.py` and `day6_main.py`:
```python
REPO_OWNER = "YourOrg"
REPO_NAME = "your-repo"
```

### Change Filter

Modify the filter function in `init_agent_cached()`:
```python
def filter(doc):
    return 'your-keyword' in doc['filename']
```

### Add Chunking

Enable chunking in `day6_app.py`:
```python
index = index_data(
    REPO_OWNER, 
    REPO_NAME, 
    filter=filter,
    chunk=True,
    chunking_params={'size': 2000, 'step': 1000}
)
```

## Troubleshooting

### App won't start
- Check that `requirements.txt` has all dependencies
- Verify `OPENAI_API_KEY` is set in Streamlit secrets
- Check Streamlit Cloud logs for errors

### Slow indexing
- The index is cached with `@st.cache_resource`, so it only runs once
- For large repos, consider pre-indexing and saving the index

### Memory issues
- Streamlit Cloud has memory limits
- Consider filtering documents or using chunking for very large repos

## Next Steps

- Add conversation history (pass `message_history` to `agent.run()`)
- Add more UI features (sidebar, settings, etc.)
- Implement vector search for better results
- Add authentication if needed
- Monitor usage and costs

