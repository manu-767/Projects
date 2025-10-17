from google.cloud import dialogflow_v2 as dialogflow

def detect_intent_text(project_id, session_id, text, language_code='en'):
    """Detects intent from text using Dialogflow."""
    session_client = dialogflow.SessionsClient()

    # Build session path
    session = session_client.session_path(project=project_id, session=session_id)

    # Construct the text input
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)

    # Construct the query input
    query_input = dialogflow.types.QueryInput(text=text_input)

    # Perform the detect intent request
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.fulfillment_text
