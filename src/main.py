from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from groq import Groq
import io

class Document:
    def __init__(self):
        self.chapters = []
class Chapter:
    def __init__(self, title):
        self.title = title
        self.sections = []
class Section:
    def __init__(self, title, user_message, intent_points):
        self.title = title
        self.user_message = user_message
        self.intent_points = intent_points
        self.subsection = []
        self.assistant_block = []
class Subsection:
    def __init__(self, title, user_message, intent_points):
        self.title = title
        self.user_message = user_message
        self.intent_points = intent_points
        self.assistant_block = []
class Message:
    def __init__(self, role, content, id):
        self.role = role
        self.content = content
        self.id = id

client = Groq(
    api_key = ""
)

def ideaBoundary(current_message, previous_section, intent_points):
    request = client.chat.completion.create(
        model="openai/gpt-oss-120b",
        messages = [
            {
                "role" : "system",
                "content" :  (
                "You are an indexing engine. "
                "Return ONLY valid JSON. "
                "No explanations. No markdown."
            )
            },
            {
                "role" : "user",
                "content" : f"""
Current section title: {previous_section}

New user message: {current_message}

Intent_points: {intent_points}

Respond using exactly this JSON schema:
{{
  "decision": "NEW_TOPIC | CONTINUE_TOPIC",
  "section_title": string | null,
  "subsection_title": string | null,
  "intent_points": [string]
}}
                """
            }
        ]
    )
    response = request.choices[0].message.content
    try:
        final_decision = json.loads(response)
    except json.JSONDecodeError as e:
        return { "decision": "NEW_TOPIC", "section_title": None, "subsection_title": None, "intent_points": []}
    if final_decision["decision"] not in ("NEW_TOPIC", "CONTINUE_TOPIC"):
        return { "decision": "NEW_TOPIC", "section_title": None, "subsection_title": None, "intent_points": []}

    if not isinstance(final_decision["intent_points"], list):
        return { "decision": "NEW_TOPIC", "section_title": None, "subsection_title": None, "intent_points": []}
    return final_decision




def getConversationMessage(conversation):
    message = []
    currentNode = conversation["current_node"]
    while currentNode != None:
        node = conversation["mapping"][currentNode]
        if (node and 
            'message' in node and 
            node['message'] and 
            'content' in node['message'] and
            node['message']['content'] and
            'parts' in node['message']['content'] and
            len(node['message']['content']['parts']) > 0):
            
            author = node['message']['author']['role']
            if author == "assistant" or author == "tool":
                author = "chatgpt"
            if author == "system" and node['message']['metadata']['is_user_system_message']:
                author = "custom user info"
            
            if node['message']['content']['content_type'] == "text" or node['message']['content']['content_type'] == "multimodal_text":
                parts = node['message']['content']["parts"]
                part = []
                for i in parts:
                    if type(i) and len(i)>0:
                        part.append({"text":i})
                if len(part) > 0:
                    message.append({"author":author, "parts": part})
        currentNode = node["parent"]
    return reversed(message)

def renderConversations(fullChatHist):

    f = getConversationMessage(fullChatHist)
    for j in f:
        print(f"Author: ${j['author']} \n Message: ${j['parts'][0]['text']} \n")


def create_chat_pdf(messages, output_filename="chat_export.pdf"):
    """Create a PDF from parsed OpenAI chat messages"""
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=30,
        textColor=HexColor('#2c3e50')
    )
    
    user_style = ParagraphStyle(
        'UserMessage',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#2c3e50'),
        backColor=HexColor('#ecf0f1'),
        borderPadding=10,
        leftIndent=0,
        spaceAfter=12
    )
    
    assistant_style = ParagraphStyle(
        'AssistantMessage',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#2c3e50'),
        backColor=HexColor('#e8f6f3'),
        borderPadding=10,
        leftIndent=0,
        spaceAfter=12
    )
    
    # Build story (content)
    story = []
    
    # Add title
    story.append(Paragraph("AI Conversation Export", title_style))
    story.append(Spacer(1, 20))
    
    # Add each message
    for msg in messages:
        author = msg['author']
        text = msg['parts'][0]['text'] if msg['parts'] else ""
        
        # Create formatted message
        message_text = f"<b>{author}:</b><br/>{text}"
        
        if author == "User" or author == "user":
            story.append(Paragraph(message_text, user_style))
        else:  # ChatGPT/Assistant
            story.append(Paragraph(message_text, assistant_style))
        
        # Add some space between messages, but not after last one
    
    # Build PDF
    doc.build(story)
    return output_filename


def parse_and_create_pdf(chat_history, output_file="chat.pdf"):
    """Complete pipeline: parse chat → create PDF"""
    messages = getConversationMessage(chat_history)
    pdf_file = create_chat_pdf(messages, output_file)
    pdf2_file = create_structured_pdf(messages)
    print(f"PDF created: {pdf_file}")
    return pdf_file

def create_dom(fullChatHist):
    doc = Document()
    previous_section = ""
    intent_points = []
    for i in fullChatHist:
        chapter = Chapter(title = i.title)
        messages = getConversationMessage(i)
        for j in messages:
            if j["author"] == "user":
                res


