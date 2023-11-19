# AIDE: Aged care assistant and companion

**[Competition judge's guide is here](ReadMe.md) ☺**

## Technical documentation for developers

The AIDE system consists of three servers that provide the A.I assistant and companion back-end ... along with the Web and Voice user interface front-ends.

- Application server
- Streamlit User Interface server
- Voice User Interface server

***TODO: Insert architecture overview diagram here***

## Local installation and execution

#### Prerequisites

- OpenAI API key: [See your OpenAPI account for acquiring an API key](https://platform.openai.com/api-keys)
- Recent version of Python 3.10.x or 3.11.x

### Local installation

The following installation commands have been tested on Linux and Mac OS X.

    git clone git@github.com:shaneantonio/aide-aiml.git
    cd aide-aiml
    python -m venv venv_aide
    source venv_aide/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

Your Python virtual environment should now be ready to support the Application and Streamlit UI servers below.

### Run the Application server on your local system

The Application server is used by the Streamlit UI and Voice UI servers and must be running before any user interaction via the AIDE User Interfaces.

*Current working directory: Top-level of the aide-aiml repository*

    export OPENAI_API_KEY="sk-........"
    python server/server.py
    # Running on http://127.0.0.1:8080  <-- REST API only, not HTML / HTTP

This server only provides a REST API endpoint for the AIDE User Interface servers.  It does not provide an HTML / HTTP endpoint for web browsers, instead have a look at the Streamlit UI server.

Note: It is entirely possible to develop a standard JavaScript / HTML / CSS web browser application that utilises this Application server.

### Run the Streamlit UI server on your local system

The Streamlit UI server provides standard web server (HTML / HTTP endpoint) that can be used by a web browser directly.

*Current working directory: streamlit subfolder*

    streamlit run streamlit-app.py
    # You can now view your Streamlit app in your browser.
    # Local URL: http://localhost:8501  <-- Web browser host address (URL)

### Run the Voice User Interface server

The Voice UI server provides a conversation interface for non-technical users, especially the patient under care.

***TO BE COMPLETED ***

## Cloud vendor (GCP) deployment and execution

***TO BE COMPLETED, IF REQUIRED, AS TIME PERMITS ***

## To do list

- Server
  - createUserAPI
  - welcome message
  - receive chat & response
  - support streaming
  - ADD RAG feature in the prompt
  - Change the welcome message to engage in the conversation (e.g., I want to know more about you?)
