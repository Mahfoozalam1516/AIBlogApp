import os
import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv
import requests
import time

# Load .env variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

# Configure Gemini
genai.configure(api_key="AIzaSyBQi4LrGW9pFirEiTnFw3RONXz39nUpghQ")  # Or paste your key directly for testing
# HIX API Configuration
HIX_API_KEYY = "71b72a19738541f28fbe02460335e12c"  # Store your HIX API key in .env
HIX_API_ENDPOINT = "https://api.hix.ai/v1/humanize"  # Replace with actual HIX API endpoint

# Two different models for different tasks
blog_generation_model = genai.GenerativeModel("gemini-1.5-flash")
grammar_improvement_model = genai.GenerativeModel("gemini-1.5-flash")

import os
import requests
import time

def split_text_into_chunks(text, max_words=500):
    """
    Split text into chunks of approximately max_words.
    
    Args:
        text (str): Input text to be split
        max_words (int): Maximum number of words per chunk
    
    Returns:
        list: List of text chunks
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_word_count = 0

    for word in words:
        current_chunk.append(word)
        current_word_count += 1

        if current_word_count >= max_words:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_word_count = 0

    # Add any remaining words
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def humanize_chunk(chunk, api_key="71b72a19738541f28fbe02460335e12c"):
    """
    Humanize a single text chunk.
    
    Args:
        chunk (str): Text chunk to humanize
        api_key (str): HIX API key
    
    Returns:
        str: Humanized chunk or original chunk if humanization fails
    """
    # API endpoints
    SUBMIT_URL = "https://bypass.hix.ai/api/hixbypass/v1/submit"
    OBTAIN_URL = "https://bypass.hix.ai/api/hixbypass/v1/obtain"

    # Headers for API requests
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    # Payload for submission
    submit_payload = {
        "input": chunk,
        "mode": "Balanced"
    }

    try:
        # Submit humanization task
        submit_response = requests.post(SUBMIT_URL, json=submit_payload, headers=headers)
        submit_response.raise_for_status()
        submit_data = submit_response.json()

        # Check for submission errors
        if submit_data.get('err_code') != 0:
            print(f"Submission Error: {submit_data.get('err_msg', 'Unknown error')}")
            return chunk

        # Extract task ID
        task_id = submit_data['data']['task_id']

        # Poll for task result
        max_attempts = 10
        for _ in range(max_attempts):
            time.sleep(2)

            # Obtain task result
            obtain_response = requests.get(
                OBTAIN_URL, 
                params={"task_id": task_id}, 
                headers=headers
            )
            obtain_response.raise_for_status()
            obtain_data = obtain_response.json()

            # Check if task is complete
            if obtain_data.get('err_code') == 0 and obtain_data['data'].get('task_status'):
                return obtain_data['data'].get('output', chunk)

        # Timeout error
        print("Humanization task timed out")
        return chunk

    except Exception as e:
        print(f"Humanization Error for chunk: {e}")
        return chunk

def humanize_text(text, max_words=500):
    """
    Humanize text by processing it in chunks.
    
    Args:
        text (str): Text to be humanized
        max_words (int): Maximum words per chunk
    
    Returns:
        str: Humanized text
    """
    # Validate input
    if not text or len(text.split()) < 50:
        return text

    # Get API key from environment
    api_key = "71b72a19738541f28fbe02460335e12c"
    if not api_key:
        print("Error: HIX API Key not set in environment variables")
        return text

    # Split text into chunks
    chunks = split_text_into_chunks(text, max_words)

    # Humanize each chunk
    humanized_chunks = []
    for chunk in chunks:
        humanized_chunk = humanize_chunk(chunk, api_key)
        humanized_chunks.append(humanized_chunk)

    # Reassemble humanized chunks
    return ' '.join(humanized_chunks)
    
def improve_grammar_and_readability(content, primary_keywords, secondary_keywords):
    """
    Improve the grammar, clarity, and readability of the generated blog content.

    Args:
        content (str): The original generated blog content
        primary_keywords (str): Comma-separated primary keywords
        secondary_keywords (str): Comma-separated secondary keywords

    Returns:
        str: Improved, more polished blog content
    """
    improvement_prompt = f"""Please review and improve the following text.
    Focus on:
    - Make sure the primary keywords are used only 4-5 times in whole blog: {primary_keywords}
    - Make sure each secondary keyword is only used at least once in whole blog: {secondary_keywords}
    - Correcting grammar and spelling errors
    - Enhancing sentence structure and flow
    - Improving clarity and readability
    - Maintaining the original tone and meaning
    - Breaking up long sentences
    - Using more engaging and precise language
    - Ensuring professional and conversational style

    Original Text:
    {content}

    Provide the improved version of the text."""

    try:
        response = grammar_improvement_model.generate_content(improvement_prompt)
        improved_content = response.text
        return improved_content
    except Exception as e:
        print(f"Grammar improvement error: {e}")
        return content  # Return original content if improvement fails

def generate_blog_outline(product_url, product_title, product_description,
                          primary_keywords, secondary_keywords, intent):
    prompt = f"""Create a comprehensive and detailed blog outline for a product blog with the following details:

Product URL: {product_url}
Product Title: {product_title}
Product Description: {product_description}
Primary Keywords: {primary_keywords}
Secondary Keywords: {secondary_keywords}
Search Intent: {intent}

Outline Requirements:
1. Introduction:
   - Compelling hook related to the product's unique value proposition
   - Brief overview of the product and its significance
   - Problem the product solves
   - Include a captivating anecdote or statistic to engage readers

2. Product Overview:
   - Detailed breakdown of product features
   - Unique selling points
   - Technical specifications
   - How it differs from competitors
   - Include sub-sections for each major feature

3. Use Cases and Applications:
   - Specific scenarios where the product excels
   - Target audience and their pain points
   - Real-world examples or potential applications
   - Include case studies or success stories if available

4. Benefits and Advantages:
   - Comprehensive list of benefits
   - Quantifiable improvements or advantages
   - Customer-centric perspective on product value
   - Include testimonials or reviews to support claims

5. Practical Insights:
   - Implementation tips
   - Best practices for using the product
   - Potential challenges and solutions
   - Include step-by-step guides or tutorials

6. Conclusion:
   - Recap of key product highlights
   - Clear call-to-action
   - Future potential or upcoming features
   - Include a final thought or reflection to leave a lasting impression

Additional Guidance:
- Ensure the outline is informative and engaging
- Incorporate keywords naturally and frequently throughout the blog
- Focus on solving customer problems
- Maintain a balanced, objective tone
- Highlight unique aspects of the product
- Provide detailed sub-points under each main section to elaborate on the content
"""
    response = blog_generation_model.generate_content(prompt)
    return response.text

def generate_blog_content(outline, product_url, product_title, product_description,
                          primary_keywords, secondary_keywords, intent):
    sections = outline.split('\n\n')
    blog_content = []
    all_keywords = primary_keywords.split(", ") + secondary_keywords.split(", ")
    keyword_usage = {keyword: 0 for keyword in all_keywords}
    primary_keyword_target = 3  # Reduced from 5 to 3 times
    secondary_keyword_target = 1  # Target usage for secondary keywords

    for i, section in enumerate(sections):
        previous_text = ' '.join(blog_content) if i > 0 else 'None'

        primary_keywords_instruction = (
            "\n- Use primary keywords sparingly and naturally, aiming for no more than 3 total uses across the entire blog: "
            + ', '.join(primary_keywords.split(", ")) +
            ". Ensure the usage is contextually relevant and not forced."
        )

        secondary_keywords_instruction = (
            "\n- Use each of the following secondary keywords approximately **1 time** throughout the entire blog: "
            + ', '.join(secondary_keywords.split(", ")) +
            ". Make the usage natural and contextually relevant."
        )

        section_prompt = f"""Generate a detailed section for a blog post while ensuring no repetition.

Section Outline:
{section}

Product Details:
- Product URL: {product_url}
- Product Title: {product_title}
- Product Description: {product_description}
- Search Intent: {intent}

Guidelines:
- Word count for this section: Approximately {1200 // len(sections)} words
- Avoid repeating points from previous sections
- Focus on new insights, examples, and fresh perspectives
- Ensure smooth transitions from previous sections
- Maintain a professional and engaging tone{primary_keywords_instruction}{secondary_keywords_instruction}

Previous Sections Summary:
{previous_text}

Generate the content for this section."""

        response = blog_generation_model.generate_content(section_prompt)
        section_content = response.text

        # Update keyword usage count
        for keyword in all_keywords:
            keyword_usage[keyword] += section_content.lower().count(keyword.lower())

        blog_content.append(section_content)

    # Ensure primary keywords are used no more than 3 times and secondary keywords are used once
    for keyword, count in keyword_usage.items():
        if keyword in primary_keywords.split(", ") and count > primary_keyword_target:
            # Remove excess mentions by regenerating content or adjusting references
            blog_content = [section.replace(keyword, f"**{keyword}**", count - primary_keyword_target) for section in blog_content]
        elif keyword in secondary_keywords.split(", ") and count < secondary_keyword_target:
            additional_content = f"Moreover, {keyword} is an important aspect to consider."
            blog_content.append(additional_content)
            keyword_usage[keyword] += 1

    # Combine content and improve grammar and readability
    final_content = '\n\n'.join(blog_content)
    improved_content = improve_grammar_and_readability(final_content, primary_keywords, secondary_keywords)
    return improved_content

def generate_general_blog_outline(keywords, primary_keywords, prompt):
    outline_prompt = f"""Create a comprehensive and detailed blog outline based on the following details:

Keywords: {keywords}
Primary Keywords: {primary_keywords}
Prompt: {prompt}

Outline Requirements:
1. Introduction:
   - Compelling hook related to the main topic
   - Brief overview of the topic and its significance
   - Problem the blog addresses
   - Include a captivating anecdote or statistic to engage readers

2. Main Sections:
   - Detailed breakdown of the main points
   - Unique insights or perspectives
   - Include sub-sections for each major point

3. Use Cases and Applications:
   - Specific scenarios where the topic is relevant
   - Target audience and their pain points
   - Real-world examples or potential applications
   - Include case studies or success stories if available

4. Benefits and Advantages:
   - Comprehensive list of benefits
   - Quantifiable improvements or advantages
   - Customer-centric perspective on the topic's value
   - Include testimonials or reviews to support claims

5. Practical Insights:
   - Implementation tips
   - Best practices related to the topic
   - Potential challenges and solutions
   - Include step-by-step guides or tutorials

6. Conclusion:
   - Recap of key points
   - Clear call-to-action
   - Future potential or upcoming trends
   - Include a final thought or reflection to leave a lasting impression

Additional Guidance:
- Ensure the outline is informative and engaging
- Incorporate keywords naturally and frequently throughout the blog
- Focus on solving reader problems
- Maintain a balanced, objective tone
- Highlight unique aspects of the topic
- Provide detailed sub-points under each main section to elaborate on the content
"""
    response = blog_generation_model.generate_content(outline_prompt)
    return response.text

def generate_general_blog_content(outline, keywords, primary_keywords, prompt):
    sections = outline.split('\n\n')
    blog_content = []
    all_keywords = primary_keywords.split(", ") + keywords.split(", ")
    keyword_usage = {keyword: 0 for keyword in all_keywords}
    primary_keyword_target = 3  # Target usage for primary keywords
    secondary_keyword_target = 1  # Target usage for secondary keywords

    for i, section in enumerate(sections):
        previous_text = ' '.join(blog_content) if i > 0 else 'None'

        primary_keywords_instruction = (
            "\n- Use primary keywords sparingly and naturally, aiming for no more than 3 total uses across the entire blog: "
            + ', '.join(primary_keywords.split(", ")) +
            ". Ensure the usage is contextually relevant and not forced."
        )

        secondary_keywords_instruction = (
            "\n- Use each of the following secondary keywords approximately **1 time** throughout the entire blog: "
            + ', '.join(keywords.split(", ")) +
            ". Make the usage natural and contextually relevant."
        )

        section_prompt = f"""Generate a detailed section for a blog post while ensuring no repetition.

Section Outline:
{section}

Guidelines:
- Word count for this section: Approximately {1200 // len(sections)} words
- Avoid repeating points from previous sections
- Focus on new insights, examples, and fresh perspectives
- Ensure smooth transitions from previous sections
- Maintain a professional and engaging tone{primary_keywords_instruction}{secondary_keywords_instruction}

Previous Sections Summary:
{previous_text}

Generate the content for this section."""

        response = blog_generation_model.generate_content(section_prompt)
        section_content = response.text

        # Update keyword usage count
        for keyword in all_keywords:
            keyword_usage[keyword] += section_content.lower().count(keyword.lower())

        blog_content.append(section_content)

    # Ensure primary keywords are used no more than 3 times and secondary keywords are used once
    for keyword, count in keyword_usage.items():
        if keyword in primary_keywords.split(", ") and count > primary_keyword_target:
            # Remove excess mentions by regenerating content or adjusting references
            blog_content = [section.replace(keyword, f"**{keyword}**", count - primary_keyword_target) for section in blog_content]
        elif keyword in keywords.split(", ") and count < secondary_keyword_target:
            additional_content = f"Moreover, {keyword} is an important aspect to consider."
            blog_content.append(additional_content)
            keyword_usage[keyword] += 1

    # Combine content and improve grammar and readability
    final_content = '\n\n'.join(blog_content)
    
    # Fix here: use 'keywords' instead of 'secondary_keywords' in this call
    improved_content = improve_grammar_and_readability(final_content, primary_keywords, keywords)
    return improved_content
# HTML templates
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Blog Generator Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script>
        function showForm(type) {
            document.getElementById('product-form-container').style.display = 'none';
            document.getElementById('general-form-container').style.display = 'none';
            if (type === 'product') {
                document.getElementById('product-form-container').style.display = 'block';
            } else if (type === 'general') {
                document.getElementById('general-form-container').style.display = 'block';
            }
        }
    </script>
</head>
<body class="bg-gradient-to-br from-gray-100 to-gray-200 min-h-screen flex items-center justify-center p-4">
    <div class="container mx-auto max-w-5xl bg-white rounded-2xl shadow-2xl overflow-hidden">
        <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-8">
            <h1 class="text-4xl font-extrabold mb-4 text-center text-white drop-shadow-lg">Blog Generator Dashboard</h1>
            <p class="text-center text-white opacity-80">Create compelling blog content with ease</p>
        </div>

        <div class="p-8">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                <div onclick="showForm('product')" class="group cursor-pointer p-6 bg-white border-2 border-transparent rounded-xl shadow-lg hover:border-blue-500 hover:shadow-2xl transition-all duration-300 ease-in-out transform hover:-translate-y-2">
                    <div class="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mb-4 group-hover:bg-blue-200 transition">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                        </svg>
                    </div>
                    <h2 class="text-2xl font-bold mb-2 text-gray-800 group-hover:text-blue-600 transition">Product-Specific Blog</h2>
                    <p class="text-gray-600 group-hover:text-gray-800 transition">Generate a blog tailored to a specific product using keywords and descriptions.</p>
                </div>
                <div onclick="showForm('general')" class="group cursor-pointer p-6 bg-white border-2 border-transparent rounded-xl shadow-lg hover:border-purple-500 hover:shadow-2xl transition-all duration-300 ease-in-out transform hover:-translate-y-2">
                    <div class="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mb-4 group-hover:bg-purple-200 transition">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                        </svg>
                    </div>
                    <h2 class="text-2xl font-bold mb-2 text-gray-800 group-hover:text-purple-600 transition">General Blog</h2>
                    <p class="text-gray-600 group-hover:text-gray-800 transition">Create general blogs for topics or industries.</p>
                </div>
            </div>

            <div id="product-form-container" style="display:none;" class="bg-white p-8 rounded-xl shadow-lg border border-gray-100">
                <h2 class="text-2xl font-bold mb-6 text-center text-blue-600">Generate Product Blog</h2>
                <form method="POST" action="/" class="space-y-4">
                    <div class="group">
                        <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Product URL</label>
                        <input type="text" name="product_url" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
                    </div>
                    <div class="group">
                        <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Product Title</label>
                        <input type="text" name="product_title" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
                    </div>
                    <div class="group">
                        <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Product Description</label>
                        <textarea name="product_description" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition" rows="4"></textarea>
                    </div>
                    <div class="group">
                        <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Primary Keywords</label>
                        <input type="text" name="primary_keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
                    </div>
                    <div class="group">
                        <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Secondary Keywords</label>
                        <input type="text" name="secondary_keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
                    </div>
                    <div class="group">
                        <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Search Intent</label>
                        <input type="text" name="intent" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
                    </div>
                    <button type="submit" class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white p-3 rounded-lg hover:from-blue-600 hover:to-purple-700 transition duration-300 ease-in-out transform hover:scale-105 hover:shadow-lg">
                        Generate Blog
                    </button>
                </form>
            </div>

            <div id="general-form-container" style="display:none;" class="bg-white p-8 rounded-xl shadow-lg border border-gray-100">
                <h2 class="text-2xl font-bold mb-6 text-center text-purple-600">Generate General Blog</h2>
                <form method="POST" action="/general" class="space-y-4">
                    <div class="group">
                        <label class="block mb-2 text-gray-700 group-hover:text-purple-600 transition">Keywords</label>
                        <input type="text" name="keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition">
                    </div>
                    <div class="group">
                        <label class="block mb-2 text-gray-700 group-hover:text-purple-600 transition">Primary Keywords</label>
                        <input type="text" name="primary_keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition">
                    </div>
                    <div class="group">
                        <label class="block mb-2 text-gray-700 group-hover:text-purple-600 transition">Prompt</label>
                        <textarea name="prompt" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition" rows="4"></textarea>
                    </div>
                    <button type="submit" class="w-full bg-gradient-to-r from-purple-500 to-blue-600 text-white p-3 rounded-lg hover:from-purple-600 hover:to-blue-700 transition duration-300 ease-in-out transform hover:scale-105 hover:shadow-lg">
                        Generate Blog
                    </button>
                </form>
            </div>
        </div>
    </div>
</body>
</html>
'''

# Updated HTML template to include humanization button and editable content
RESULT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Blog Generation Result</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script>
        function humanizeBlog() {
            fetch('/humanize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: document.getElementById('blog-content').textContent
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('humanized-content').textContent = data.humanized_content;
                document.getElementById('humanize-section').style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to humanize the blog');
            });
        }

        function saveEdits() {
            const editedContent = document.getElementById('blog-content').textContent;
            fetch('/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: editedContent
                })
            })
            .then(response => response.json())
            .then(data => {
                alert('Edits saved successfully');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to save edits');
            });
        }
    </script>
</head>
<body class="bg-gradient-to-br from-gray-100 to-gray-200 min-h-screen flex items-center justify-center p-4">
    <div class="container mx-auto max-w-6xl bg-white rounded-2xl shadow-2xl overflow-hidden">
        <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-6">
            <h1 class="text-4xl font-extrabold text-center text-white drop-shadow-lg">Generated Blog Content</h1>
        </div>

        <div class="p-8 space-y-8">
            <div class="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-lg">
                <h2 class="text-2xl font-bold mb-4 text-blue-600 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                    </svg>
                    Blog Outline
                </h2>
                <pre class="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-wrap text-gray-700">{{ outline }}</pre>
            </div>

            <div class="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-lg">
                <h2 class="text-2xl font-bold mb-4 text-purple-600 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Blog Content
                </h2>
                <div class="prose max-w-none">
                    <pre id="blog-content" contenteditable="true" class="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-wrap text-gray-800 focus:ring-2 focus:ring-purple-500 transition">{{ content }}</pre>
                </div>
            </div>

            <div class="flex justify-center space-x-4">
                <button onclick="humanizeBlog()" class="flex items-center bg-gradient-to-r from-green-500 to-teal-600 text-white px-6 py-3 rounded-lg hover:from-green-600 hover:to-teal-700 transition transform hover:scale-105 shadow-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Humanize Blog
                </button>
                <button onclick="saveEdits()" class="flex items-center bg-gradient-to-r from-yellow-500 to-orange-600 text-white px-6 py-3 rounded-lg hover:from-yellow-600 hover:to-orange-700 transition transform hover:scale-105 shadow-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                    </svg>
                    Save Edits
                </button>
                <a href="/" class="flex items-center bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-indigo-700 transition transform hover:scale-105 shadow-lg">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Generate Another Blog
                </a>
            </div>

            <div id="humanize-section" style="display:none;" class="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-lg">
                <h2 class="text-2xl font-bold mb-4 text-green-600 flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Humanized Blog Content
                </h2>
                <pre id="humanized-content" class="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-wrap text-gray-700"></pre>
            </div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_url = request.form.get('product_url')
        product_title = request.form.get('product_title')
        product_description = request.form.get('product_description')
        primary_keywords = request.form.get('primary_keywords')
        secondary_keywords = request.form.get('secondary_keywords')
        intent = request.form.get('intent')

        try:
            blog_outline = generate_blog_outline(
                product_url, product_title, product_description,
                primary_keywords, secondary_keywords, intent
            )

            blog_content = generate_blog_content(
                blog_outline, product_url, product_title, product_description,
                primary_keywords, secondary_keywords, intent
            )

            return render_template_string(RESULT_TEMPLATE,
                                          outline=blog_outline,
                                          content=blog_content)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return render_template_string(INDEX_TEMPLATE)

@app.route('/general', methods=['POST'])
def generate_general_blog():
    keywords = request.form.get('keywords')
    primary_keywords = request.form.get('primary_keywords')
    prompt = request.form.get('prompt')

    try:
        blog_outline = generate_general_blog_outline(keywords, primary_keywords, prompt)
        blog_content = generate_general_blog_content(blog_outline, keywords, primary_keywords, prompt)

        return render_template_string(RESULT_TEMPLATE,
                                      outline=blog_outline,
                                      content=blog_content)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a new route for humanization
@app.route('/humanize', methods=['POST'])
def humanize_blog():
    try:
        # Get the content from the request
        data = request.get_json()
        content = data.get('content', '')

        # Humanize the content
        humanized_content = humanize_text(content)

        return jsonify({
            'humanized_content': humanized_content
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

# Add a new route to save edits
@app.route('/save', methods=['POST'])
def save_edits():
    try:
        # Get the edited content from the request
        data = request.get_json()
        edited_content = data.get('content', '')

        # Here you can add logic to save the edited content to a database or file
        # For this example, we'll just return a success message

        return jsonify({
            'message': 'Edits saved successfully'
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)








#tHIS FUNCTION USES GEMINI
# import os
# import google.generativeai as genai
# from flask import Flask, render_template_string, request, jsonify
# from dotenv import load_dotenv
# import requests
# import time

# # Load .env variables
# load_dotenv()

# # Initialize Flask
# app = Flask(__name__)

# # Configure Gemini
# genai.configure(api_key=os.getenv("API_KEY_GEMINI"))  # Or paste your key directly for testing
# # HIX API Configuration
# HIX_API_KEYY = os.getenv("HIX_API_KEY")  # Store your HIX API key in .env
# HIX_API_ENDPOINT = "https://api.hix.ai/v1/humanize"  # Replace with actual HIX API endpoint

# # Two different models for different tasks
# blog_generation_model = genai.GenerativeModel("gemini-2.0-flash")
# grammar_improvement_model = genai.GenerativeModel("gemini-2.0-flash")

# import os
# import requests
# import time

# def split_text_into_chunks(text, max_words=500):
#     """
#     Split text into chunks of approximately max_words.
    
#     Args:
#         text (str): Input text to be split
#         max_words (int): Maximum number of words per chunk
    
#     Returns:
#         list: List of text chunks
#     """
#     words = text.split()
#     chunks = []
#     current_chunk = []
#     current_word_count = 0

#     for word in words:
#         current_chunk.append(word)
#         current_word_count += 1

#         if current_word_count >= max_words:
#             chunks.append(' '.join(current_chunk))
#             current_chunk = []
#             current_word_count = 0

#     # Add any remaining words
#     if current_chunk:
#         chunks.append(' '.join(current_chunk))

#     return chunks

# def humanize_chunk(chunk, api_key=os.getenv("HIX_API_KEY")):
#     """
#     Humanize a single text chunk.
    
#     Args:
#         chunk (str): Text chunk to humanize
#         api_key (str): HIX API key
    
#     Returns:
#         str: Humanized chunk or original chunk if humanization fails
#     """
#     # API endpoints
#     SUBMIT_URL = "https://bypass.hix.ai/api/hixbypass/v1/submit"
#     OBTAIN_URL = "https://bypass.hix.ai/api/hixbypass/v1/obtain"

#     # Headers for API requests
#     headers = {
#         "api-key": api_key,
#         "Content-Type": "application/json"
#     }

#     # Payload for submission
#     submit_payload = {
#         "input": chunk,
#         "mode": "Balanced"
#     }

#     try:
#         # Submit humanization task
#         submit_response = requests.post(SUBMIT_URL, json=submit_payload, headers=headers)
#         submit_response.raise_for_status()
#         submit_data = submit_response.json()

#         # Check for submission errors
#         if submit_data.get('err_code') != 0:
#             print(f"Submission Error: {submit_data.get('err_msg', 'Unknown error')}")
#             return chunk

#         # Extract task ID
#         task_id = submit_data['data']['task_id']

#         # Poll for task result
#         max_attempts = 10
#         for _ in range(max_attempts):
#             time.sleep(2)

#             # Obtain task result
#             obtain_response = requests.get(
#                 OBTAIN_URL, 
#                 params={"task_id": task_id}, 
#                 headers=headers
#             )
#             obtain_response.raise_for_status()
#             obtain_data = obtain_response.json()

#             # Check if task is complete
#             if obtain_data.get('err_code') == 0 and obtain_data['data'].get('task_status'):
#                 return obtain_data['data'].get('output', chunk)

#         # Timeout error
#         print("Humanization task timed out")
#         return chunk

#     except Exception as e:
#         print(f"Humanization Error for chunk: {e}")
#         return chunk

# def humanize_text(text, max_words=500):
#     """
#     Humanize text by processing it in chunks.
    
#     Args:
#         text (str): Text to be humanized
#         max_words (int): Maximum words per chunk
    
#     Returns:
#         str: Humanized text
#     """
#     # Validate input
#     if not text or len(text.split()) < 50:
#         return text

#     # Get API key from environment
#     api_key = os.getenv("HIX_API_KEY")
#     if not api_key:
#         print("Error: HIX API Key not set in environment variables")
#         return text

#     # Split text into chunks
#     chunks = split_text_into_chunks(text, max_words)

#     # Humanize each chunk
#     humanized_chunks = []
#     for chunk in chunks:
#         humanized_chunk = humanize_chunk(chunk, api_key)
#         humanized_chunks.append(humanized_chunk)

#     # Reassemble humanized chunks
#     return ' '.join(humanized_chunks)
    
# def improve_grammar_and_readability(content, primary_keywords, secondary_keywords):
#     """
#     Improve the grammar, clarity, and readability of the generated blog content.

#     Args:
#         content (str): The original generated blog content
#         primary_keywords (str): Comma-separated primary keywords
#         secondary_keywords (str): Comma-separated secondary keywords

#     Returns:
#         str: Improved, more polished blog content
#     """
#     improvement_prompt = f"""Please review and improve the following text.
#     Focus on:
#     - Make sure the primary keywords are used only 4-5 times in whole blog: {primary_keywords}
#     - Make sure each secondary keyword is only used at least once in whole blog: {secondary_keywords}
#     - Correcting grammar and spelling errors
#     - Enhancing sentence structure and flow
#     - Improving clarity and readability
#     - Maintaining the original tone and meaning
#     - Breaking up long sentences
#     - Using more engaging and precise language
#     - Ensuring professional and conversational style

#     Original Text:
#     {content}

#     Provide the improved version of the text."""

#     try:
#         response = grammar_improvement_model.generate_content(improvement_prompt)
#         improved_content = response.text
#         return improved_content
#     except Exception as e:
#         print(f"Grammar improvement error: {e}")
#         return content  # Return original content if improvement fails

# def generate_blog_outline(product_url, product_title, product_description,
#                           primary_keywords, secondary_keywords, intent):
#     prompt = f"""Create a comprehensive and detailed blog outline for a product blog with the following details:

# Product URL: {product_url}
# Product Title: {product_title}
# Product Description: {product_description}
# Primary Keywords: {primary_keywords}
# Secondary Keywords: {secondary_keywords}
# Search Intent: {intent}

# Outline Requirements:
# 1. Introduction:
#    - Compelling hook related to the product's unique value proposition
#    - Brief overview of the product and its significance
#    - Problem the product solves
#    - Include a captivating anecdote or statistic to engage readers

# 2. Product Overview:
#    - Detailed breakdown of product features
#    - Unique selling points
#    - Technical specifications
#    - How it differs from competitors
#    - Include sub-sections for each major feature

# 3. Use Cases and Applications:
#    - Specific scenarios where the product excels
#    - Target audience and their pain points
#    - Real-world examples or potential applications
#    - Include case studies or success stories if available

# 4. Benefits and Advantages:
#    - Comprehensive list of benefits
#    - Quantifiable improvements or advantages
#    - Customer-centric perspective on product value
#    - Include testimonials or reviews to support claims

# 5. Practical Insights:
#    - Implementation tips
#    - Best practices for using the product
#    - Potential challenges and solutions
#    - Include step-by-step guides or tutorials

# 6. Conclusion:
#    - Recap of key product highlights
#    - Clear call-to-action
#    - Future potential or upcoming features
#    - Include a final thought or reflection to leave a lasting impression

# Additional Guidance:
# - Ensure the outline is informative and engaging
# - Incorporate keywords naturally and frequently throughout the blog
# - Focus on solving customer problems
# - Maintain a balanced, objective tone
# - Highlight unique aspects of the product
# - Provide detailed sub-points under each main section to elaborate on the content
# """
#     response = blog_generation_model.generate_content(prompt)
#     return response.text

# def generate_blog_content(outline, product_url, product_title, product_description,
#                           primary_keywords, secondary_keywords, intent):
#     sections = outline.split('\n\n')
#     blog_content = []
#     all_keywords = primary_keywords.split(", ") + secondary_keywords.split(", ")
#     keyword_usage = {keyword: 0 for keyword in all_keywords}
#     primary_keyword_target = 3  # Reduced from 5 to 3 times
#     secondary_keyword_target = 1  # Target usage for secondary keywords

#     for i, section in enumerate(sections):
#         previous_text = ' '.join(blog_content) if i > 0 else 'None'

#         primary_keywords_instruction = (
#             "\n- Use primary keywords sparingly and naturally, aiming for no more than 3 total uses across the entire blog: "
#             + ', '.join(primary_keywords.split(", ")) +
#             ". Ensure the usage is contextually relevant and not forced."
#         )

#         secondary_keywords_instruction = (
#             "\n- Use each of the following secondary keywords approximately **1 time** throughout the entire blog: "
#             + ', '.join(secondary_keywords.split(", ")) +
#             ". Make the usage natural and contextually relevant."
#         )

#         section_prompt = f"""Generate a detailed section for a blog post while ensuring no repetition.

# Section Outline:
# {section}

# Product Details:
# - Product URL: {product_url}
# - Product Title: {product_title}
# - Product Description: {product_description}
# - Search Intent: {intent}

# Guidelines:
# - Word count for this section: Approximately {1200 // len(sections)} words
# - Avoid repeating points from previous sections
# - Focus on new insights, examples, and fresh perspectives
# - Ensure smooth transitions from previous sections
# - Maintain a professional and engaging tone{primary_keywords_instruction}{secondary_keywords_instruction}

# Previous Sections Summary:
# {previous_text}

# Generate the content for this section."""

#         response = blog_generation_model.generate_content(section_prompt)
#         section_content = response.text

#         # Update keyword usage count
#         for keyword in all_keywords:
#             keyword_usage[keyword] += section_content.lower().count(keyword.lower())

#         blog_content.append(section_content)

#     # Ensure primary keywords are used no more than 3 times and secondary keywords are used once
#     for keyword, count in keyword_usage.items():
#         if keyword in primary_keywords.split(", ") and count > primary_keyword_target:
#             # Remove excess mentions by regenerating content or adjusting references
#             blog_content = [section.replace(keyword, f"**{keyword}**", count - primary_keyword_target) for section in blog_content]
#         elif keyword in secondary_keywords.split(", ") and count < secondary_keyword_target:
#             additional_content = f"Moreover, {keyword} is an important aspect to consider."
#             blog_content.append(additional_content)
#             keyword_usage[keyword] += 1

#     # Combine content and improve grammar and readability
#     final_content = '\n\n'.join(blog_content)
#     improved_content = improve_grammar_and_readability(final_content, primary_keywords, secondary_keywords)
#     return improved_content

# def generate_general_blog_outline(keywords, primary_keywords, prompt):
#     outline_prompt = f"""Create a comprehensive and detailed blog outline based on the following details:

# Keywords: {keywords}
# Primary Keywords: {primary_keywords}
# Prompt: {prompt}

# Outline Requirements:
# 1. Introduction:
#    - Compelling hook related to the main topic
#    - Brief overview of the topic and its significance
#    - Problem the blog addresses
#    - Include a captivating anecdote or statistic to engage readers

# 2. Main Sections:
#    - Detailed breakdown of the main points
#    - Unique insights or perspectives
#    - Include sub-sections for each major point

# 3. Use Cases and Applications:
#    - Specific scenarios where the topic is relevant
#    - Target audience and their pain points
#    - Real-world examples or potential applications
#    - Include case studies or success stories if available

# 4. Benefits and Advantages:
#    - Comprehensive list of benefits
#    - Quantifiable improvements or advantages
#    - Customer-centric perspective on the topic's value
#    - Include testimonials or reviews to support claims

# 5. Practical Insights:
#    - Implementation tips
#    - Best practices related to the topic
#    - Potential challenges and solutions
#    - Include step-by-step guides or tutorials

# 6. Conclusion:
#    - Recap of key points
#    - Clear call-to-action
#    - Future potential or upcoming trends
#    - Include a final thought or reflection to leave a lasting impression

# Additional Guidance:
# - Ensure the outline is informative and engaging
# - Incorporate keywords naturally and frequently throughout the blog
# - Focus on solving reader problems
# - Maintain a balanced, objective tone
# - Highlight unique aspects of the topic
# - Provide detailed sub-points under each main section to elaborate on the content
# """
#     response = blog_generation_model.generate_content(outline_prompt)
#     return response.text

# def generate_general_blog_content(outline, keywords, primary_keywords, prompt):
#     sections = outline.split('\n\n')
#     blog_content = []
#     all_keywords = primary_keywords.split(", ") + keywords.split(", ")
#     keyword_usage = {keyword: 0 for keyword in all_keywords}
#     primary_keyword_target = 3  # Target usage for primary keywords
#     secondary_keyword_target = 1  # Target usage for secondary keywords

#     for i, section in enumerate(sections):
#         previous_text = ' '.join(blog_content) if i > 0 else 'None'

#         primary_keywords_instruction = (
#             "\n- Use primary keywords sparingly and naturally, aiming for no more than 3 total uses across the entire blog: "
#             + ', '.join(primary_keywords.split(", ")) +
#             ". Ensure the usage is contextually relevant and not forced."
#         )

#         secondary_keywords_instruction = (
#             "\n- Use each of the following secondary keywords approximately **1 time** throughout the entire blog: "
#             + ', '.join(keywords.split(", ")) +
#             ". Make the usage natural and contextually relevant."
#         )

#         section_prompt = f"""Generate a detailed section for a blog post while ensuring no repetition.

# Section Outline:
# {section}

# Guidelines:
# - Word count for this section: Approximately {1200 // len(sections)} words
# - Avoid repeating points from previous sections
# - Focus on new insights, examples, and fresh perspectives
# - Ensure smooth transitions from previous sections
# - Maintain a professional and engaging tone{primary_keywords_instruction}{secondary_keywords_instruction}

# Previous Sections Summary:
# {previous_text}

# Generate the content for this section."""

#         response = blog_generation_model.generate_content(section_prompt)
#         section_content = response.text

#         # Update keyword usage count
#         for keyword in all_keywords:
#             keyword_usage[keyword] += section_content.lower().count(keyword.lower())

#         blog_content.append(section_content)

#     # Ensure primary keywords are used no more than 3 times and secondary keywords are used once
#     for keyword, count in keyword_usage.items():
#         if keyword in primary_keywords.split(", ") and count > primary_keyword_target:
#             # Remove excess mentions by regenerating content or adjusting references
#             blog_content = [section.replace(keyword, f"**{keyword}**", count - primary_keyword_target) for section in blog_content]
#         elif keyword in keywords.split(", ") and count < secondary_keyword_target:
#             additional_content = f"Moreover, {keyword} is an important aspect to consider."
#             blog_content.append(additional_content)
#             keyword_usage[keyword] += 1

#     # Combine content and improve grammar and readability
#     final_content = '\n\n'.join(blog_content)
    
#     # Fix here: use 'keywords' instead of 'secondary_keywords' in this call
#     improved_content = improve_grammar_and_readability(final_content, primary_keywords, keywords)
#     return improved_content
# # HTML templates
# INDEX_TEMPLATE = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Blog Generator Dashboard</title>
#     <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
#     <script>
#         function showForm(type) {
#             document.getElementById('product-form-container').style.display = 'none';
#             document.getElementById('general-form-container').style.display = 'none';
#             if (type === 'product') {
#                 document.getElementById('product-form-container').style.display = 'block';
#             } else if (type === 'general') {
#                 document.getElementById('general-form-container').style.display = 'block';
#             }
#         }
#     </script>
# </head>
# <body class="bg-gradient-to-br from-gray-100 to-gray-200 min-h-screen flex items-center justify-center p-4">
#     <div class="container mx-auto max-w-5xl bg-white rounded-2xl shadow-2xl overflow-hidden">
#         <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-8">
#             <h1 class="text-4xl font-extrabold mb-4 text-center text-white drop-shadow-lg">Blog Generator Dashboard</h1>
#             <p class="text-center text-white opacity-80">Create compelling blog content with ease</p>
#         </div>

#         <div class="p-8">
#             <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
#                 <div onclick="showForm('product')" class="group cursor-pointer p-6 bg-white border-2 border-transparent rounded-xl shadow-lg hover:border-blue-500 hover:shadow-2xl transition-all duration-300 ease-in-out transform hover:-translate-y-2">
#                     <div class="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mb-4 group-hover:bg-blue-200 transition">
#                         <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
#                         </svg>
#                     </div>
#                     <h2 class="text-2xl font-bold mb-2 text-gray-800 group-hover:text-blue-600 transition">Product-Specific Blog</h2>
#                     <p class="text-gray-600 group-hover:text-gray-800 transition">Generate a blog tailored to a specific product using keywords and descriptions.</p>
#                 </div>
#                 <div onclick="showForm('general')" class="group cursor-pointer p-6 bg-white border-2 border-transparent rounded-xl shadow-lg hover:border-purple-500 hover:shadow-2xl transition-all duration-300 ease-in-out transform hover:-translate-y-2">
#                     <div class="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mb-4 group-hover:bg-purple-200 transition">
#                         <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
#                         </svg>
#                     </div>
#                     <h2 class="text-2xl font-bold mb-2 text-gray-800 group-hover:text-purple-600 transition">General Blog</h2>
#                     <p class="text-gray-600 group-hover:text-gray-800 transition">Create general blogs for topics or industries.</p>
#                 </div>
#             </div>

#             <div id="product-form-container" style="display:none;" class="bg-white p-8 rounded-xl shadow-lg border border-gray-100">
#                 <h2 class="text-2xl font-bold mb-6 text-center text-blue-600">Generate Product Blog</h2>
#                 <form method="POST" action="/" class="space-y-4">
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Product URL</label>
#                         <input type="text" name="product_url" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Product Title</label>
#                         <input type="text" name="product_title" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Product Description</label>
#                         <textarea name="product_description" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition" rows="4"></textarea>
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Primary Keywords</label>
#                         <input type="text" name="primary_keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Secondary Keywords</label>
#                         <input type="text" name="secondary_keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Search Intent</label>
#                         <input type="text" name="intent" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <button type="submit" class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white p-3 rounded-lg hover:from-blue-600 hover:to-purple-700 transition duration-300 ease-in-out transform hover:scale-105 hover:shadow-lg">
#                         Generate Blog
#                     </button>
#                 </form>
#             </div>

#             <div id="general-form-container" style="display:none;" class="bg-white p-8 rounded-xl shadow-lg border border-gray-100">
#                 <h2 class="text-2xl font-bold mb-6 text-center text-purple-600">Generate General Blog</h2>
#                 <form method="POST" action="/general" class="space-y-4">
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-purple-600 transition">Keywords</label>
#                         <input type="text" name="keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-purple-600 transition">Primary Keywords</label>
#                         <input type="text" name="primary_keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-purple-600 transition">Prompt</label>
#                         <textarea name="prompt" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition" rows="4"></textarea>
#                     </div>
#                     <button type="submit" class="w-full bg-gradient-to-r from-purple-500 to-blue-600 text-white p-3 rounded-lg hover:from-purple-600 hover:to-blue-700 transition duration-300 ease-in-out transform hover:scale-105 hover:shadow-lg">
#                         Generate Blog
#                     </button>
#                 </form>
#             </div>
#         </div>
#     </div>
# </body>
# </html>
# '''

# # Updated HTML template to include humanization button and editable content
# RESULT_TEMPLATE = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Blog Generation Result</title>
#     <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
#     <script>
#         function humanizeBlog() {
#             fetch('/humanize', {
#                 method: 'POST',
#                 headers: {
#                     'Content-Type': 'application/json',
#                 },
#                 body: JSON.stringify({
#                     content: document.getElementById('blog-content').textContent
#                 })
#             })
#             .then(response => response.json())
#             .then(data => {
#                 document.getElementById('humanized-content').textContent = data.humanized_content;
#                 document.getElementById('humanize-section').style.display = 'block';
#             })
#             .catch(error => {
#                 console.error('Error:', error);
#                 alert('Failed to humanize the blog');
#             });
#         }

#         function saveEdits() {
#             const editedContent = document.getElementById('blog-content').textContent;
#             fetch('/save', {
#                 method: 'POST',
#                 headers: {
#                     'Content-Type': 'application/json',
#                 },
#                 body: JSON.stringify({
#                     content: editedContent
#                 })
#             })
#             .then(response => response.json())
#             .then(data => {
#                 alert('Edits saved successfully');
#             })
#             .catch(error => {
#                 console.error('Error:', error);
#                 alert('Failed to save edits');
#             });
#         }
#     </script>
# </head>
# <body class="bg-gradient-to-br from-gray-100 to-gray-200 min-h-screen flex items-center justify-center p-4">
#     <div class="container mx-auto max-w-6xl bg-white rounded-2xl shadow-2xl overflow-hidden">
#         <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-6">
#             <h1 class="text-4xl font-extrabold text-center text-white drop-shadow-lg">Generated Blog Content</h1>
#         </div>

#         <div class="p-8 space-y-8">
#             <div class="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-lg">
#                 <h2 class="text-2xl font-bold mb-4 text-blue-600 flex items-center">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
#                     </svg>
#                     Blog Outline
#                 </h2>
#                 <pre class="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-wrap text-gray-700">{{ outline }}</pre>
#             </div>

#             <div class="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-lg">
#                 <h2 class="text-2xl font-bold mb-4 text-purple-600 flex items-center">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
#                     </svg>
#                     Blog Content
#                 </h2>
#                 <div class="prose max-w-none">
#                     <pre id="blog-content" contenteditable="true" class="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-wrap text-gray-800 focus:ring-2 focus:ring-purple-500 transition">{{ content }}</pre>
#                 </div>
#             </div>

#             <div class="flex justify-center space-x-4">
#                 <button onclick="humanizeBlog()" class="flex items-center bg-gradient-to-r from-green-500 to-teal-600 text-white px-6 py-3 rounded-lg hover:from-green-600 hover:to-teal-700 transition transform hover:scale-105 shadow-lg">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
#                     </svg>
#                     Humanize Blog
#                 </button>
#                 <button onclick="saveEdits()" class="flex items-center bg-gradient-to-r from-yellow-500 to-orange-600 text-white px-6 py-3 rounded-lg hover:from-yellow-600 hover:to-orange-700 transition transform hover:scale-105 shadow-lg">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
#                     </svg>
#                     Save Edits
#                 </button>
#                 <a href="/" class="flex items-center bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-indigo-700 transition transform hover:scale-105 shadow-lg">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
#                     </svg>
#                     Generate Another Blog
#                 </a>
#             </div>

#             <div id="humanize-section" style="display:none;" class="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-lg">
#                 <h2 class="text-2xl font-bold mb-4 text-green-600 flex items-center">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
#                     </svg>
#                     Humanized Blog Content
#                 </h2>
#                 <pre id="humanized-content" class="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-wrap text-gray-700"></pre>
#             </div>
#         </div>
#     </div>
# </body>
# </html>
# '''

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         product_url = request.form.get('product_url')
#         product_title = request.form.get('product_title')
#         product_description = request.form.get('product_description')
#         primary_keywords = request.form.get('primary_keywords')
#         secondary_keywords = request.form.get('secondary_keywords')
#         intent = request.form.get('intent')

#         try:
#             blog_outline = generate_blog_outline(
#                 product_url, product_title, product_description,
#                 primary_keywords, secondary_keywords, intent
#             )

#             blog_content = generate_blog_content(
#                 blog_outline, product_url, product_title, product_description,
#                 primary_keywords, secondary_keywords, intent
#             )

#             return render_template_string(RESULT_TEMPLATE,
#                                           outline=blog_outline,
#                                           content=blog_content)

#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

#     return render_template_string(INDEX_TEMPLATE)

# @app.route('/general', methods=['POST'])
# def generate_general_blog():
#     keywords = request.form.get('keywords')
#     primary_keywords = request.form.get('primary_keywords')
#     prompt = request.form.get('prompt')

#     try:
#         blog_outline = generate_general_blog_outline(keywords, primary_keywords, prompt)
#         blog_content = generate_general_blog_content(blog_outline, keywords, primary_keywords, prompt)

#         return render_template_string(RESULT_TEMPLATE,
#                                       outline=blog_outline,
#                                       content=blog_content)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Add a new route for humanization
# @app.route('/humanize', methods=['POST'])
# def humanize_blog():
#     try:
#         # Get the content from the request
#         data = request.get_json()
#         content = data.get('content', '')

#         # Humanize the content
#         humanized_content = humanize_text(content)

#         return jsonify({
#             'humanized_content': humanized_content
#         })
#     except Exception as e:
#         return jsonify({
#             'error': str(e)
#         }), 500

# # Add a new route to save edits
# @app.route('/save', methods=['POST'])
# def save_edits():
#     try:
#         # Get the edited content from the request
#         data = request.get_json()
#         edited_content = data.get('content', '')

#         # Here you can add logic to save the edited content to a database or file
#         # For this example, we'll just return a success message

#         return jsonify({
#             'message': 'Edits saved successfully'
#         })
#     except Exception as e:
#         return jsonify({
#             'error': str(e)
#         }), 500

# if __name__ == '__main__':
#     app.run(debug=True)




























# import os
# import google.generativeai as genai
# from flask import Flask, render_template_string, request, jsonify
# from dotenv import load_dotenv
# import requests
# import time

# # Load .env variables
# load_dotenv()

# # Initialize Flask
# app = Flask(__name__)

# # Configure Gemini
# genai.configure(api_key=os.getenv("API_KEY_GEMINI"))  # Or paste your key directly for testing
# # HIX API Configuration
# HIX_API_KEY = os.getenv("HIX_API_KEY")  # Store your HIX API key in .env
# HIX_API_ENDPOINT = "https://api.hix.ai/v1/humanize"  # Replace with actual HIX API endpoint

# # Two different models for different tasks
# blog_generation_model = genai.GenerativeModel("gemini-2.0-flash")
# grammar_improvement_model = genai.GenerativeModel("gemini-2.0-flash")

# def split_text_into_chunks(text, max_words=500):
#     """
#     Split text into chunks of approximately max_words.

#     Args:
#         text (str): Input text to be split
#         max_words (int): Maximum number of words per chunk

#     Returns:
#         list: List of text chunks
#     """
#     words = text.split()
#     chunks = []
#     current_chunk = []
#     current_word_count = 0

#     for word in words:
#         current_chunk.append(word)
#         current_word_count += 1

#         if current_word_count >= max_words:
#             chunks.append(' '.join(current_chunk))
#             current_chunk = []
#             current_word_count = 0

#     # Add any remaining words
#     if current_chunk:
#         chunks.append(' '.join(current_chunk))

#     return chunks

# def humanize_chunk(chunk, api_key=os.getenv("HIX_API_KEY")):
#     """
#     Humanize a single text chunk.

#     Args:
#         chunk (str): Text chunk to humanize
#         api_key (str): HIX API key

#     Returns:
#         str: Humanized chunk or original chunk if humanization fails
#     """
#     # API endpoints
#     SUBMIT_URL = "https://bypass.hix.ai/api/hixbypass/v1/submit"
#     OBTAIN_URL = "https://bypass.hix.ai/api/hixbypass/v1/obtain"

#     # Headers for API requests
#     headers = {
#         "api-key": api_key,
#         "Content-Type": "application/json"
#     }

#     # Payload for submission
#     submit_payload = {
#         "input": chunk,
#         "mode": "Balanced"
#     }

#     try:
#         # Submit humanization task
#         submit_response = requests.post(SUBMIT_URL, json=submit_payload, headers=headers)
#         submit_response.raise_for_status()
#         submit_data = submit_response.json()

#         # Check for submission errors
#         if submit_data.get('err_code') != 0:
#             print(f"Submission Error: {submit_data.get('err_msg', 'Unknown error')}")
#             return chunk

#         # Extract task ID
#         task_id = submit_data['data']['task_id']

#         # Poll for task result
#         max_attempts = 10
#         for _ in range(max_attempts):
#             time.sleep(2)

#             # Obtain task result
#             obtain_response = requests.get(
#                 OBTAIN_URL,
#                 params={"task_id": task_id},
#                 headers=headers
#             )
#             obtain_response.raise_for_status()
#             obtain_data = obtain_response.json()

#             # Check if task is complete
#             if obtain_data.get('err_code') == 0 and obtain_data['data'].get('task_status'):
#                 return obtain_data['data'].get('output', chunk)

#         # Timeout error
#         print("Humanization task timed out")
#         return chunk

#     except Exception as e:
#         print(f"Humanization Error for chunk: {e}")
#         return chunk

# def humanize_text(text, max_words=500):
#     """
#     Humanize text by processing it in chunks.

#     Args:
#         text (str): Text to be humanized
#         max_words (int): Maximum words per chunk

#     Returns:
#         str: Humanized text
#     """
#     # Validate input
#     if not text or len(text.split()) < 50:
#         return text

#     # Get API key from environment
#     api_key = os.getenv("HIX_API_KEY")
#     if not api_key:
#         print("Error: HIX API Key not set in environment variables")
#         return text

#     # Split text into chunks
#     chunks = split_text_into_chunks(text, max_words)

#     # Humanize each chunk
#     humanized_chunks = []
#     for chunk in chunks:
#         humanized_chunk = humanize_chunk(chunk, api_key)
#         humanized_chunks.append(humanized_chunk)

#     # Reassemble humanized chunks
#     return ' '.join(humanized_chunks)

# def improve_grammar_and_readability(content, primary_keywords, secondary_keywords):
#     """
#     Improve the grammar, clarity, and readability of the generated blog content.

#     Args:
#         content (str): The original generated blog content
#         primary_keywords (str): Comma-separated primary keywords
#         secondary_keywords (str): Comma-separated secondary keywords

#     Returns:
#         str: Improved, more polished blog content
#     """
#     improvement_prompt = f"""Please review and improve the following text.
#     Focus on:
#     - Make sure the primary keywords are used only 4-5 times in whole blog: {primary_keywords}
#     - Make sure each secondary keyword is only used at least once in whole blog: {secondary_keywords}
#     - Correcting grammar and spelling errors
#     - Enhancing sentence structure and flow
#     - Improving clarity and readability
#     - Maintaining the original tone and meaning
#     - Breaking up long sentences
#     - Using more engaging and precise language
#     - Ensuring professional and conversational style

#     Original Text:
#     {content}

#     Provide the improved version of the text."""

#     try:
#         response = grammar_improvement_model.generate_content(improvement_prompt)
#         improved_content = response.text
#         return improved_content
#     except Exception as e:
#         print(f"Grammar improvement error: {e}")
#         return content  # Return original content if improvement fails

# def improve_general_blog_grammar_and_readability(content, primary_keywords, secondary_keywords):
#     """
#     Improve the grammar, clarity, and readability of the generated general blog content.

#     Args:
#         content (str): The original generated blog content
#         primary_keywords (str): Comma-separated primary keywords
#         secondary_keywords (str): Comma-separated secondary keywords

#     Returns:
#         str: Improved, more polished blog content
#     """
#     improvement_prompt = f"""Please review and improve the following text.
#     Focus on:
#     - Make sure the primary keywords are used only 4-5 times in whole blog: {primary_keywords}
#     - Make sure each secondary keyword is only used at least once in whole blog: {secondary_keywords}
#     - Correcting grammar and spelling errors
#     - Enhancing sentence structure and flow
#     - Improving clarity and readability
#     - Maintaining the original tone and meaning
#     - Breaking up long sentences
#     - Using more engaging and precise language
#     - Ensuring professional and conversational style

#     Original Text:
#     {content}

#     Provide the improved version of the text."""

#     try:
#         response = grammar_improvement_model.generate_content(improvement_prompt)
#         improved_content = response.text
#         return improved_content
#     except Exception as e:
#         print(f"Grammar improvement error: {e}")
#         return content  # Return original content if improvement fails

# def generate_blog_outline(product_url, product_title, product_description,
#                           primary_keywords, secondary_keywords, intent):
#     prompt = f"""Create a comprehensive and detailed blog outline for a product blog with the following details:

# Product URL: {product_url}
# Product Title: {product_title}
# Product Description: {product_description}
# Primary Keywords: {primary_keywords}
# Secondary Keywords: {secondary_keywords}
# Search Intent: {intent}

# Outline Requirements:
# 1. Introduction:
#    - Compelling hook related to the product's unique value proposition
#    - Brief overview of the product and its significance
#    - Problem the product solves
#    - Include a captivating anecdote or statistic to engage readers

# 2. Product Overview:
#    - Detailed breakdown of product features
#    - Unique selling points
#    - Technical specifications
#    - How it differs from competitors
#    - Include sub-sections for each major feature

# 3. Use Cases and Applications:
#    - Specific scenarios where the product excels
#    - Target audience and their pain points
#    - Real-world examples or potential applications
#    - Include case studies or success stories if available

# 4. Benefits and Advantages:
#    - Comprehensive list of benefits
#    - Quantifiable improvements or advantages
#    - Customer-centric perspective on product value
#    - Include testimonials or reviews to support claims

# 5. Practical Insights:
#    - Implementation tips
#    - Best practices for using the product
#    - Potential challenges and solutions
#    - Include step-by-step guides or tutorials

# 6. Conclusion:
#    - Recap of key product highlights
#    - Clear call-to-action
#    - Future potential or upcoming features
#    - Include a final thought or reflection to leave a lasting impression

# Additional Guidance:
# - Ensure the outline is informative and engaging
# - Incorporate keywords naturally and frequently throughout the blog
# - Focus on solving customer problems
# - Maintain a balanced, objective tone
# - Highlight unique aspects of the product
# - Provide detailed sub-points under each main section to elaborate on the content
# """
#     response = blog_generation_model.generate_content(prompt)
#     return response.text

# def generate_blog_content(outline, product_url, product_title, product_description,
#                           primary_keywords, secondary_keywords, intent):
#     sections = outline.split('\n\n')
#     blog_content = []
#     all_keywords = primary_keywords.split(", ") + secondary_keywords.split(", ")
#     keyword_usage = {keyword: 0 for keyword in all_keywords}
#     primary_keyword_target = 3  # Reduced from 5 to 3 times
#     secondary_keyword_target = 1  # Target usage for secondary keywords

#     for i, section in enumerate(sections):
#         previous_text = ' '.join(blog_content) if i > 0 else 'None'

#         primary_keywords_instruction = (
#             "\n- Use primary keywords sparingly and naturally, aiming for no more than 3 total uses across the entire blog: "
#             + ', '.join(primary_keywords.split(", ")) +
#             ". Ensure the usage is contextually relevant and not forced."
#         )

#         secondary_keywords_instruction = (
#             "\n- Use each of the following secondary keywords approximately **1 time** throughout the entire blog: "
#             + ', '.join(secondary_keywords.split(", ")) +
#             ". Make the usage natural and contextually relevant."
#         )

#         section_prompt = f"""Generate a detailed section for a blog post while ensuring no repetition.

# Section Outline:
# {section}

# Product Details:
# - Product URL: {product_url}
# - Product Title: {product_title}
# - Product Description: {product_description}
# - Search Intent: {intent}

# Guidelines:
# - Word count for this section: Approximately {1200 // len(sections)} words
# - Avoid repeating points from previous sections
# - Focus on new insights, examples, and fresh perspectives
# - Ensure smooth transitions from previous sections
# - Maintain a professional and engaging tone{primary_keywords_instruction}{secondary_keywords_instruction}

# Previous Sections Summary:
# {previous_text}

# Generate the content for this section."""

#         response = blog_generation_model.generate_content(section_prompt)
#         section_content = response.text

#         # Update keyword usage count
#         for keyword in all_keywords:
#             keyword_usage[keyword] += section_content.lower().count(keyword.lower())

#         blog_content.append(section_content)

#     # Ensure primary keywords are used no more than 3 times and secondary keywords are used once
#     for keyword, count in keyword_usage.items():
#         if keyword in primary_keywords.split(", ") and count > primary_keyword_target:
#             # Remove excess mentions by regenerating content or adjusting references
#             blog_content = [section.replace(keyword, f"**{keyword}**", count - primary_keyword_target) for section in blog_content]
#         elif keyword in secondary_keywords.split(", ") and count < secondary_keyword_target:
#             additional_content = f"Moreover, {keyword} is an important aspect to consider."
#             blog_content.append(additional_content)
#             keyword_usage[keyword] += 1

#     # Combine content and improve grammar and readability
#     final_content = '\n\n'.join(blog_content)
#     improved_content = improve_grammar_and_readability(final_content, primary_keywords, secondary_keywords)
#     return improved_content

# def generate_general_blog_outline(keywords, primary_keywords, prompt):
#     outline_prompt = f"""Create a comprehensive and detailed blog outline based on the following details:

# Keywords: {keywords}
# Primary Keywords: {primary_keywords}
# Prompt: {prompt}

# Outline Requirements:
# 1. Introduction:
#    - Compelling hook related to the main topic
#    - Brief overview of the topic and its significance
#    - Problem the blog addresses
#    - Include a captivating anecdote or statistic to engage readers

# 2. Main Sections:
#    - Detailed breakdown of the main points
#    - Unique insights or perspectives
#    - Include sub-sections for each major point

# 3. Use Cases and Applications:
#    - Specific scenarios where the topic is relevant
#    - Target audience and their pain points
#    - Real-world examples or potential applications
#    - Include case studies or success stories if available

# 4. Benefits and Advantages:
#    - Comprehensive list of benefits
#    - Quantifiable improvements or advantages
#    - Customer-centric perspective on the topic's value
#    - Include testimonials or reviews to support claims

# 5. Practical Insights:
#    - Implementation tips
#    - Best practices related to the topic
#    - Potential challenges and solutions
#    - Include step-by-step guides or tutorials

# 6. Conclusion:
#    - Recap of key points
#    - Clear call-to-action
#    - Future potential or upcoming trends
#    - Include a final thought or reflection to leave a lasting impression

# Additional Guidance:
# - Ensure the outline is informative and engaging
# - Incorporate keywords naturally and frequently throughout the blog
# - Focus on solving reader problems
# - Maintain a balanced, objective tone
# - Highlight unique aspects of the topic
# - Provide detailed sub-points under each main section to elaborate on the content
# """
#     response = blog_generation_model.generate_content(outline_prompt)
#     return response.text

# def generate_general_blog_content(outline, keywords, primary_keywords, prompt):
#     sections = outline.split('\n\n')
#     blog_content = []
#     all_keywords = primary_keywords.split(", ") + keywords.split(", ")
#     keyword_usage = {keyword: 0 for keyword in all_keywords}
#     primary_keyword_target = 3  # Target usage for primary keywords
#     secondary_keyword_target = 1  # Target usage for secondary keywords

#     for i, section in enumerate(sections):
#         previous_text = ' '.join(blog_content) if i > 0 else 'None'

#         primary_keywords_instruction = (
#             "\n- Use primary keywords sparingly and naturally, aiming for no more than 3 total uses across the entire blog: "
#             + ', '.join(primary_keywords.split(", ")) +
#             ". Ensure the usage is contextually relevant and not forced."
#         )

#         secondary_keywords_instruction = (
#             "\n- Use each of the following secondary keywords approximately **1 time** throughout the entire blog: "
#             + ', '.join(keywords.split(", ")) +
#             ". Make the usage natural and contextually relevant."
#         )

#         section_prompt = f"""Generate a detailed section for a blog post while ensuring no repetition.

# Section Outline:
# {section}

# Guidelines:
# - Word count for this section: Approximately {1200 // len(sections)} words
# - Avoid repeating points from previous sections
# - Focus on new insights, examples, and fresh perspectives
# - Ensure smooth transitions from previous sections
# - Maintain a professional and engaging tone{primary_keywords_instruction}{secondary_keywords_instruction}

# Previous Sections Summary:
# {previous_text}

# Generate the content for this section."""

#         response = blog_generation_model.generate_content(section_prompt)
#         section_content = response.text

#         # Update keyword usage count
#         for keyword in all_keywords:
#             keyword_usage[keyword] += section_content.lower().count(keyword.lower())

#         blog_content.append(section_content)

#     # Ensure primary keywords are used no more than 3 times and secondary keywords are used once
#     for keyword, count in keyword_usage.items():
#         if keyword in primary_keywords.split(", ") and count > primary_keyword_target:
#             # Remove excess mentions by regenerating content or adjusting references
#             blog_content = [section.replace(keyword, f"**{keyword}**", count - primary_keyword_target) for section in blog_content]
#         elif keyword in keywords.split(", ") and count < secondary_keyword_target:
#             additional_content = f"Moreover, {keyword} is an important aspect to consider."
#             blog_content.append(additional_content)
#             keyword_usage[keyword] += 1

#     # Combine content and improve grammar and readability
#     final_content = '\n\n'.join(blog_content)
#     improved_content = improve_general_blog_grammar_and_readability(final_content, primary_keywords, secondary_keywords)
#     return improved_content

# # HTML templates
# INDEX_TEMPLATE = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Blog Generator Dashboard</title>
#     <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
#     <script>
#         function showForm(type) {
#             document.getElementById('product-form-container').style.display = 'none';
#             document.getElementById('general-form-container').style.display = 'none';
#             if (type === 'product') {
#                 document.getElementById('product-form-container').style.display = 'block';
#             } else if (type === 'general') {
#                 document.getElementById('general-form-container').style.display = 'block';
#             }
#         }
#     </script>
# </head>
# <body class="bg-gradient-to-br from-gray-100 to-gray-200 min-h-screen flex items-center justify-center p-4">
#     <div class="container mx-auto max-w-5xl bg-white rounded-2xl shadow-2xl overflow-hidden">
#         <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-8">
#             <h1 class="text-4xl font-extrabold mb-4 text-center text-white drop-shadow-lg">Blog Generator Dashboard</h1>
#             <p class="text-center text-white opacity-80">Create compelling blog content with ease</p>
#         </div>

#         <div class="p-8">
#             <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
#                 <div onclick="showForm('product')" class="group cursor-pointer p-6 bg-white border-2 border-transparent rounded-xl shadow-lg hover:border-blue-500 hover:shadow-2xl transition-all duration-300 ease-in-out transform hover:-translate-y-2">
#                     <div class="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mb-4 group-hover:bg-blue-200 transition">
#                         <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
#                         </svg>
#                     </div>
#                     <h2 class="text-2xl font-bold mb-2 text-gray-800 group-hover:text-blue-600 transition">Product-Specific Blog</h2>
#                     <p class="text-gray-600 group-hover:text-gray-800 transition">Generate a blog tailored to a specific product using keywords and descriptions.</p>
#                 </div>
#                 <div onclick="showForm('general')" class="group cursor-pointer p-6 bg-white border-2 border-transparent rounded-xl shadow-lg hover:border-purple-500 hover:shadow-2xl transition-all duration-300 ease-in-out transform hover:-translate-y-2">
#                     <div class="bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mb-4 group-hover:bg-purple-200 transition">
#                         <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
#                         </svg>
#                     </div>
#                     <h2 class="text-2xl font-bold mb-2 text-gray-800 group-hover:text-purple-600 transition">General Blog</h2>
#                     <p class="text-gray-600 group-hover:text-gray-800 transition">Create general blogs for topics or industries.</p>
#                 </div>
#             </div>

#             <div id="product-form-container" style="display:none;" class="bg-white p-8 rounded-xl shadow-lg border border-gray-100">
#                 <h2 class="text-2xl font-bold mb-6 text-center text-blue-600">Generate Product Blog</h2>
#                 <form method="POST" action="/" class="space-y-4">
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Product URL</label>
#                         <input type="text" name="product_url" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Product Title</label>
#                         <input type="text" name="product_title" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Product Description</label>
#                         <textarea name="product_description" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition" rows="4"></textarea>
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Primary Keywords</label>
#                         <input type="text" name="primary_keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Secondary Keywords</label>
#                         <input type="text" name="secondary_keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-blue-600 transition">Search Intent</label>
#                         <input type="text" name="intent" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 transition">
#                     </div>
#                     <button type="submit" class="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white p-3 rounded-lg hover:from-blue-600 hover:to-purple-700 transition duration-300 ease-in-out transform hover:scale-105 hover:shadow-lg">
#                         Generate Blog
#                     </button>
#                 </form>
#             </div>

#             <div id="general-form-container" style="display:none;" class="bg-white p-8 rounded-xl shadow-lg border border-gray-100">
#                 <h2 class="text-2xl font-bold mb-6 text-center text-purple-600">Generate General Blog</h2>
#                 <form method="POST" action="/general" class="space-y-4">
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-purple-600 transition">Keywords</label>
#                         <input type="text" name="keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-purple-600 transition">Primary Keywords</label>
#                         <input type="text" name="primary_keywords" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition">
#                     </div>
#                     <div class="group">
#                         <label class="block mb-2 text-gray-700 group-hover:text-purple-600 transition">Prompt</label>
#                         <textarea name="prompt" required class="w-full p-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition" rows="4"></textarea>
#                     </div>
#                     <button type="submit" class="w-full bg-gradient-to-r from-purple-500 to-blue-600 text-white p-3 rounded-lg hover:from-purple-600 hover:to-blue-700 transition duration-300 ease-in-out transform hover:scale-105 hover:shadow-lg">
#                         Generate Blog
#                     </button>
#                 </form>
#             </div>
#         </div>
#     </div>
# </body>
# </html>
# '''

# # Updated HTML template to include humanization button and editable content
# RESULT_TEMPLATE = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Blog Generation Result</title>
#     <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
#     <script>
#         function humanizeBlog() {
#             fetch('/humanize', {
#                 method: 'POST',
#                 headers: {
#                     'Content-Type': 'application/json',
#                 },
#                 body: JSON.stringify({
#                     content: document.getElementById('blog-content').textContent
#                 })
#             })
#             .then(response => response.json())
#             .then(data => {
#                 document.getElementById('humanized-content').textContent = data.humanized_content;
#                 document.getElementById('humanize-section').style.display = 'block';
#             })
#             .catch(error => {
#                 console.error('Error:', error);
#                 alert('Failed to humanize the blog');
#             });
#         }

#         function saveEdits() {
#             const editedContent = document.getElementById('blog-content').textContent;
#             fetch('/save', {
#                 method: 'POST',
#                 headers: {
#                     'Content-Type': 'application/json',
#                 },
#                 body: JSON.stringify({
#                     content: editedContent
#                 })
#             })
#             .then(response => response.json())
#             .then(data => {
#                 alert('Edits saved successfully');
#             })
#             .catch(error => {
#                 console.error('Error:', error);
#                 alert('Failed to save edits');
#             });
#         }
#     </script>
# </head>
# <body class="bg-gradient-to-br from-gray-100 to-gray-200 min-h-screen flex items-center justify-center p-4">
#     <div class="container mx-auto max-w-6xl bg-white rounded-2xl shadow-2xl overflow-hidden">
#         <div class="bg-gradient-to-r from-blue-500 to-purple-600 p-6">
#             <h1 class="text-4xl font-extrabold text-center text-white drop-shadow-lg">Generated Blog Content</h1>
#         </div>

#         <div class="p-8 space-y-8">
#             <div class="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-lg">
#                 <h2 class="text-2xl font-bold mb-4 text-blue-600 flex items-center">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
#                     </svg>
#                     Blog Outline
#                 </h2>
#                 <pre class="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-wrap text-gray-700">{{ outline }}</pre>
#             </div>

#             <div class="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-lg">
#                 <h2 class="text-2xl font-bold mb-4 text-purple-600 flex items-center">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
#                     </svg>
#                     Blog Content
#                 </h2>
#                 <div class="prose max-w-none">
#                     <pre id="blog-content" contenteditable="true" class="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-wrap text-gray-800 focus:ring-2 focus:ring-purple-500 transition">{{ content }}</pre>
#                 </div>
#             </div>

#             <div class="flex justify-center space-x-4">
#                 <button onclick="humanizeBlog()" class="flex items-center bg-gradient-to-r from-green-500 to-teal-600 text-white px-6 py-3 rounded-lg hover:from-green-600 hover:to-teal-700 transition transform hover:scale-105 shadow-lg">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
#                     </svg>
#                     Humanize Blog
#                 </button>
#                 <button onclick="saveEdits()" class="flex items-center bg-gradient-to-r from-yellow-500 to-orange-600 text-white px-6 py-3 rounded-lg hover:from-yellow-600 hover:to-orange-700 transition transform hover:scale-105 shadow-lg">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
#                     </svg>
#                     Save Edits
#                 </button>
#                 <a href="/" class="flex items-center bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-indigo-700 transition transform hover:scale-105 shadow-lg">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
#                     </svg>
#                     Generate Another Blog
#                 </a>
#             </div>

#             <div id="humanize-section" style="display:none;" class="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-lg">
#                 <h2 class="text-2xl font-bold mb-4 text-green-600 flex items-center">
#                     <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
#                         <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
#                     </svg>
#                     Humanized Blog Content
#                 </h2>
#                 <pre id="humanized-content" class="bg-gray-50 p-4 rounded-lg border border-gray-200 whitespace-pre-wrap text-gray-700"></pre>
#             </div>
#         </div>
#     </div>
# </body>
# </html>
# '''

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         product_url = request.form.get('product_url')
#         product_title = request.form.get('product_title')
#         product_description = request.form.get('product_description')
#         primary_keywords = request.form.get('primary_keywords')
#         secondary_keywords = request.form.get('secondary_keywords')
#         intent = request.form.get('intent')

#         try:
#             blog_outline = generate_blog_outline(
#                 product_url, product_title, product_description,
#                 primary_keywords, secondary_keywords, intent
#             )

#             blog_content = generate_blog_content(
#                 blog_outline, product_url, product_title, product_description,
#                 primary_keywords, secondary_keywords, intent
#             )

#             return render_template_string(RESULT_TEMPLATE,
#                                           outline=blog_outline,
#                                           content=blog_content)

#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

#     return render_template_string(INDEX_TEMPLATE)

# @app.route('/general', methods=['POST'])
# def generate_general_blog():
#     keywords = request.form.get('keywords')
#     primary_keywords = request.form.get('primary_keywords')
#     prompt = request.form.get('prompt')

#     try:
#         blog_outline = generate_general_blog_outline(keywords, primary_keywords, prompt)
#         blog_content = generate_general_blog_content(blog_outline, keywords, primary_keywords, prompt)

#         return render_template_string(RESULT_TEMPLATE,
#                                       outline=blog_outline,
#                                       content=blog_content)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # Add a new route for humanization
# @app.route('/humanize', methods=['POST'])
# def humanize_blog():
#     try:
#         # Get the content from the request
#         data = request.get_json()
#         content = data.get('content', '')

#         # Humanize the content
#         humanized_content = humanize_text(content)

#         return jsonify({
#             'humanized_content': humanized_content
#         })
#     except Exception as e:
#         return jsonify({
#             'error': str(e)
#         }), 500

# # Add a new route to save edits
# @app.route('/save', methods=['POST'])
# def save_edits():
#     try:
#         # Get the edited content from the request
#         data = request.get_json()
#         edited_content = data.get('content', '')

#         # Here you can add logic to save the edited content to a database or file
#         # For this example, we'll just return a success message

#         return jsonify({
#             'message': 'Edits saved successfully'
#         })
#     except Exception as e:
#         return jsonify({
#             'error': str(e)
#         }), 500

# if __name__ == '__main__':
#     app.run(debug=True)
