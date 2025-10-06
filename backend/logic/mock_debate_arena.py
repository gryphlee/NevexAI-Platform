# mock_debate_arena.py
import time

def run_mock_debate(task_force_ids, event):
    """
    Simulates a debate by returning a pre-written, hardcoded transcript and recommendation.
    This does NOT call any AI.
    """
    print(f"\n--- 💬 MOCK DEBATE ARENA: Case #{event['event_id']} ---")
    print(f"--- Task Force: {', '.join(task_force_ids)} ---")

    time.sleep(2) # Simulate the time it takes for the debate to happen

    # --- Round 1: Hardcoded Opening Statements ---
    print("\n📍 ROUND 1: Opening Statements")
    print("🤖 agent_002 (ResourceAgent): \"The student's low quiz scores in Calculus indicate a foundational gap. I recommend assigning targeted review modules immediately.\"")
    print("🤖 agent_001 (DataAnalyst): \"My analysis shows this is part of a 3-week decline in performance across all metrics, not just quizzes. The root cause may be external stressors.\"")
    print("🤖 agent_003 (CommunicationAgent): \"Agreed. An immediate, empathetic check-in is required before we assign more work, which could increase pressure.\"")
    
    time.sleep(1)

    # --- Final Round: Hardcoded Synthesis ---
    print("\n📍 FINAL ROUND: Synthesizing Recommendation")
    final_recommendation = """
    Based on the arguments, the consensus is to prioritize student well-being before academic intervention.
    
    **Final Plan:**
    1. **Immediate:** The Communication Agent will initiate the 'Day 1' outreach.
    2. **Monitor:** A Progress Tracker will monitor engagement for 48 hours.
    3. **Contingency:** If no engagement is detected, the Resource Agent will be cleared to assign the Calculus review modules.
    """
    print(f"🎓 Moderator's Final Recommendation:\n{final_recommendation}")
    
    return final_recommendation