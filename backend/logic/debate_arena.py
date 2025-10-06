# debate_arena.py
import requests
import json
import time

# --- Configuration ---
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def run_debate(task_force_ids, event):
    """
    Orchestrates a multi-round debate between the selected AI agents with improved prompts.
    """
    print(f"\n--- 💬 DEBATE ARENA: Case #{event['event_id']} ({event['type']}) ---")
    print(f"--- Task Force: {', '.join(task_force_ids)} ---")

    # Create a simple, clear context for the debate
    case_context = f"A student is at-risk due to '{event['type']}' in the course '{event['details'].get('course', 'N/A')}'. The specific problem area is '{event['details'].get('topic', 'N/A')}'."
    debate_history = f"CONTEXT: {case_context}\n\n--- DEBATE LOG ---\n"
    
    # --- Round 1: Opening Statements ---
    print("\n📍 ROUND 1: Opening Statements")
    for agent_id in task_force_ids:
        agent_type = "Specialist" if agent_id in ['agent_001', 'agent_002'] else 'Generalist'

        # --- IMPROVED PROMPT ---
        prompt = f"""You are an AI assistant role-playing as '{agent_id}', an expert '{agent_type}'.
Your task is to propose the best single action to help a student.

CONTEXT: {case_context}

Based on your role, what is your opening argument for the best first step? Be concise and justify your reasoning in one or two sentences.

Your argument:"""
        
        payload = {"model": "phi3:mini", "prompt": prompt, "stream": False, "options": {"temperature": 0.7}}
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=300).json()
            argument = response.get('response', 'I am unable to provide a specific argument.').strip()
            
            print(f"🤖 {agent_id} ({agent_type}): \"{argument}\"")
            debate_history += f"Argument from {agent_id} ({agent_type}): {argument}\n"
            time.sleep(1)
            
        except Exception as e:
            print(f"  -> ❌ ERROR during debate for {agent_id}: {e}")

    # --- Round 2: Synthesis & Final Recommendation ---
    print("\n📍 FINAL ROUND: Synthesizing Recommendation")
    
    # --- IMPROVED SYNTHESIS PROMPT ---
    synthesis_prompt = f"""You are a Debate Moderator. Analyze the following arguments from different AI agents and create a single, unified, step-by-step action plan. Prioritize the most logical and impactful suggestions.

{debate_history}

Synthesize these arguments into a final, consensus-based recommendation with clear steps.

Final Recommendation:"""

    payload = {"model": "phi3:mini", "prompt": synthesis_prompt, "stream": False, "options": {"temperature": 0.5}}
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=300).json()
        final_recommendation = response.get('response', 'The agents could not reach a consensus.').strip()
        
        print(f"🎓 Moderator's Final Recommendation:\n{final_recommendation}")
        return final_recommendation
        
    except Exception as e:
        print(f"  -> ❌ ERROR during synthesis: {e}")
        return None