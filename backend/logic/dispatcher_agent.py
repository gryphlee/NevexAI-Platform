import pandas as pd
import json
import random
import time
from sqlalchemy import create_engine, text
from datetime import datetime
import os
from mock_debate_arena import run_mock_debate # <-- IMPORT THE MOCK FUNCTION
from meta_agent_manager import log_system_event, update_agent_performance

# --- Configuration ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
DB_PATH = os.path.join(ROOT_DIR, 'university.db')
DB_URI = f'sqlite:///{DB_PATH}'
AGENT_REGISTRY_FILE = os.path.join(ROOT_DIR, 'data', 'agent_registry.json')

# --- Helper Functions ---
def load_registry():
    """Loads the agent registry from the JSON file."""
    try:
        with open(AGENT_REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"agents": [], "system_log": []}

def get_new_events(engine):
    """Fetches new events from the event bus table."""
    try:
        query = "SELECT * FROM events WHERE status = 'new'"
        with engine.connect() as connection:
            events_df = pd.read_sql(query, connection)
        return events_df
    except Exception as e:
        print(f"  -> ERROR fetching new events: {e}")
        return pd.DataFrame()

def update_event_status(engine, event_id, new_status):
    """Updates the status of an event in the database."""
    try:
        with engine.connect() as connection:
            update_query = text("UPDATE events SET status = :status WHERE event_id = :event_id")
            connection.execute(update_query, {"status": new_status, "event_id": event_id})
            connection.commit()
        print(f"  -> Event {event_id} status updated to '{new_status}'.")
    except Exception as e:
        print(f"  -> ERROR updating event status: {e}")

# --- Agent Bidding Logic ---
def run_bidding_process(event):
    """Simulates agents bidding on a new case."""
    registry = load_registry()
    active_agents = [agent for agent in registry.get('agents', []) if agent.get('status') == 'active']
    
    bids = []
    print(f"\n--- 📢 Agent Bidding in Progress for Event: {event['event_id']} ---")

    for agent in active_agents:
        bid_score = 0
        if agent['type'] == 'ResourceAgent' and 'score' in event['event_type']: bid_score += 40
        if agent['type'] == 'CommunicationAgent' and 'attendance' in event['event_type']: bid_score += 40
        if agent['type'] == 'DataAnalyst': bid_score += 25
        
        reputation_boost = (agent.get('reputation', 500) - 500) / 10
        bid_score += reputation_boost
        bid_score += random.randint(-5, 5)

        if bid_score > 10:
             bids.append({"agent_id": agent['id'], "type": agent['type'], "score": bid_score})

    sorted_bids = sorted(bids, key=lambda x: x['score'], reverse=True)
    
    for bid in sorted_bids:
        print(f"  - Bid from {bid['agent_id']} ({bid['type']}): Score = {bid['score']:.1f}")
            
    return sorted_bids

def assemble_task_force(bids, num_agents=3):
    """Selects the top bidders to form a task force."""
    if not bids: return []
    top_bidders = bids[:num_agents]
    task_force_ids = [bid['agent_id'] for bid in top_bidders]
    print(f"\n--- ✅ Top {len(task_force_ids)} Selected for Task Force ---")
    print(f"  Members: {', '.join(task_force_ids)}")
    return task_force_ids

# --- Main Dispatcher Logic ---
def run_dispatcher_cycle():
    """Runs a single cycle of the dispatcher agent."""
    print("\n-------------------------------------------")
    print(f"🤖 Dispatcher Agent: Checking for new events... ({datetime.now().strftime('%H:%M:%S')})")
    
    engine = create_engine(DB_URI)
    new_events_df = get_new_events(engine)
    
    if new_events_df.empty:
        print("No new events on the Event Bus.")
        return
        
    current_event = new_events_df.iloc[0]
    update_event_status(engine, current_event['event_id'], 'in_progress')

    bids = run_bidding_process(current_event)
    task_force = assemble_task_force(bids)
    
    if task_force:
        log_system_event(f"Task Force {task_force} assembled for Event {current_event['event_id']}.")
        
        # --- INTEGRATION POINT ---
        final_plan = run_mock_debate(task_force, current_event)
        
        # --- UPDATE REPUTATION (The Feedback Loop) ---
        if final_plan:
            print("\n--- 📈 Updating Agent Reputations (Simulated Success) ---")
            update_event_status(engine, current_event['event_id'], 'resolved')
            for agent_id in task_force:
                update_agent_performance(agent_id, was_successful=True)
        else:
            print("\n--- 📉 Updating Agent Reputations (Simulated Failure) ---")
            update_event_status(engine, current_event['event_id'], 'failed')
            for agent_id in task_force:
                update_agent_performance(agent_id, was_successful=False)
    else:
        update_event_status(engine, current_event['event_id'], 'new')

if __name__ == "__main__":
    print("🚀 Dispatcher Agent is now LIVE. It will check for new events every 10 seconds.")
    print("Press Ctrl+C to stop.")
    
    while True:
        try:
            run_dispatcher_cycle()
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n🛑 Dispatcher Agent stopped by user.")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            time.sleep(30)