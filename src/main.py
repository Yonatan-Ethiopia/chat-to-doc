def getConversationMessage(conversation):
    message = {}
    currentNode = conversation.current_node
    while currentNode != None:
        node = conversation.mapping[currentNode]
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
            else if authot == "system" and node['message']['metadata']['is_user_system_message']:
                author = "custom user info"
            
            if node['message']['content']['content_type'] == "text" or node['message']['content']['content_type'] == "multimodal_text"):
                parts = node['message']['content']["parts"]
                part = {}
                for i in parts:
                    if type(i) and len(i)>0:
                        part["text"] = i


