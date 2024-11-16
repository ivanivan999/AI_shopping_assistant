# AI Shopping Assistant

An intelligent shopping assistant built with Flask and LangChain that provides natural language interactions for e-commerce operations.

## Features

- 🔍 Natural language product search
- 🛒 Shopping cart management
- 📦 Order tracking
- 💬 Conversational AI interface
- 🔒 Tool approval system
- 📱 Responsive web interface

## Tech Stack

- Flask (Web Framework)
- LangChain (LLM Integration)
- SQLite (Database)
- Bootstrap 5 (Frontend)
- Python 3.12+

## Project Structure
shopping_assistant/ 
├── app/ 
│ ├── models/ # Data operations 
│ ├── services/ # Business logic 
│ ├── utils/ # Helper functions 
│ ├── routes/ # API endpoints 
│ ├── static/ # Frontend assets 
│ └── templates/ # HTML templates 
├── data/ # Database files 
├── aibot.ipynb #Jupiter Book
├── config.py
├── run.py
├── createtable.py

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Initialize database:
```bash
python createtable.py
```
4. Run the application:
```bash
python run.py
```
## Usage Examples
### Product Search
"Show me wireless headphones under $300"
"Find products similar to Sony WH-1000XM4"

### Cart Management
"Add Bose QuietComfort to my cart"
"Remove AirPods from cart"

### Order Tracking
"Show my recent orders"
"What's the status of order #1234?"

## Jupyter Output
look out details in aibot_gernerate.txt

## Additional
In case the chatbox doesn't work, please check aibot.ipynb it's the same core, and also the output aibot_generate.txt from it.