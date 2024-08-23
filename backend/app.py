from flask import Flask, request, jsonify
from services.pinecone_service import store_review, query_review
from services.scraping_service import scrape_professor_data
import openai
import os 
import uuid  # Import UUID library for generating unique IDs

app = Flask(__name__)

# Load your OpenAI API key from the environment
openai.api_key = os.getenv('OPENAI_API_KEY')


@app.route('/scrape-and-store', methods=['POST'])
def scrape_and_store():
    data = request.json
    link = data.get('link')
    try:
        professor_data = scrape_professor_data(link)
        # Store all the relevant information in Pinecone
        for review in professor_data['reviews']:
            unique_id = f"{professor_data['name']}-{uuid.uuid4()}"  # Generate a unique ID for each review
            store_review(
                unique_id,  # Use the unique ID instead of the professor's name as the identifier
                professor_data['name'],
                professor_data['department'],
                professor_data['school'],
                professor_data['overall_quality'],
                professor_data['would_take_again'],
                professor_data['level_of_difficulty'],
                review,
            )
        return jsonify({'success': True, 'professor': professor_data['name']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-professor-review', methods=['POST'])
def get_professor_review():
    data = request.json
    query_text = data.get('queryText')
    try:
        # Use the query text to find relevant reviews using Pinecone's embeddings
        matches = query_review(query_text)
        
        # Extract the text of the matching reviews from metadata
        reviews_by_professor = {}
        for match in matches:
            if 'metadata' in match:
                professor_name = match['metadata'].get('professor_name', 'Unknown')
                review_text = match['metadata'].get('review', '')
                
                if professor_name not in reviews_by_professor:
                    reviews_by_professor[professor_name] = []
                
                reviews_by_professor[professor_name].append(review_text)

        if not reviews_by_professor:
            return jsonify({'error': 'No relevant reviews found for the provided query.'}), 404

        # Analyze sentiment and summarize for each professor
        results = {}
        for professor, reviews in reviews_by_professor.items():
            combined_reviews = " ".join(reviews)
            
            sentiment_analysis_prompt = (
                f"Analyze the following reviews for Professor {professor} and provide a sentiment analysis and summary:\n\n"
                f"{combined_reviews}\n\n"
                "Sentiment Analysis: Positive, Neutral, or Negative?\nSummary:"
            )
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": sentiment_analysis_prompt},
                ],
                max_tokens=150
            )
            
            sentiment_summary = response['choices'][0]['message']['content'].strip()
            results[professor] = sentiment_summary
        
        # Return the sentiment analysis and summaries for each professor
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
