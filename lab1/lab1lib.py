from collections import defaultdict
from dotenv import load_dotenv
from markdown import markdown

import chatlib

from langchain_core.messages import AIMessage, HumanMessage

load_dotenv()

# initialize chats with a session token (chat_id) and array to hold chats from each session
chats = defaultdict(lambda: [])

# get_chat_model is a wrapper for boise state AI
llm = chatlib.get_chat_model()

def chat(chat_id, user_message, config=None):
    """Sends the chat along with the parameters to the LLM and gets the 
    response.

    Args:
        chat_id (string): essentially a session token
        user_message (string): user message extracted from the form
        config (dict, optional): LLM parameters. Defaults to None.
    """
    
    # convert to HumanMessage object
    chats[chat_id].append(HumanMessage(user_message))
    messages = chats[chat_id]
    
    response = llm.invoke(messages, **config)
    
    for key in [ 'temperature', 'top_p', 'max_tokens' ]:
        if key in config: response.additional_kwargs[key] = config[key]

    # chats[chat_id][-1] is the last HumanMessage sent, this appends a dictionary to the response_metadata field in the 
    # HumanMessage object.  This stores the token_usage for more verbose tracking.
    chats[chat_id][-1].response_metadata['token_usage'] = { 'prompt_tokens': response.response_metadata.get('token_usage', {}).get('prompt_tokens') }
    chats[chat_id].append(response)
    

from langchain_core.messages import HumanMessage, AIMessage
from markdown import markdown # Assuming you're using the markdown library

def get_chat_html(chat_id: str) -> str:
    """
    Converts a list of chat messages into a formatted HTML string.
    
    This function iterates through messages in a specific chat session, 
    formats the content using markdown, and appends metadata using 
    FontAwesome icons.

    Args:
        chat_id (str): session token

    Returns:
        str: string of HTML divs formatting the chats
    """
    results = ""
    
    # Ensure the chat_id exists to avoid KeyErrors
    if chat_id not in chats:
        return "<p>Chat session not found.</p>"

    for msg in chats[chat_id]:
        msg_type = type(msg)
        
        # Determine CSS class based on message origin
        msg_class = "user" if msg_type is HumanMessage else "assistant" if msg_type is AIMessage else None
        
        # Skip messages that aren't Human or AI like SystemMessages
        if msg_class:
            meta = msg.response_metadata
            info = f"<div class='info'>"

            if msg_class == "assistant":
                # Add completion token count
                tokens = meta.get('token_usage', {}).get('completion_tokens', 0)
                info += f"<div> <i class='fas fa-coins text-warning'></i> {tokens}</div>"
                
                # Dynamic mapping for model configuration parameters
                configs = [
                    ('temperature', 'fa-thermometer-half text-error'),
                    ('top_p', 'fa-gauge text-success'),
                    ('max_tokens', 'fa-ban text-danger')
                ]
                
                for config, icon in configs:
                    if config in msg.additional_kwargs:
                        val = msg.additional_kwargs.get(config)
                        info += f"<div class='config'><i class='fas {icon}'></i> {val}</div>"
            else:
                # Add prompt token count for user messages
                tokens = meta.get('token_usage', {}).get('prompt_tokens', 0)
                info += f"<div> <i class='fas fa-coins text-warning'></i> {tokens}</div>"

            info += "</div>"
            
            # Wrap content and metadata in a container div
            results += f"<div class='{msg_class}'> {markdown(msg.content)} {info} </div>"
            
    return results