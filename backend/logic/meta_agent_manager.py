# meta_agent_manager.py
import json
import os
from datetime import datetime

# --- Configuration ---
AGENT_REGISTRY_FILE = 'data/agent_registry.json'

def load_registry():
    """Loads the agent registry from the JSON file."""
    try:
        with open(AGENT_REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"agents": [], "system_log": []}

def save_registry(registry_data):
    """Saves the updated registry data to the JSON file."""
    with open(AGENT_REGISTRY_FILE, 'w') as f:
        json.dump(registry_data, f, indent=4)

def log_system_event(event_message):
    """Adds a timestamped event to the system log."""
    registry = load_registry()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    registry.get('system_log', []).append({"timestamp": timestamp, "event": event_message})
    save_registry(registry)
    print(f"  -> Meta-Agent Log: {event_message}")

def update_agent_performance(agent_id, was_successful):
    """Updates an agent's stats and reputation after a case."""
    registry = load_registry()
    agent_found = False
    for agent in registry.get('agents', []):
        if agent['id'] == agent_id:
            agent['cases_handled'] += 1
            if was_successful:
                agent['successes'] += 1
                agent['reputation'] += 20 # Reward for success
            else:
                agent['reputation'] -= 15 # Penalty for failure
            
            # Calculate new success rate
            success_rate = (agent['successes'] / agent['cases_handled']) * 100 if agent['cases_handled'] > 0 else 0
            
            print(f"  -> Performance Updated for {agent_id}: Cases={agent['cases_handled']}, Success Rate={success_rate:.1f}%, Reputation={agent['reputation']}")
            agent_found = True
            break
            
    if agent_found:
        save_registry(registry)
    else:
        print(f"  -> ERROR: Could not find agent {agent_id} to update performance.")

# --- Test Block ---
if __name__ == "__main__":
    print("--- Testing Meta-Agent Manager ---")
    
    log_system_event("Running diagnostic test.")
    
    # Simulate a successful case for agent_002
    print("\nSimulating a successful case for the Resource Agent...")
    update_agent_performance('agent_002', was_successful=True)
    
    # Simulate a failed case for agent_003
    print("\nSimulating a failed case for the Communication Agent...")
    update_agent_performance('agent_003', was_successful=False)

    print("\n--- Test Complete ---")
    print(f"Check your '{AGENT_REGISTRY_FILE}' file to see the updated reputation scores.")