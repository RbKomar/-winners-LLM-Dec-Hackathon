## Demo Files Overview

This section provides guidance on running demonstration files located in the `knowledge_graph` directory of
the `legacy_code_assistant` project.

### Directory Path

- **Location:** `.demo/`

### Demo Files

- [x] `github_graph_DEMO_1_GIF.py`: Visualizes GitHub graphs.
- [x] `repo_code_graph_DEMO_2_GIF.py`: Demonstrates repository code graphs.

    - **Note for DEMO 2**:
        - To integrate an LLM into this demo, locate the `TODO` comment in the code where additional processing should
          be added.
        - Currently, the template selection feature is not operational. This needs to be fixed to enable proper
          functionality.

### Running Streamlit Demos

To run the Streamlit demonstrations for each script, use the following commands in PowerShell:

- For GitHub Graph Visualization:
  ```powershell
  streamlit run github_graph_DEMO_1_GIF.py
  ```
- For Repository Code Graph:
  ```powershell
  streamlit run repo_code_graph_DEMO_2_GIF.py
  ```

### Repository Setup

Ensure the repository path is set to `tests/test_repo`. To clone the required repository, execute the `repo_cloner`
script:

```powershell
python legacy_code_assistant/data_extraction/repo_cloner.py
```

### Credentials
You must provide credentials in the demo folder. A file credentials.yaml should be placed there. It should have the following structure:
```
'AZURE_OPENAI_ENDPOINT': <URL OF AZURE ENDPOINT>
'AZURE_OPENAI_API_KEY': <KEY>
'Deployment_completion': <AZURE DEPLOYMENT FOR COMPLETION MODEL (e.g. gpt4)>
'Deployment_embeddings':  <AZURE DEPLOYMENT FOR EMBEDDING MODEL (e.g. ada)>
```
