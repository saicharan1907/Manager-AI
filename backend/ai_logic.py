import os
import re
import json

# Try importing google.generativeai, but safely fallback to heuristics if not available/configured
try:
    import google.generativeai as genai
    has_ai_lib = True
except Exception as e:
    has_ai_lib = False

def get_genai_model():
    """Helper to get a configured model if available, else returns None"""
    if not has_ai_lib:
        return None
        
    # Check multiple common names in case of Vercel dashboard misconfiguration
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("API_KEY")
    
    if not api_key:
        return None
        
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def extract_inventory_action_heuristics(text: str):
    """Fallback logic if no AI is present to parse natural language"""
    text = text.lower()
    
    # Simple regex to find numbers
    qty_match = re.search(r'\d+', text)
    qty = int(qty_match.group()) if qty_match else 0
    
    action = "add"
    if any(word in text for word in ["sold", "removed", "shipped", "-"]):
        action = "subtract"
    elif any(word in text for word in ["set", "updated to"]):
        action = "set"
        
    # Extract item name by removing stop words and action words
    item_name = text
    stop_words = ["added", "sold", "removed", "shipped", "set", "updated", "to", "units", "of", "today", "yesterday", "we", "i", str(qty)]
    for word in stop_words:
        item_name = item_name.replace(word, "").strip()
        
    # clean up multiple spaces
    item_name = re.sub(r'\s+', ' ', item_name).strip().title()
    if not item_name:
        item_name = "Unknown Product"
        
    return {
        "action": action,
        "qty": qty,
        "item_name": item_name
    }

def analyze_natural_language_inventory(text: str):
    """
    Takes natural language like: 'Added 200 units of Fashion Accessories today'
    Returns dict: {'action': 'add', 'qty': 200, 'item_name': 'Fashion Accessories'}
    """
    model = get_genai_model()
    if model:
        try:
            prompt = f"""
            Extract the inventory update from this text.
            Text: "{text}"
            Return ONLY a valid JSON object with: 
            "action" (must be "add", "subtract", or "set")
            "qty" (integer)
            "item_name" (clean product name)
            """
            response = model.generate_content(prompt)
            # Find json block inside response
            match = re.search(r'\{.*\}', response.text.replace('\n', ''), re.IGNORECASE)
            if match:
                return json.loads(match.group())
        except Exception:
            pass # fallback
            
    return extract_inventory_action_heuristics(text)

def ask_business_query(query: str, data_context: str):
    """
    Answers business questions based on the JSON payload context of their dashboard.
    """
    try:
        model = get_genai_model()
        if not model:
            raise Exception("AI is not configured. Please set the GEMINI_API_KEY environment variable.")
            
        prompt = f"""
        You are a smart Data Analyst Assistant for an MSME business using the "Manager AI" platform.
        You must answer the user's question concisely and accurately, referencing the data below.
        Be helpful, friendly, and act as if you manage their inventory and sales operations.
        If they ask something far outside the scope of inventory/sales, politely guide them back.
        
        ==============
        LIVE BUSINESS DATA:
        {data_context}
        ==============
        
        Question: {query}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Service is currently warming up or unavailable. Error: {str(e)}. Context shows your top items:\n{data_context}"
