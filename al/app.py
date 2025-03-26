# from flask import Flask, request, jsonify
# import requests
 
# app = Flask(__name__)


# @app.route('/', methods=['POST'])
# def generate_prompt():
#     try:
#         # Get data from the frontend (form)
#         data = request.get_json()
 
#         product_url = data['productUrl']
#         product_title = data['productTitle']
#         product_description = data['productDescription']
#         primary_keyword = data['primaryKeyword']
#         secondary_keywords = data['secondaryKeywords']
#         intent = data['intent']
#         word_count = data['wordCount']
 
#         # Construct the prompt for ChatGPT
#         prompt = f"""
#             I want to write a product-specific blog.
 
#             Name of the product is {product_title}.
#             Product description is: {product_description}.
#             Keywords to target in the blog are: {secondary_keywords}.
#             Use {primary_keyword} as the primary keyword.
#             Write the blog in {word_count} words.
#             The intent for the article is {intent}.
#             Link of the product is {product_url}.
#         """
 
#         # Call ChatGPT API
        # api_key = "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"  # Replace with your actual API key
#         headers = {
#             "Authorization": f"Bearer {api_key}",
#             "Content-Type": "application/json",
#         }
#         chatgpt_url = "https://api.openai.com/v1/completions"
 
#         payload = {
#             "model": "gpt-3.5-turbo",  # You can use the appropriate model
#             "prompt": prompt,
#             "max_tokens": 1000,
#         }
 
#         # Send the prompt to the ChatGPT API
#         response = requests.post(chatgpt_url, headers=headers, json=payload)
#         response_data = response.json()
 
#         # Return the response from ChatGPT
#         if 'choices' in response_data:
#             return jsonify({
#                 'status': 'success',
#                 'generated_text': response_data['choices'][0]['text'].strip()
#             })
#         else:
#             return jsonify({'status': 'error', 'message': 'No valid response from ChatGPT API'})
 
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})
 
# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Serve index.html from the 'templates' folder

@app.route('/generate-prompt', methods=['POST'])
def generate_prompt():
    try:
        # Get data from the frontend (form)
        data = request.get_json()

        product_url = data['productUrl']
        product_title = data['productTitle']
        product_description = data['productDescription']
        primary_keyword = data['primaryKeyword']
        secondary_keywords = data['secondaryKeywords']
        intent = data['intent']
        word_count = data['wordCount']

        # Construct the prompt for ChatGPT
        prompt = f"""
            I want to write a product-specific blog.
            Name of the product is {product_title}.
            Product description is: {product_description}.
            Keywords to target in the blog are: {secondary_keywords}.
            Use {primary_keyword} as the primary keyword.
            Write the blog in {word_count} words.
            The intent for the article is {intent}.
            Link of the product is {product_url}.
        """

        # Call ChatGPT API
        api_key = "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"  # Replace with your actual API key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        chatgpt_url = "https://api.openai.com/v1/chat/completions"

        payload = {
            "model": "gpt-3.5-turbo",  # Use the appropriate model for chat completions
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1500,
    "temperature": 0.7  # Add temperature value (adjust as needed)
        }

        # Send the prompt to the ChatGPT API
        response = requests.post(chatgpt_url, headers=headers, json=payload)
        response_data = response.json()

        # Return the response from ChatGPT
        if 'choices' in response_data:
            return jsonify({
                'status': 'success',
                'generated_text': response_data['choices'][0]['message']['content'].strip()
            })
        else:
            return jsonify({'status': 'error', 'message': 'No valid response from ChatGPT API'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
