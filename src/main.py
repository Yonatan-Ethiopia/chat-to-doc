from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import io



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

