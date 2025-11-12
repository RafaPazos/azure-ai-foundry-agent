# azure-ai-foundry-agent

## Overview

The `azure-ai-foundry-agent` is a Python-based Azure Function application designed to interact with Azure AI Projects. It provides an HTTP-triggered endpoint for processing user messages and generating responses using AI agents.

This application is built to:

1. Handle user requests with message input.
2. Retrieve or create an AI agent thread.
3. Interact with the Azure AI Project API to process messages.
4. Generate responses based on AI agent capabilities.

## Features

- **HTTP Trigger**: Provides an anonymous endpoint `/agent_httptrigger` to accept user inputs.
- **Integration with Azure AI Projects**: Uses the `azure-ai-projects` library to manage AI agents, threads, and messages.
- **Error Handling**: Includes robust error checking and logging to ensure smooth operation.

## Prerequisites

To run this project, ensure that you have:

1. Azure Functions Core Tools installed.
2. Python 3.8 or later.
3. Required libraries listed in `requirements.txt`.
4. Azure Subscription to set up required resources like AI Projects.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/azure-data-ai-hub/azure-ai-foundry-agent.git
    cd azure-ai-foundry-agent
    ```

2. Install dependencies on a virtual environment:

    ```bash
    python -m venv .venv

    .venv\scripts\activate

    pip install -r requirements.txt
    ```

3. Set up environment variables:
    - Add `AIProjectConnString` to your local settings or environment variables. This is crucial for connecting to Azure AI Projects. The AI Project connection string can be found in the Azure portal under your AI Project resource as the Azure AI Foundry project endpoint.
    - Authentication is handled via Entra ID, you will need to login and be sure that you have the right permissions. As a security best practice, we'll use keyless authentication to authenticate to Azure OpenAI with Microsoft Entra ID. Open a terminal and run az login --use-device-code to sign in to your Azure account.

4. Run the Azure Function locally:

    ```bash
    func start
    ```

## HTTP Trigger Details

### Endpoint

`POST /agent_httptrigger`

### Query Parameters

| Name       | Type   | Description                          |
|------------|--------|--------------------------------------|
| `message`  | string | The user message to process.         |
| `agentid`  | string | The ID of the AI agent.              |
| `threadid` | string | (Optional) The thread ID for context.|

### Request Example

```json
{
  "message": "Hello, AI Agent!",
  "agentid": "agent123",
  "threadid": "thread456"
}
