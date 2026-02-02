#****************************************************************************
# chatlib.py - Chat model support files
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# This adds support for the Boise State AI API
# Use get_chat_model() to get a model. Values must be set in a .env file:
# MODEL_PROVIDER : the name of the provider, e.g. openai, or boise-state
# MODEL_CHAT : must be a supported model from the provider
# PROVIDER_URL : if a custom url is used set it here
# API_KEY : the secret api key for the model provider
#----------------------------------------------------------------------------
from dotenv import load_dotenv
from typing import List, Optional
import requests
import os

from langchain.chat_models.base import BaseChatModel
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_core.outputs import ChatResult, ChatGeneration

load_dotenv()

class BoiseStateChatModel(BaseChatModel):
    model_id: str
    api_key: str
    temperature: float = 0.7
    max_tokens: int = 1000
    base_url: str = "https://api.boisestate.ai/chat/api-converse"

    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs):
        message_text = messages[-1].content if messages else ""
        
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'message': message_text,
            'modelId': self.model_id,
            'temperature': self.temperature,
            'maxTokens': self.max_tokens
        }

        print(headers)
        
        response = requests.post(self.base_url, headers=headers, json=payload)
        data = response.json()

        if "error" in data:
            message = AIMessage(content=data['message'])
        elif "text" in data:
            message = AIMessage(content=data['text'])    
        else:
            message = AIMessage(content="Unknown error")
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])
    
    @property
    def _llm_type(self):
        return "boise-state"

def get_chat_model():
    model = os.getenv("MODEL_CHAT")
    key = os.getenv("API_KEY")
    provider = os.getenv("MODEL_PROVIDER")

    assert model, "MODEL_CHAT not defined in environment"
    assert key, "API_KEY not defined in environment"
    assert provider, "MODEL_PROVIDER not defined in environment"

    if os.getenv("MODEL_PROVIDER") == "boise-state":
        llm = BoiseStateChatModel(model_id = model, api_key=key)
    else:
        llm = init_chat_model(
            model,
            configurable_fields="any",
            model_provider=provider,
            temperature=0,
            base_url=os.getenv('PROVIDER_URL'),
            api_key=key
        )

    return llm
    
