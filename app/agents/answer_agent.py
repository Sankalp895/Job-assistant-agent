from app.models import JobDescription, UserProfile

class AnswerAgent:
    def __init__(self, llm_provider=None):
        self.llm = llm_provider

    async def generate_answer(self, question: str, jd: JobDescription, profile: UserProfile) -> str:
        # Data Science Logic: We feed the AI the 'Work History' and 'Skills' separately
        work_context = ""
        for exp in profile.work_history[:2]: # Use top 2 experiences
            work_context += f"- {exp.role} at {exp.company}: {exp.description}\n"

        prompt = f"""
Role: Professional Career Coach & Ghostwriter.
Task: Write a personalized response to a specific application question.

APPLICATION QUESTION: {question}
TARGET JOB: {jd.title} at {jd.company}
USER SKILLS: {", ".join(profile.skills)}
USER EXPERIENCE:
{work_context}

INSTRUCTIONS:
1. Use the STAR Method (Situation, Task, Action, Result).
2. Connect a specific skill from the USER SKILLS list to a requirement in the JOB DESCRIPTION.
3. Tone: Professional, ambitious, and concise.
4. Length: 100-150 words.
5. Avoid generic phrases like "I am a hard worker." Use "I demonstrated [Skill] by [Action]."

Answer:
"""
        if not self.llm:
            return "AI Client not configured."

        # The AI Client returns a raw string (the answer)
        response = await self.llm.chat(prompt)
        return response.strip()