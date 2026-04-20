from sqlalchemy.orm import Session
from app.services.analytics import get_dashboard_summary, revenue_by_country, top_products

def get_chat_response(query: str, db: Session) -> str:
    query = query.lower()
    
    # Fetch summary data for context
    summary = get_dashboard_summary(db)
    
    if "customer" in query and ("how many" in query or "count" in query or "number" in query):
        return f"We currently have {summary['customers']} registered customers in our system."
    
    if "order" in query and ("how many" in query or "count" in query or "number" in query):
        return f"There are a total of {summary['orders']} orders recorded so far."
    
    if "revenue" in query or "sales" in query or "money" in query:
        rev = f"${summary['salesRevenue']:,.2f}"
        if "total" in query:
            return f"The total sales revenue is {rev}."
        if "country" in query:
            countries = revenue_by_country(db)
            top = countries[0] if countries else None
            if top:
                return f"The top country by revenue is {top['label']} with ${top['value']:,.2f}."
        return f"Our current total revenue stands at {rev}."

    if "product" in query and ("top" in query or "best" in query or "popular" in query):
        products = top_products(db, limit=1)
        if products:
            p = products[0]
            return f"The most popular product is '{p['productName']}' with {p['quantityOrdered']} units ordered."

    if "hello" in query or "hi" in query:
        return "Hello! I'm the Classic Models Analytics assistant. How can I help you with our data today?"

    if "who are you" in query or "what can you do" in query:
        return "I can answer questions about our customers, orders, revenue, and top-performing products. Try asking 'What is our total revenue?'"

    return "I'm sorry, I don't have the data to answer that specific question. Try asking about total revenue, customer counts, or top products."
