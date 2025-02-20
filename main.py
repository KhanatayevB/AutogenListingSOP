import os
import json
from dotenv import load_dotenv
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from flipkart_api_handler import FlipkartAPIHandler

# Load environment variables - Using your secure approach
load_dotenv()

# Configuration - Using environment variables instead of hardcoded values
config_list = [{
    'model': os.getenv('DEPLOYMENT_NAME'),
    'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
    'api_type': 'azure',
    'base_url': os.getenv('ENDPOINT_URL'),
    'api_version': '2024-02-15-preview'
}]

def get_test_responses() -> dict:
    """Get test responses from user input"""
    responses = {}
    
    # Account Status
    print("\nSelect test account status:")
    print("1: ACTIVE")
    print("2: ONBOARDING")
    print("3: ON_HOLD")
    choice = input("Enter number (1-3): ").strip() or "1"
    responses['account_status'] = {
        "1": "ACTIVE",
        "2": "ONBOARDING",
        "3": "ON_HOLD"
    }.get(choice, "ACTIVE")

    # Listing Status
    print("\nSelect test listing status:")
    print("1: ACTIVE")
    print("2: INACTIVE")
    print("3: ARCHIVED")
    print("4: READY_FOR_ACTIVATION")
    print("5: BLOCKED")
    choice = input("Enter number (1-5): ").strip() or "1"
    responses['listing_status'] = {
        "1": "ACTIVE",
        "2": "INACTIVE",
        "3": "ARCHIVED",
        "4": "READY_FOR_ACTIVATION",
        "5": "BLOCKED"
    }.get(choice, "ACTIVE")

    # Block Reason
    print("\nSelect test block reason:")
    print("1: SELLER_STATE_CHANGE")
    print("2: POLICY_VIOLATION")
    print("3: TRADEMARK_VIOLATION")
    choice = input("Enter number (1-3): ").strip() or "1"
    responses['block_reason'] = {
        "1": "SELLER_STATE_CHANGE",
        "2": "POLICY_VIOLATION",
        "3": "TRADEMARK_VIOLATION"
    }.get(choice, "SELLER_STATE_CHANGE")

    # Brand Approval
    print("\nSelect BrandXVertical approval status:")
    print("1: APPROVED")
    print("2: PENDING")
    print("3: REJECTED")
    choice = input("Enter number (1-3): ").strip() or "2"
    responses['brand_approval'] = {
        "1": "APPROVED",
        "2": "PENDING",
        "3": "REJECTED"
    }.get(choice, "PENDING")

    return responses

# Initialize API Handler with user-selected test responses
print("\n[DEBUG] Getting test responses...")
test_responses = get_test_responses()
api_handler = FlipkartAPIHandler(test_responses)

# Core agents with exact same names and base configuration as original
function_executor = UserProxyAgent(
    name="FunctionExecutor",
    human_input_mode="NEVER",
    system_message="""You are a function executor that interfaces with the Flipkart API handler.
When you receive a function call:
1. Parse the function name and arguments from the FUNCTION_CALL format
2. Execute the corresponding API handler method
3. Return results in a structured JSON format
4. Handle any errors gracefully with clear error messages

Example format:
FUNCTION_CALL:get_user_status
{"user_id": "SELLER123"}""",
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "groupchat",
        "use_docker": False
    }
)

user_agent = UserProxyAgent(
    name="User",
    human_input_mode="ALWAYS",
    system_message="""You are a user interface that:
1. Directly accepts human input without modification
2. Passes messages exactly as received to other agents
3. Does not add any additional processing or formatting
4. Does not generate responses on behalf of the human
5. Allows the human to type their responses naturally""",
    code_execution_config=False
)

api_agent = AssistantAgent(
    name="API_Agent",  # Exact name from original
    system_message="""You are the API Gateway. Format your responses exactly as shown:
1. For user status checks:
FUNCTION_CALL:get_user_status
{"user_id": "[ID]"}

2. For listing status checks:
FUNCTION_CALL:get_listing_status
{"listing_id": "[ID]"}

3. For reactivation checks:
FUNCTION_CALL:can_reactivate_listing
{"block_reason": "[REASON]"}

4. For ticket creation:
FUNCTION_CALL:create_support_ticket
{"user_id": "[USER_ID]", "listing_id": "[LISTING_ID]", "reason": "[REASON]"}""",
    llm_config={"config_list": config_list}
)

sia = AssistantAgent(  # Exact name from original
    name="SIA",
    system_message="""You are a Seller Integration Assistant. Follow these steps exactly:
1. When user first connects, ask for their user ID
2. When user provides ID, format: "@API_Agent user_status:[ID]"
3. After receiving user status:
   - If active, IMMEDIATELY say "Your account is active. Please provide your listing ID."
   - If not active, explain status and end conversation
4. When user provides listing ID, format: "@API_Agent listing_status:[ID]"
5. For blocked listings:
   - Format: "@API_Agent reactivate:block_reason"
   - If reactivatable: "@API_Agent create_ticket:[USER_ID]:[LISTING_ID]:[REASON]"
6. Present results clearly to user""",
    llm_config={"config_list": config_list}
)

# Enhanced speaker selection function
# Improved: Added more precise routing and error handling
def speaker_selection_func(last_speaker, groupchat):
    messages = groupchat.messages
    last_msg = messages[-1]["content"] if messages else ""
    
    # Handle API calls
    if "@API_Agent" in last_msg:
        return api_agent
    
    # Handle function execution
    if "FUNCTION_CALL:" in last_msg:
        return function_executor
        
    # Handle function results
    if last_speaker == function_executor:
        return sia
    
    # Handle user input needed
    if last_speaker == sia and any(phrase in last_msg.lower() for phrase in [
        "provide", "please provide", "what is", "enter", "what's your"
    ]):
        return user_agent
    
    # Handle user input
    if last_speaker == user_agent:
        return sia
    
    return user_agent

# Create group chat with enhanced agents
groupchat = GroupChat(
    agents=[user_agent, sia, api_agent, function_executor],
    messages=[],
    max_round=25,
    speaker_selection_method=speaker_selection_func
)

# Create manager with enhanced configuration
manager = GroupChatManager(
    groupchat=groupchat,
    llm_config={
        "config_list": config_list,
        "temperature": 0,
        "timeout": 120
    }
)

def start_chat():
    """Start a new chat session with enhanced error handling"""
    print("\n🔍 DEBUG: Starting new chat session")
    try:
        # Initialize API handler with test responses
        print("🔧 DEBUG: API Handler initialized with test responses")
        
        # Start chat
        user_agent.initiate_chat(
            manager,
            message="I need help with my listing",
            clear_history=True
        )
    except Exception as e:
        print(f"❌ ERROR: Chat session failed: {str(e)}")
        print("🔍 DEBUG: Attempting graceful shutdown...")
        raise

if __name__ == "__main__":
    start_chat() 