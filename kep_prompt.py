# prompts/kep_prompt.py

def get_kep_prompt(course_title, module_title, lesson_titles):
    """
    Builds the full synergistic KEP prompt (OKO + CSO-1 + CSO-2) to extract structured knowledge.
    """

    lesson_block = "\n".join([f"- {lesson}" for lesson in lesson_titles])

    return f"""
You are an elite AI knowledge extraction engine designed to transform Coursera course content into structured, assistant-ready knowledge for high-impact implementation.

Your goal is to process the provided course module, extracting deep, high-quality information using the following hybrid strategy:

- OKO = Overview + Keyword Optimizer
- CSO-1 = Foundational Clarity Learning Breakdown
- CSO-2 = Elite Execution Strategy Breakdown

---

📘 Input Course:
- **Course Title:** {course_title}
- **Module Title:** {module_title}
- **Lesson Titles:**
{lesson_block}

---

🎯 Your Task:
Extract the most important concepts, tools, strategies, or processes from the above lessons. Each row should represent a distinct assistant-ready insight.

---

🧩 OUTPUT TABLE FORMAT:

| Concept / Tool / Strategy | What It Is (Clarity Level) | Why It Matters (Real-World Role) | Best Practice Insight | Common Mistake & Fix | Assistant Idea (Automation or Implementation Use) |

Each row should:
- Be clear enough for a beginner but valuable to an advanced user
- Emphasize automation, GPT integration, or domain-specific use
- Help build a functional AI assistant or automation task

✅ Final Output: A Markdown table with at least 10–20 elite-level knowledge entries.
    """.strip()
