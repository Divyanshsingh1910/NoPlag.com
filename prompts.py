def get_solution_analysis_prompt(question, solution):
    """
    Generate a prompt for analyzing the solution and creating a detailed idea for rewriting.
    
    This prompt is critical for extracting the core concepts without plagiarizing the original style.
    """
    return f"""
I need to understand the approach used in a solution to an academic problem without copying the style.

PROBLEM:
{question}

ORIGINAL SOLUTION:
{solution}

I want you to analyze this solution in extreme detail and create a comprehensive step-by-step plan for 
solving this problem using a completely different approach and style. This plan should:

1. Identify the core concepts, algorithms, and techniques used in the original solution.
2. Propose a completely different style, structure, and approach that achieves the same result.
3. Include alternative variable names, function structures, and coding patterns (if it's code).
4. Suggest different explanations, metaphors, and examples (if it's written text).
5. Outline a step-by-step plan that someone could follow to create a new solution.
6. Make sure the new approach is technically correct but stylistically very different.
7. Be extremely detailed with the idea, explaining every step thoroughly.

Your output should be a comprehensive blueprint that someone could follow to create a new solution 
that would not be flagged by plagiarism detection tools while maintaining correctness.
"""

def get_solution_rewrite_prompt(question, solution_idea, solution_format):
    """
    Generate a prompt for rewriting the solution based on the detailed idea.
    
    This prompt focuses on creating a natural, student-like style that differs from the original.
    """
    
    base_prompt = f"""
I need to create a complete solution for an academic problem based on a detailed plan.

PROBLEM:
{question}

DETAILED SOLUTION PLAN:
{solution_idea}

Please create a complete solution following this plan exactly, but make it look like it was written by a student with these characteristics:
1. Uses informal language in comments/explanations
2. Has a unique and personal coding/writing style
3. May include some non-standard but valid approaches
4. Uses different variable names and structure than what might be conventional
5. Includes some personality in the solution (like personal notes or comments)
6. Makes the solution look organically created rather than polished and perfect
7. Avoids any academic or professional templates or structures that might appear in standard solutions

The solution must be TECHNICALLY CORRECT and solve the problem properly, but should look stylistically different from typical solutions.
"""

    if solution_format == 'code':
        return base_prompt + """
For this code solution, please ensure you:
1. Use unconventional but readable variable names
2. Add personal-style comments that reflect a student's thought process
3. Structure the code in a way that differs from standard patterns but remains functional
4. Include occasional informal notes/comments that a student might add while working
5. Make sure the code is fully working and correct, but stylistically unique
6. Don't make it look too clean or professional - add some character to it

Return ONLY the complete code solution without explanations before or after.
"""
    else:
        return base_prompt + """
For this written solution, please ensure you:
1. Use a conversational, first-person tone where appropriate
2. Avoid formal academic language patterns while maintaining correct content
3. Structure paragraphs and explanations in a unique way
4. Include occasional thought processes or asides that a student might include
5. Make sure all facts and analysis are correct, but presented in a personal style
6. Use metaphors or examples that are different from standard ones

Return ONLY the complete written solution without explanations before or after.
"""