import os
import json
import autogen
from dotenv import load_dotenv
from typing import Dict, Any
from flipkart_api_handler import FlipkartAPIHandler

###############################################################################
# 1. Load environment variables
###############################################################################
load_dotenv()

###############################################################################
# Color and formatting constants
###############################################################################
class Colors:
    # Basic colors
    GRAY = "\033[90m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    # Formatting
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    
    # Reset
    RESET = "\033[0m"

# Agent colors
AGENT_COLORS = {
    "listing_specialist": Colors.BLUE,
    "api_agent": Colors.GREEN,
    "ticket_agent": Colors.MAGENTA,
    "user_proxy": Colors.YELLOW
}

def format_debug(msg):
    return f"{Colors.GRAY}[DEBUG] {msg}{Colors.RESET}"

def format_agent_message(agent_name, receiver, content):
    color = AGENT_COLORS.get(agent_name, Colors.WHITE)
    return f"\n{color}{Colors.BOLD}{agent_name}{Colors.RESET} (to {Colors.UNDERLINE}{receiver}{Colors.RESET}):\n{content}\n"

def format_separator():
    return f"\n{Colors.CYAN}{Colors.BOLD}{'-'*80}{Colors.RESET}\n"

def format_summary_header():
    return f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}{'='*40} CONVERSATION SUMMARY {'='*40}{Colors.RESET}\n"

def format_ticket_details():
    return f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD} TICKET/ENROLLMENT DETAILS {Colors.RESET}\n{Colors.CYAN}{'-'*40}{Colors.RESET}"

###############################################################################
# 2. Helper functions to pick statuses (just as in your original code)
###############################################################################
def get_test_responses() -> Dict[str, str]:
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

def create_api_agent(api_handler: FlipkartAPIHandler, config_list: list) -> autogen.AssistantAgent:
    """Create API agent with function calling capabilities"""
    return autogen.AssistantAgent(
        name="api_agent",
        system_message="""You are an API agent that makes calls to Flipkart's backend systems.
        When you receive a request, analyze it and call the appropriate function:
        
        - For account status queries, extract the seller_id and call check_account_status()
        - For listing status queries, extract the listing_id and call check_listing_status()
        - For block reason queries, extract the listing_id and call get_block_reason()
        - For brand approval queries, extract the brand_id and call check_brand_approval()
        - For override status queries, extract the listing_id and call get_override_status()
        
        Return the function's response in a clear format.
        """,
        llm_config={
            "config_list": config_list,
            "functions": [
                {
                    "name": "check_account_status",
                    "description": "Check account status for a seller",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "seller_id": {
                                "type": "string",
                                "description": "The seller ID to check"
                            }
                        },
                        "required": ["seller_id"]
                    }
                },
                {
                    "name": "check_listing_status",
                    "description": "Check status for a listing",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "listing_id": {
                                "type": "string",
                                "description": "The listing ID to check"
                            }
                        },
                        "required": ["listing_id"]
                    }
                },
                {
                    "name": "get_block_reason",
                    "description": "Get block reason for a listing",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "listing_id": {
                                "type": "string",
                                "description": "The listing ID to check"
                            }
                        },
                        "required": ["listing_id"]
                    }
                },
                {
                    "name": "check_brand_approval",
                    "description": "Check brand approval status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "brand_id": {
                                "type": "string",
                                "description": "The brand ID to check"
                            }
                        },
                        "required": ["brand_id"]
                    }
                },
                {
                    "name": "get_override_status",
                    "description": "Get override status for a listing",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "listing_id": {
                                "type": "string",
                                "description": "The listing ID to check"
                            }
                        },
                        "required": ["listing_id"]
                    }
                }
            ]
        }
    )

###############################################################################
# 3. Main code
###############################################################################
def main():
    # Load environment variables
    load_dotenv()
    
    # Get test responses
    print("\n[DEBUG] Getting test responses...")
    test_responses = get_test_responses()
    
    # Create API handler with test responses
    api_handler = FlipkartAPIHandler(test_responses)
    
    # Configure LLM
    config_list = [{
        'model': os.getenv('DEPLOYMENT_NAME'),
        'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
        'azure_endpoint': os.getenv('ENDPOINT_URL'),
        'api_type': 'azure',
        'api_version': '2024-02-15-preview'
    }]

    ############################################################################
    # 4. Define our Agents
    ############################################################################

    # -- 4a. The "User" proxy agent
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        # system_message is the role/instructions for the user agent
        system_message="A user seeking help with their listing.",
        human_input_mode="ALWAYS",
        code_execution_config={"use_docker": False}
    )
    
    # -- 4b. API agent
    api_agent = create_api_agent(api_handler, config_list)

    # -- 4c. Ticket agent
    ticket_agent = autogen.AssistantAgent(
        name="ticket_agent",
        system_message="""You are a Ticket Agent responsible for creating and managing support tickets.
    
    For Brand Assure Program enrollment, respond with JSON:
    {
        "type": "BRAND_ASSURE_ENROLLMENT",
        "status": "CREATED",
        "enrollment": {
            "program_id": "BAP123456",
            "enrollment_link": "https://brandassure.example.com",
            "seller_id": "(from conversation)",
            "listing_id": "(from conversation)"
        }
    }

    For L2 tickets, respond with JSON:
    {
        "type": "L2_TICKET",
        "ticket_id": "T123456",
        "status": "CREATED",
        "data": {
            "listing_id": "(from conversation)",
            "account_status": "(from conversation)",
            "listing_status": "(from conversation)",
            "reason_code": "(from conversation)",
            "ticket_type": "L2_INFRINGEMENT or L2_INCIDENT"
        }
    }

    Always include all context from the conversation in your response.
    Respond with EXACTLY these JSON formats, no additional text.""",
        llm_config={"config_list": config_list}
    )

    # -- 4d. Listing specialist
    listing_specialist = autogen.AssistantAgent(
        name="listing_specialist",
        system_message="""You are a Listing Specialist helping users with blocked/inactive listings.
    Follow the SOP flow exactly:
    1. Ask if listing is blocked/inactive
    2. Get seller ID and check account status:
       - Ask: "[@api_agent] What is the account status for this seller?"
       - If response is "ONBOARDING":
         Show Template 1: "Your account is currently in the onboarding phase. Listings cannot be activated until the onboarding process is complete. Please complete all onboarding steps to proceed."
         Then terminate conversation.
       - If response is "ON_HOLD" or "ACTIVE": Continue to step 3
    3. Get listing ID (FSN/SKU)
    4. Check listing status:
       - Ask: "[@api_agent] What is the listing status for this FSN?"
       - If "INACTIVE": Show Template 2 and terminate
       - If "ARCHIVED": Show Template 7 and terminate
       - If "READY_FOR_ACTIVATION": Show Template 3 and terminate
       - If "ACTIVE": Show Template 4 and terminate
       - If "BLOCKED": Continue to step 5
    5. If BLOCKED:
       - Ask: "[@api_agent] What is the block reason for this listing?"
       - If SELLER_STATE_CHANGE, show Template 5 and terminate
       - Otherwise, proceed to override check:
         a. Ask: "[@api_agent] What is the override status?"
         b. If single override, check resolution
         c. If multiple overrides, list them and check each
    
    6. For Trademark Violations:
       - Ask: "[@api_agent] What is the BrandXVertical approval status?"
       - Ask: "[@api_agent] Is listing creation allowed?"
       - If cannot create listing:
         Send: "[@ticket_agent] Please enroll user in Brand Assure Program for FSN: {listing_id}, Account Status: {account_status}, Block Reason: TRADEMARK_VIOLATION"
         After response, show user:
         "I've initiated your enrollment in the Brand Assure Program. Here are your details:
         Program ID: {program_id}
         Enrollment Link: {enrollment_link}
         Please complete your enrollment using the link above."
       - If can create listing:
         Send: "[@ticket_agent] Please create L2 Infringement ticket for FSN: {listing_id}, Account Status: {account_status}, Block Reason: TRADEMARK_VIOLATION"
         After response, show user:
         "I've created a ticket for your case. Here are the details:
         Ticket ID: {ticket_id}
         Status: {status}
         Type: {ticket_type}
         We'll investigate your case and get back to you soon."
    
    Always use EXACT query formats when asking agents.
    Maintain professional tone and clear communication.
    After showing ticket/enrollment information to user, terminate conversation.""",
        llm_config={"config_list": config_list}
    )

    print("\n[DEBUG] Created agents...")
    print("[DEBUG] UserProxyAgent:", user_proxy.name)
    print("[DEBUG] APIAgent:", api_agent.name)
    print("[DEBUG] TicketAgent:", ticket_agent.name)
    print("[DEBUG] ListingSpecialist:", listing_specialist.name)

    ############################################################################
    # 5. ORCHESTRATOR: Step-by-step conversation flow among agents
    ############################################################################
    # The orchestrator will track messages and direct them to the correct agent.
    # This is a simplified example showing how to handle user <-> listing_specialist <-> api_agent.
    ############################################################################

    def orchestrate_conversation(listing_specialist, user_proxy, api_agent, ticket_agent, api_handler):
        print("\n" + format_debug("Starting conversation...") + "\n")
        
        conversation = []
        
        # Start with listing specialist's first question
        first_message = {
            "role": "assistant",
            "sender": listing_specialist.name,
            "receiver": user_proxy.name,
            "content": "Is your listing blocked or inactive?"
        }
        print(format_agent_message(first_message['sender'], first_message['receiver'], first_message['content']))
        print(format_separator())
        conversation.append(first_message)

        # Main conversation loop
        while True:
            last_message = conversation[-1]
            sender = last_message["sender"]
            receiver = last_message["receiver"]
            content = last_message["content"]

            # Print debug info
            print(format_debug(f"Processing message:"))
            print(format_debug(f"From: {sender}"))
            print(format_debug(f"To: {receiver}"))
            print(format_debug(f"Content: {content}"))

            # Handle user input
            if receiver == user_proxy.name:
                user_input = input(
                    f"{Colors.YELLOW}Replying as {user_proxy.name}. Provide feedback to {listing_specialist.name}. "
                    f"Press enter to skip and use auto-reply, or type 'exit' to end the conversation: {Colors.RESET}"
                )
                if user_input.lower() == "exit":
                    print("[DEBUG] User ended the conversation.")
                    break

                # Create user response message
                user_message = {
                    "role": "user",
                    "sender": user_proxy.name,
                    "receiver": listing_specialist.name,
                    "content": user_input
                }
                conversation.append(user_message)
                print(format_agent_message(user_message['sender'], user_message['receiver'], user_message['content']))
                print(format_separator())

            # Handle API agent response
            elif receiver == api_agent.name:
                print("[DEBUG] Requesting API response...")
                # The API agent will use function calling to execute the appropriate method
                api_response = api_agent.generate_reply(messages=conversation)
                
                if api_response:
                    # Check if this is a function call
                    if isinstance(api_response, dict) and 'function_call' in api_response:
                        func_name = api_response['function_call']['name']
                        func_args = json.loads(api_response['function_call']['arguments'])
                        
                        # Get the function from the API handler
                        func = getattr(api_handler, func_name)
                        # Call the function with the arguments
                        result = func(**func_args)
                        
                        api_message = {
                            "role": "assistant",
                            "sender": api_agent.name,
                            "receiver": listing_specialist.name,
                            "content": json.dumps(result, indent=2)
                        }
                    else:
                        api_message = {
                            "role": "assistant",
                            "sender": api_agent.name,
                            "receiver": listing_specialist.name,
                            "content": api_response
                        }
                    
                    conversation.append(api_message)
                    print(format_agent_message(api_message['sender'], api_message['receiver'], api_message['content']))
                    print(format_separator())
                    print(f"[DEBUG] API responded with: {api_message['content']}")

            # Handle ticket agent response
            elif receiver == ticket_agent.name:
                print("[DEBUG] Requesting ticket creation...")
                ticket_response = ticket_agent.generate_reply(messages=conversation)
                if ticket_response:
                    ticket_message = {
                        "role": "assistant",
                        "sender": ticket_agent.name,
                        "receiver": listing_specialist.name,
                        "content": ticket_response
                    }
                    conversation.append(ticket_message)
                    print(format_agent_message(ticket_message['sender'], ticket_message['receiver'], ticket_message['content']))
                    print(format_separator())
                    print(f"[DEBUG] Ticket agent responded with: {ticket_response}")

            # Handle listing specialist response
            elif receiver == listing_specialist.name:
                print("[DEBUG] Generating listing specialist response...")
                specialist_response = listing_specialist.generate_reply(messages=conversation)
                if specialist_response:
                    # Check if this is a query for the API agent
                    if "[@api_agent]" in specialist_response:
                        print("[DEBUG] Detected API query, routing to API agent...")
                        response_message = {
                            "role": "assistant",
                            "sender": listing_specialist.name,
                            "receiver": api_agent.name,
                            "content": specialist_response
                        }
                    # Check if this is a query for the ticket agent
                    elif "[@ticket_agent]" in specialist_response:
                        print("[DEBUG] Detected ticket request, routing to ticket agent...")
                        response_message = {
                            "role": "assistant",
                            "sender": listing_specialist.name,
                            "receiver": ticket_agent.name,
                            "content": specialist_response
                        }
                    else:
                        print("[DEBUG] Regular user interaction...")
                        # Normal user interaction
                        response_message = {
                            "role": "assistant",
                            "sender": listing_specialist.name,
                            "receiver": user_proxy.name,
                            "content": specialist_response
                        }
                    
                    conversation.append(response_message)
                    print(format_agent_message(response_message['sender'], response_message['receiver'], response_message['content']))
                    print(format_separator())
                else:
                    print("[DEBUG] ListingSpecialist has no further response. Stopping.")
                    break

            # Check for termination conditions
            if "stop" in content.lower() or "template" in content.lower():
                print("[DEBUG] Conversation complete. Ending.")
                break

        # Add ticket summary at the end
        print(format_summary_header())
        print(format_ticket_details())
        
        # Find the last ticket agent response
        ticket_info = None
        for message in reversed(conversation):
            if message["sender"] == ticket_agent.name:
                try:
                    ticket_info = eval(message["content"])
                    break
                except:
                    continue
        
        if ticket_info:
            if ticket_info["type"] == "BRAND_ASSURE_ENROLLMENT":
                print(f"{Colors.GREEN}Type:{Colors.RESET} Brand Assure Program Enrollment")
                print(f"{Colors.GREEN}Status:{Colors.RESET} {ticket_info['status']}")
                print(f"{Colors.GREEN}Program ID:{Colors.RESET} {ticket_info['enrollment']['program_id']}")
                print(f"{Colors.GREEN}Enrollment Link:{Colors.RESET} {ticket_info['enrollment']['enrollment_link']}")
                print(f"{Colors.GREEN}Listing ID:{Colors.RESET} {ticket_info['enrollment']['listing_id']}")
            else:
                print(f"{Colors.GREEN}Type:{Colors.RESET} Support Ticket")
                print(f"{Colors.GREEN}Ticket ID:{Colors.RESET} {ticket_info['ticket_id']}")
                print(f"{Colors.GREEN}Status:{Colors.RESET} {ticket_info['status']}")
                print(f"{Colors.GREEN}Ticket Type:{Colors.RESET} {ticket_info['data']['ticket_type']}")
                print(f"{Colors.GREEN}Listing ID:{Colors.RESET} {ticket_info['data']['listing_id']}")
                print(f"{Colors.GREEN}Reason Code:{Colors.RESET} {ticket_info['data']['reason_code']}")
        
        print(format_separator())

    # Start orchestration with the API handler
    orchestrate_conversation(
        listing_specialist=listing_specialist,
        user_proxy=user_proxy,
        api_agent=api_agent,
        ticket_agent=ticket_agent,
        api_handler=api_handler
    )

###############################################################################
# 6. Entry point
###############################################################################
if __name__ == "__main__":
    main() 