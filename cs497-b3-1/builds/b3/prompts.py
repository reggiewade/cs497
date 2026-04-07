#****************************************************************************
# prompts.py - Forbidden Island multi-agent app llm prompts
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# Keep all your prompts in this file and import them from your agents.py module
# You can create and use templates by defining them here. Use the {name} syntax
# in your prompts to dynamically inject content:
#
#   chain = prompt | llm
#   chain.invoke({ "name": "injected content" })
#----------------------------------------------------------------------------
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

ROLE_DESCRIPTIONS = {
    "diver": "You can move through adjacent 'Sunk' or 'Flooded' tiles for 1 action. You are the only one who can cross gaps in the island.",
    "engineer": "You can 'Shore Up' two tiles for only 1 action. This is your primary job—keeping the island from sinking.",
    "explorer": "You can move or 'Shore Up' diagonally. You have the best reach of any player.",
    "messenger": "You can give any of your Treasure Cards to any player, anywhere on the island, for 1 action. You are the team's logistics hub.",
    "navigator": "You can move another player up to 2 adjacent tiles for 1 action. You help get your teammates to safety or towards treasures.",
    "pilot": "Once per turn, you can move to any tile on the board for 1 action. You are the most mobile player."
}

# Example template with {role} and {role_description} injection variables
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are the {role} in Forbidden Island. {role_description}"),
    ("human", "Current game state:\n{obs}\n\nChoose up to 3 actions.")
])

def get_role_description(role):
    return ROLE_DESCRIPTIONS.get(role, "No description available for this role.")

def get_strategy_prompt(state, role):
    return prompt.invoke({
        "role": role,
        "role_description": get_role_description(role),
        "obs": state["obs"]
    })