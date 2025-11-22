"""
Flask web application for the Multi-Agent Tourism System.
"""
from flask import Flask, render_template, request, jsonify
from agents.tourism_agent import TourismAgent
import sys

app = Flask(__name__)
agent = TourismAgent()

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process user query and return response."""
    try:
        data = request.get_json()
        user_input = data.get('query', '').strip()
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': 'Please enter a query.'
            }), 400
        
        # Process the query using the tourism agent
        response = agent.process_request(user_input)
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

