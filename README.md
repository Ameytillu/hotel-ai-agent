# Hotel Concierge AI Agent

**Hotel Concierge AI** is a multi-agent conversational system built with **Streamlit** and **OpenAI GPT-4o**.  
It acts as an intelligent hotel concierge — dynamically routing guest queries to specialized agents such as Booking, FAQs, Policies, Restaurant, Spa, and Shuttle.

**Try the live demo:**  
👉 [Hotel Concierge AI (Streamlit App)](https://hotel-ai-agent-c32sr8qb3jxacz8app7f36h.streamlit.app/)

---

## Features

- **Multi-Agent Architecture** — intelligently routes user queries to domain-specific agents (FAQ, Policy, Booking, etc.)  
- **RAG-Ready Structure** — modular design allows seamless integration of Retrieval-Augmented Generation later.  
- **Streamlit Chat Interface** — conversational UI for intuitive, human-like interaction.  
- **OpenAI API Powered** — uses GPT-4o for natural, context-aware responses.  
- **Modular & Extensible** — each agent (Python module) handles a specific function, making it easy to add more services.

---

## How It Works

1. **User sends a query** through the Streamlit chat interface.  
2. The **Router Agent** determines the intent and directs the query to the relevant agent:  
   - `faq_agent` → Handles hotel FAQs.  
   - `policy_agent` → Manages hotel policies (check-in/out, cancellations, etc.).  
   - `booking_agent` → Provides booking and availability details.  
   - `restaurant_agent` → Shares dining and menu information.  
   - `spa_agent` → Describes treatments and spa services.  
   - `shuttle_agent` → Gives shuttle timing and service info.  
3. If no match is found, the **General GPT agent** takes over to provide a helpful fallback response.  
4. Future-ready: the `rag_agent.py` is designed to integrate a RAG pipeline for semantic database retrieval.

---

## Future Developments -
- I am planning to develop this Agent further to help guest book room, services, shuttles and in return the Agent will send a booling confirmation email once the booking is done successfully. 
- As of now this project brings multiple Chatbots of different departments together and the router logic smartly transfers the user query to the concerned bot. 