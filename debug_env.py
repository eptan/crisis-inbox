"""Debug script to inspect environment response format."""
import sys
sys.path.insert(0, r'C:\Users\smrit\CascadeProjects\crisis-inbox-test')

from crisis_inbox import CrisisInboxEnv

with CrisisInboxEnv(base_url="https://eptan-crisis-inbox.hf.space") as env:
    env.reset()
    
    # List available tools
    tools = env.list_tools()
    print(f"Available tools ({len(tools)}):")
    for t in tools:
        print(f"  - {t.name}: {t.description[:60]}...")
    
    # Get inbox and inspect
    print("\n--- Calling get_inbox ---")
    inbox = env.call_tool("get_inbox")
    print(f"Type: {type(inbox)}")
    print(f"Content preview: {str(inbox)[:500]}")
    
    # Try to get a specific message
    print("\n--- Trying read_message ---")
    try:
        msg = env.call_tool("read_message", message_id="msg_001")
        print(f"Type: {type(msg)}")
        print(f"Content: {str(msg)[:300]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Try status
    print("\n--- Calling get_status ---")
    try:
        status = env.call_tool("get_status")
        print(f"Type: {type(status)}")
        print(f"Content: {str(status)[:300]}")
    except Exception as e:
        print(f"Error: {e}")
