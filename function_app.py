import os
import json
import azure.functions as func
import logging
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml
from azure_functions_openapi.swagger_ui import render_swagger_ui

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Enable OpenAPI/Swagger
@openapi(
    summary="Greet user",
    route="/agent_httptrigger",
    request_model={"message": "string","agentid": "string","threadid": "string"},
    response_model={"message": "string"},
    tags=["agent"]
)

@app.function_name(name="agent_httptrigger")
@app.route(route="agent_httptrigger")
def agent_httptrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    message = req.params.get('message')
    agentid = req.params.get('agentid')
    threadid = req.params.get('threadid')
    
    if not message or not agentid:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = None

        if req_body:
            message = req_body.get('message')
            agentid = req_body.get('agentid')
            threadid = req_body.get('threadid')

    if not message or not agentid:
        return func.HttpResponse(
            "Pass in a message and agentid in the query string or in the request body for a personalized response.",
            status_code=400
        )

    conn_str = os.environ.get("AIProjectConnString")
    if not conn_str:
        logging.error("AIProjectConnString is not set in local.settings.json or environment variables.")
        return func.HttpResponse(
            "Internal Server Error: Missing AIProjectConnString.",
            status_code=500
        )

    try:            
        project_client = AIProjectClient(
            credential=DefaultAzureCredential(),
            endpoint=conn_str,
        )

        agent = project_client.agents.get_agent(agentid)
        if not agent:
            logging.error(f"Agent with ID {agentid} not found.")
            return func.HttpResponse(
                f"Agent with ID {agentid} not found.",
                status_code=404
            )

        # Create or reuse thread
        if not threadid:
            thread = project_client.agents.threads.create()
            threadid = thread.id

        # Post user message
        project_client.agents.messages.create(
            thread_id=threadid,
            role="user",
            content=message
        )

        # Process the message with the agent
        project_client.agents.runs.create_and_process(
            thread_id=threadid,
            agent_id=agent.id
        )

        # Get the messages from the thread
        messages = project_client.agents.messages.list(thread_id=threadid)
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        if assistant_messages:
            assistant_message = assistant_messages[-1]
            assistant_text = " ".join(
                part["text"]["value"] for part in assistant_message["content"] if "text" in part
            )
        else:
            assistant_text = "No assistant message found."

        response = {
            "response": assistant_text,
            "threadId": threadid
        }

        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return func.HttpResponse(
            "Internal Server Error: " + str(e),
            status_code=500
        )
    
@app.function_name(name="openapi_json")
@app.route(route="/api/openapi.json", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def openapi_json(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
            json.dumps(get_openapi_json()),
            status_code=200,
            mimetype="application/json"
        )

@app.function_name(name="openapi_yaml")
@app.route(route="/api/openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def openapi_yaml(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
            json.dumps(get_openapi_yaml()),
            status_code=200,
            mimetype="application/x-yaml"
        )

@app.function_name(name="swagger_ui")
@app.route(route="/api/docs", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
