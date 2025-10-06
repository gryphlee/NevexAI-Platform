# resource_matcher.py
import json

RESOURCES_FILE = 'data/resources.json'

def load_resources():
    """Loads resources from the JSON file."""
    try:
        with open(RESOURCES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def find_best_resources(student_data, max_results=3):
    """
    Finds the best matching resources for a given student's needs
    based on a tag-scoring system.
    """
    resources = load_resources()
    if not resources:
        return []

    # --- Define the student's needs based on their data ---
    # In a more advanced system, this could be dynamically generated.
    # For now, we'll derive needs from their department, year, and a problem.
    student_needs = set()
    problem = "low_quiz_scores" # We can make this dynamic later
    
    if student_data.get('department'):
        student_needs.add(student_data['department'].lower())
    if student_data.get('year_level'):
        # e.g., "1st Year" -> "1st", "year"
        student_needs.update(student_data['year_level'].lower().split())
    if problem:
        # We can create tags for problems, e.g., "quiz", "assignment"
        student_needs.add("quiz") # Assuming low scores are quiz-related
        
    # Example: student_needs might be {'it', '1st', 'year', 'quiz'}
    
    # --- Score each resource based on matching tags ---
    scored_resources = []
    for resource in resources:
        score = 0
        resource_tags = set(tag.lower().strip() for tag in resource.get('tags', []))
        
        # The score is the number of tags that match the student's needs
        matching_tags = student_needs.intersection(resource_tags)
        score = len(matching_tags)
        
        if score > 0:
            scored_resources.append({'resource': resource, 'score': score})

    # --- Sort resources by score (highest first) and return the top results ---
    if not scored_resources:
        return []
        
    sorted_resources = sorted(scored_resources, key=lambda x: x['score'], reverse=True)
    
    # Return just the resource dictionaries, not the scores
    top_resources = [item['resource'] for item in sorted_resources]
    
    return top_resources[:max_results]

# --- Example of how to use this script (for testing) ---
if __name__ == '__main__':
    # Simulate a student who is struggling
    test_student = {
        'student_id': '2025999',
        'department': 'IT',
        'year_level': '4th Year',
        'quiz_avg': 55
    }
    
    print(f"Finding best resources for a student from the {test_student['department']} department...")
    
    best_matches = find_best_resources(test_student)
    
    if best_matches:
        print("\n--- Top Matches Found ---")
        for i, match in enumerate(best_matches):
            print(f"{i+1}. {match['title']} (Tags: {', '.join(match['tags'])})")
    else:
        print("\n--- No relevant resources found. ---")