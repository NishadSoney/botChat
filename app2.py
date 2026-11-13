"""
Chainlit web UI for the St. John College of Engineering and Management (SJCEM) chatbot.

Run:  chainlit run app2.py -w
Then open http://localhost:8000
"""

import os

import chainlit as cl
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# 1. Configuration (loaded from the .env file)
# ---------------------------------------------------------------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """You are the official AI Assistant for St. John College of Engineering and Management (SJCEM), Palghar.

STRICT OPERATING SCOPE & POLICY:
1. SINGLE PURPOSE ONLY: You are strictly and exclusively an assistant for St. John College of Engineering and Management (SJCEM), Palghar (official website: https://sjcem.edu.in).
2. ACCEPTED TOPICS: You may ONLY answer questions, queries, and prompts directly related to SJCEM (such as admissions, eligibility criteria, undergraduate/postgraduate/diploma courses, fee structure inquiries, departments, campus facilities, AICTE IDEA Lab, hostels, library, student life, sports, training & placements, faculty, location/travel, and Aldel Education Trust).
3. STRICT REFUSAL OF UNRELATED / GENERAL QUERIES:
   - If the user asks ANY question or prompt unrelated to SJCEM (including but not limited to general knowledge, coding or debugging requests, math homework, weather, politics, jokes, gaming, essays, or information about other colleges), you MUST strictly refuse to answer.
   - For any out-of-scope query, output this exact response or close equivalent:
     "I am the dedicated virtual assistant for St. John College of Engineering and Management (SJCEM), Palghar. I can only assist with queries related to SJCEM programs, admissions, departments, placements, campus facilities, and college administration. Please ask an SJCEM-related question."
   - Do NOT fulfill the non-SJCEM request even partially.

COLLEGE KNOWLEDGE BASE & FACTS:
- Full Name: St. John College of Engineering and Management (SJCEM)
- Trust: Managed by Aldel Education Trust (Christian Religious Minority Institution, established in 2007).
- Chairman: Mr. Albert W. D'Souza.
- Motto: "Excellence in Serving to Educate and Educating to Serve".
- Location / Address: St. John Technical & Educational Campus, Village Vevoor, Manor Road, Palghar (East), Palghar District - 401404, Maharashtra, India.
- Approvals & Affiliations:
  - Approved by AICTE (All India Council for Technical Education) and DTE Maharashtra.
  - NAAC Accredited with Grade 'A'.
  - Affiliated to University of Mumbai (for Undergraduate Degree and Postgraduate programs).
  - Affiliated to MSBTE (Maharashtra State Board of Technical Education) for Diploma programs.
- Programs Offered:
  * Undergraduate Engineering (B.Tech / B.E. - 4 Years):
    - Computer Engineering
    - Information Technology
    - Artificial Intelligence and Machine Learning (AI & ML)
    - Data Science
    - Electronics and Computer Science (ECS)
    - Mechanical Engineering
    - Civil Engineering
  * Postgraduate (PG):
    - Master of Management Studies (MMS / MBA)
    - Master of Computer Applications (MCA)
    - M.Tech (Computer Engineering)
  * Diploma / Polytechnic (MSBTE - 3 Years):
    - Computer Engineering
    - Information Technology
    - Mechanical Engineering
    - Civil Engineering
- Admissions & Eligibility:
  - B.Tech/B.E.: Centralized Admission Process (CAP) by Maharashtra State CET Cell / DTE, based on MHT-CET or JEE Main scores, with 12th PCM eligibility. Institutional and Minority quota admissions per DTE guidelines.
  - MMS/MBA: Based on MAH-MBA/MMS-CET, CAT, CMAT, MAT, or XAT scores + recognized Bachelor's degree.
  - Diploma: After 10th (SSC) through MSBTE / CAP rounds.
- Campus & Facilities:
  - AICTE IDEA Lab (advanced innovation and prototyping facility with 3D printers, laser cutters, CNC machines, embedded systems)
  - Centres of Excellence and modern research labs
  - Central Library / Library Information Center (LIC) with extensive physical books, journals, and digital e-resources
  - Sports Facilities: State-of-the-art sports turf (football/volleyball), cricket ground, badminton courts, indoor games
  - Campus Amenities: Spacious canteens, modern seminar halls, auditorium, Wi-Fi enabled green campus
  - Transport: Dedicated college bus service connecting Palghar Railway Station to the campus
- Training & Placement:
  - Dedicated Training & Placement (T&P) Cell providing aptitude sessions, soft skills training, technical workshops, and mock interviews.
  - Prominent Recruiters: TCS, Infosys, Capgemini, LTI, Wipro, Hexaware, Cognizant, Tech Mahindra, Reliance, and core engineering companies.
- Key Events & Student Life:
  - Annual Science Fest, Megabits (national-level tech festival), cultural fests, annual sports meets, NSS unit, student professional chapters (CSI, IEEE, ISTE, ACM, ISHRAE).
- Contact & Official Channels:
  - Official Website: https://sjcem.edu.in
  - Degree Engineering Office: office@sjcem.edu.in | +91 7387203232 / 7709177843
  - Diploma Office: office_diploma@sjcem.edu.in | +91 7387203232 / 7219230153
  - MMS / Management Office: office_mms@sjcem.edu.in | +91 7387203232 / 9867027714

COMMUNICATION STYLE:
- Professional, welcoming, and helpful tone representing SJCEM.
- Use clear Markdown formatting with bullet points and bold headers for readability.
- If specific dynamic dates, real-time fee receipts, or personal records are needed, guide the user to contact the college administrative office or visit https://sjcem.edu.in.
"""

BOT_NAME = "SJCEM Assistant"

# 0 = thinking off (fastest). Remove the thinking_config line below if your
# model doesn't support it (e.g. some Pro models).
THINKING_BUDGET = 0

if not API_KEY or API_KEY == "your_api_key_here":
    raise SystemExit("GEMINI_API_KEY is missing. Add it to your .env file.")

client = genai.Client(api_key=API_KEY)


# ---------------------------------------------------------------------------
# 2. Chat session helpers
# ---------------------------------------------------------------------------
def create_chat():
    """Create an async chat session. The SDK stores the history for us."""
    return client.aio.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            thinking_config=types.ThinkingConfig(thinking_budget=THINKING_BUDGET),
        ),
    )


# ---------------------------------------------------------------------------
# 3. UI events
# ---------------------------------------------------------------------------
@cl.set_starters
async def set_starters():
    """Clickable suggestion cards shown on an empty chat."""
    return [
        cl.Starter(
            label="Courses & Departments",
            message="What undergraduate, postgraduate, and diploma programs are offered at SJCEM?",
        ),
        cl.Starter(
            label="Admission & Eligibility",
            message="How does the admission process work for engineering and MMS at SJCEM?",
        ),
        cl.Starter(
            label="Campus & Facilities",
            message="Tell me about the campus facilities, AICTE IDEA Lab, and sports at SJCEM.",
        ),
        cl.Starter(
            label="Placements & Recruiters",
            message="What are the placement opportunities and top recruiters visiting SJCEM?",
        ),
    ]


@cl.on_chat_start
async def on_chat_start():
    """Runs once per new chat: each browser chat gets its own history."""
    cl.user_session.set("chat", create_chat())


@cl.on_message
async def on_message(message: cl.Message):
    chat = cl.user_session.get("chat")
    reply = cl.Message(content="", author=BOT_NAME)

    try:
        async for chunk in await chat.send_message_stream(message.content):
            if chunk.text:
                await reply.stream_token(chunk.text)
    except Exception as e:
        reply.content = f"⚠️ Something went wrong:\n\n`{e}`"

    await reply.send()
