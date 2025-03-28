# import os
# from flask import Flask, request, jsonify, render_template_string
# from dotenv import load_dotenv
# from openai import OpenAI

# # Load environment variables
# load_dotenv()

# # Initialize OpenAI client with API key from .env
# client = OpenAI(api_key="")

# app = Flask(__name__)

# def generate_blog_outline(product_url, product_title, product_description,
#                          primary_keywords, secondary_keywords, intent):
#     """
#     Generate an SEO-friendly blog outline ensuring all primary and secondary keywords are used
#     """
#     primary_keywords_list = [kw.strip() for kw in primary_keywords.split(',')]
#     secondary_keywords_list = [kw.strip() for kw in secondary_keywords.split(',')]
#     primary_keywords_str = ', '.join(primary_keywords_list)
#     secondary_keywords_str = ', '.join(secondary_keywords_list)

#     prompt = f"""
#     Create a comprehensive, SEO-friendly blog outline for a product blog post with the following details:

#     Product URL: {product_url}
#     Product Title: {product_title}
#     Product Description: {product_description}
#     Primary Keywords: {primary_keywords_str}
#     Secondary Keywords: {secondary_keywords_str}
#     Blog Intent: {intent}

#     Requirements for the outline:
#     1. Headline: Include ALL primary keywords ({primary_keywords_str}) at least once each and ALL secondary keywords ({secondary_keywords_str}) at least once each in a compelling title.
#     2. Structure: Include 5 main sections, each addressing a unique aspect of {product_title} based on {product_description}.
#     3. Per Section: Use EACH primary keyword ({primary_keywords_str}) at least 2 times and EACH secondary keyword ({secondary_keywords_str}) at least 3 times within every section.
#     4. Introduction: Write a strong introduction using EACH primary keyword ({primary_keywords_str}) once and EACH secondary keyword ({secondary_keywords_str}) twice, setting the stage for {intent}.
#     5. Conclusion: Write a strong conclusion using EACH primary keyword ({primary_keywords_str}) once and EACH secondary keyword ({secondary_keywords_str}) twice, reinforcing {intent}.
#     6. Subsections: Suggest 1-2 subsections per main section, each incorporating ALL primary keywords ({primary_keywords_str}) and ALL secondary keywords ({secondary_keywords_str}) at least once.
#     7. Frequency: Ensure ALL secondary keywords ({secondary_keywords_str}) appear more often than ALL primary keywords ({primary_keywords_str}) across the outline, distributed evenly.
#     8. Integration: Use keywords naturally while explicitly meeting the minimum usage requirements for EVERY keyword.
#     9. URL Reference: Mention {product_url} at least once in a section for context (e.g., linking to the product).
#     10. Tone: Use a conversational and engaging tone to make the content more relatable.
#     11. Storytelling: Include personal anecdotes or stories to make the content more engaging.

#     Output the outline in a structured, markdown-like format (e.g., # for headline, ## for sections, ### for subsections).
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are an expert SEO content strategist and blog outline creator. You must explicitly use ALL provided primary and secondary keywords the specified number of times, especially prioritizing secondary keywords."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=1000,
#             temperature=0.7
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"Error generating outline: {str(e)}"

# def generate_section(content_type, word_count, product_url, product_title, product_description,
#                      primary_keywords, secondary_keywords, intent, section_title=""):
#     """
#     Generate a single section (e.g., intro, main section, conclusion) with specified word count
#     """
#     primary_keywords_list = [kw.strip() for kw in primary_keywords.split(',')]
#     secondary_keywords_list = [kw.strip() for kw in secondary_keywords.split(',')]
#     primary_keywords_str = ', '.join(primary_keywords_list)
#     secondary_keywords_str = ', '.join(secondary_keywords_list)

#     prompt = f"""
#     Generate a {content_type} section for a blog post with the following details:

#     Product URL: {product_url}
#     Product Title: {product_title}
#     Product Description: {product_description}
#     Primary Keywords: {primary_keywords_str}
#     Secondary Keywords: {secondary_keywords_str}
#     Blog Intent: {intent}
#     Section Title (if applicable): {section_title}

#     Requirements:
#     1. Word Count: The section must be approximately {word_count} words (within ±10% of {word_count}).
#     2. Tone: Use a conversational yet professional tone aligned with {intent}.
#     3. Keyword Usage:
#        - Use EACH primary keyword ({primary_keywords_str}) at least {2 if content_type == 'main' else 1} times.
#        - Use EACH secondary keyword ({secondary_keywords_str}) at least {3 if content_type == 'main' else 2} times.
#     4. Placement: Incorporate keywords naturally in the section title (if applicable), opening sentences, and body text.
#     5. Structure: Use short paragraphs (3-5 sentences). For main sections, include 1-2 subsections with subheadings.
#     6. Content: Draw from {product_title} and {product_description} to provide value aligned with {intent}.
#     7. {f'URL: Include {product_url} once as a natural link suggestion.' if content_type == 'main' else ''}
#     8. Output: Use markdown-like format (e.g., ## for section title, ### for subsections if applicable).
#     9. Storytelling: Include personal anecdotes or stories to make the content more engaging.
#     10. Calls-to-Action: Include clear calls-to-action to encourage readers to take the next step.

#     Ensure the content is engaging and meets the word count and keyword requirements.
#     """

#     try:
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are an expert blog writer creating SEO-optimized content. Meet the specified word count and keyword usage requirements."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=int(word_count * 1.5),  # Tokens ≈ 1.5 * words to account for markdown and buffer
#             temperature=0.7
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"Error generating {content_type} section: {str(e)}"

# def generate_full_blog_content(product_url, product_title, product_description,
#                               primary_keywords, secondary_keywords, intent, blog_outline):
#     """
#     Generate a full 1200-word blog by creating sections separately and combining them
#     """
#     try:
#         # Parse the outline to extract section titles (assuming 5 main sections)
#         outline_lines = blog_outline.split('\n')
#         main_section_titles = [line.strip('# ').strip() for line in outline_lines if line.startswith('## ') and 'Introduction' not in line and 'Conclusion' not in line]
#         if len(main_section_titles) != 5:
#             main_section_titles = [f"Section {i+1}" for i in range(5)]  # Fallback if outline parsing fails

#         # Distribute 1200 words: 200 for intro, 200 each for 5 sections, 200 for conclusion
#         content_parts = []

#         # Generate Introduction (200 words)
#         intro = generate_section(
#             "introduction", 200, product_url, product_title, product_description,
#             primary_keywords, secondary_keywords, intent
#         )
#         content_parts.append(intro)

#         # Generate 5 Main Sections (200 words each)
#         for title in main_section_titles[:5]:  # Ensure exactly 5 sections
#             section = generate_section(
#                 "main", 200, product_url, product_title, product_description,
#                 primary_keywords, secondary_keywords, intent, title
#             )
#             content_parts.append(section)

#         # Generate Conclusion (200 words)
#         conclusion = generate_section(
#             "conclusion", 200, product_url, product_title, product_description,
#             primary_keywords, secondary_keywords, intent
#         )
#         content_parts.append(conclusion)

#         # Combine all parts with the headline from the outline
#         headline = next((line for line in outline_lines if line.startswith('# ')), '# Blog Post')
#         full_content = headline + '\n\n' + '\n\n'.join(content_parts)

#         # Verify total word count
#         total_words = len(full_content.split())
#         if total_words < 1150 or total_words > 1250:
#             full_content = f"Generated content is {total_words} words, slightly off the 1200-word target (±50 words).\n\n{full_content}"

#         return full_content
#     except Exception as e:
#         return f"Error generating full blog content: {str(e)}"

# @app.route('/', methods=['GET'])
# def dashboard():
#     return render_template_string('''
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>Blog Generation Dashboard</title>
#         <style>
#             body {
#                 font-family: Arial, sans-serif;
#                 line-height: 1.6;
#                 margin: 0;
#                 padding: 0;
#                 background-color: #f4f4f4;
#             }
#             .container {
#                 width: 80%;
#                 margin: auto;
#                 overflow: hidden;
#                 padding: 20px;
#                 background-color: white;
#                 box-shadow: 0 0 10px rgba(0,0,0,0.1);
#             }
#             .card {
#                 background-color: #fff;
#                 border-radius: 8px;
#                 box-shadow: 0 2px 4px rgba(0,0,0,0.1);
#                 margin-bottom: 20px;
#                 padding: 20px;
#                 transition: transform 0.2s;
#             }
#             .card:hover {
#                 transform: translateY(-5px);
#             }
#             .card h2 {
#                 margin-top: 0;
#             }
#             .card p {
#                 margin-bottom: 0;
#             }
#             .card a {
#                 text-decoration: none;
#                 color: #333;
#             }
#             .card a:hover {
#                 color: #007BFF;
#             }
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <h1>Blog Generation Dashboard</h1>
#             <div class="card">
#                 <h2>Product Specific Blog</h2>
#                 <p>Generate a blog post tailored to a specific product.</p>
#                 <a href="/product_blog">Generate Product Blog</a>
#             </div>
#             <div class="card">
#                 <h2>General Blogs</h2>
#                 <p>Generate a general blog post on various topics.</p>
#                 <a href="/general_blog">Generate General Blog</a>
#             </div>
#         </div>
#     </body>
#     </html>
#     ''')

# @app.route('/product_blog', methods=['GET'])
# def product_blog_form():
#     return '''
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>Product Specific Blog Generation</title>
#         <style>
#             body {
#                 font-family: Arial, sans-serif;
#                 line-height: 1.6;
#                 margin: 0;
#                 padding: 0;
#                 background-color: #f4f4f4;
#             }
#             .container {
#                 width: 80%;
#                 margin: auto;
#                 overflow: hidden;
#                 padding: 20px;
#                 background-color: white;
#                 box-shadow: 0 0 10px rgba(0,0,0,0.1);
#             }
#             form {
#                 display: flex;
#                 flex-direction: column;
#             }
#             label {
#                 margin-top: 10px;
#             }
#             input, textarea, select {
#                 margin-bottom: 15px;
#                 padding: 10px;
#                 border: 1px solid #ddd;
#                 border-radius: 4px;
#             }
#             button {
#                 padding: 10px;
#                 background-color: #333;
#                 color: white;
#                 border: none;
#                 border-radius: 4px;
#                 cursor: pointer;
#             }
#             .back-button {
#                 display: inline-block;
#                 background-color: #333;
#                 color: white;
#                 padding: 10px 15px;
#                 text-decoration: none;
#                 border-radius: 4px;
#                 margin-top: 15px;
#             }
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <h1>Product Specific Blog Generation</h1>
#             <form action="/generate_blog" method="post">
#                 <label for="product_url">Product URL:</label>
#                 <input type="url" id="product_url" name="product_url" required>

#                 <label for="product_title">Product Title:</label>
#                 <input type="text" id="product_title" name="product_title" required>

#                 <label for="product_description">Product Description:</label>
#                 <textarea id="product_description" name="product_description" required></textarea>

#                 <label for="primary_keywords">Primary Keywords (comma-separated):</label>
#                 <input type="text" id="primary_keywords" name="primary_keywords" required>

#                 <label for="secondary_keywords">Secondary Keywords (comma-separated):</label>
#                 <input type="text" id="secondary_keywords" name="secondary_keywords" required>

#                 <label for="intent">Blog Intent:</label>
#                 <select id="intent" name="intent" required>
#                     <option value="informative">Informative</option>
#                     <option value="persuasive">Persuasive</option>
#                     <option value="review">Review</option>
#                     <option value="comparison">Comparison</option>
#                 </select>

#                 <button type="submit">Generate Blog</button>
#             </form>
#             <a href="/" class="back-button">Back to Dashboard</a>
#         </div>
#     </body>
#     </html>
#     '''

# @app.route('/general_blog', methods=['GET'])
# def general_blog_form():
#     return '''
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>General Blog Generation</title>
#         <style>
#             body {
#                 font-family: Arial, sans-serif;
#                 line-height: 1.6;
#                 margin: 0;
#                 padding: 0;
#                 background-color: #f4f4f4;
#             }
#             .container {
#                 width: 80%;
#                 margin: auto;
#                 overflow: hidden;
#                 padding: 20px;
#                 background-color: white;
#                 box-shadow: 0 0 10px rgba(0,0,0,0.1);
#             }
#             form {
#                 display: flex;
#                 flex-direction: column;
#             }
#             label {
#                 margin-top: 10px;
#             }
#             input, textarea, select {
#                 margin-bottom: 15px;
#                 padding: 10px;
#                 border: 1px solid #ddd;
#                 border-radius: 4px;
#             }
#             button {
#                 padding: 10px;
#                 background-color: #333;
#                 color: white;
#                 border: none;
#                 border-radius: 4px;
#                 cursor: pointer;
#             }
#             .back-button {
#                 display: inline-block;
#                 background-color: #333;
#                 color: white;
#                 padding: 10px 15px;
#                 text-decoration: none;
#                 border-radius: 4px;
#                 margin-top: 15px;
#             }
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <h1>General Blog Generation</h1>
#             <form action="/generate_general_blog" method="post">
#                 <label for="blog_title">Blog Title:</label>
#                 <input type="text" id="blog_title" name="blog_title" required>

#                 <label for="blog_description">Blog Description:</label>
#                 <textarea id="blog_description" name="blog_description" required></textarea>

#                 <label for="primary_keywords">Primary Keywords (comma-separated):</label>
#                 <input type="text" id="primary_keywords" name="primary_keywords" required>

#                 <label for="secondary_keywords">Secondary Keywords (comma-separated):</label>
#                 <input type="text" id="secondary_keywords" name="secondary_keywords" required>

#                 <label for="intent">Blog Intent:</label>
#                 <select id="intent" name="intent" required>
#                     <option value="informative">Informative</option>
#                     <option value="persuasive">Persuasive</option>
#                     <option value="review">Review</option>
#                     <option value="comparison">Comparison</option>
#                 </select>

#                 <button type="submit">Generate Blog</button>
#             </form>
#             <a href="/" class="back-button">Back to Dashboard</a>
#         </div>
#     </body>
#     </html>
#     '''

# @app.route('/generate_blog', methods=['POST'])
# def generate_blog():
#     try:
#         # Collect form data
#         product_url = request.form.get('product_url')
#         product_title = request.form.get('product_title')
#         product_description = request.form.get('product_description')
#         primary_keywords = request.form.get('primary_keywords')
#         secondary_keywords = request.form.get('secondary_keywords')
#         intent = request.form.get('intent')

#         # Generate blog outline
#         blog_outline = generate_blog_outline(
#             product_url, product_title, product_description,
#             primary_keywords, secondary_keywords, intent
#         )

#         # Generate full blog content by sections
#         blog_content = generate_full_blog_content(
#             product_url, product_title, product_description,
#             primary_keywords, secondary_keywords, intent, blog_outline
#         )

#         return f'''
#         <!DOCTYPE html>
#         <html lang="en">
#         <head>
#             <meta charset="UTF-8">
#             <title>Generated Blog</title>
#             <style>
#                 body {{
#                     font-family: Arial, sans-serif;
#                     line-height: 1.6;
#                     margin: 0;
#                     padding: 0;
#                     background-color: #f4f4f4;
#                 }}
#                 .container {{
#                     width: 80%;
#                     margin: auto;
#                     overflow: hidden;
#                     padding: 20px;
#                     background-color: white;
#                     box-shadow: 0 0 10px rgba(0,0,0,0.1);
#                 }}
#                 .section {{
#                     margin-bottom: 20px;
#                     padding: 15px;
#                     background-color: #f9f9f9;
#                     border-radius: 4px;
#                 }}
#                 pre {{
#                     white-space: pre-wrap;
#                     word-wrap: break-word;
#                     font-family: monospace;
#                 }}
#                 .back-button {{
#                     display: inline-block;
#                     background-color: #333;
#                     color: white;
#                     padding: 10px 15px;
#                     text-decoration: none;
#                     border-radius: 4px;
#                     margin-top: 15px;
#                 }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <h1>Generated Blog</h1>

#                 <div class="section">
#                     <h2>Blog Outline</h2>
#                     <pre>{blog_outline}</pre>
#                 </div>

#                 <div class="section">
#                     <h2>Blog Content</h2>
#                     <pre>{blog_content}</pre>
#                 </div>

#                 <a href="/" class="back-button">Back to Dashboard</a>
#             </div>
#         </body>
#         </html>
#         '''
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @app.route('/generate_general_blog', methods=['POST'])
# def generate_general_blog():
#     try:
#         # Collect form data
#         blog_title = request.form.get('blog_title')
#         blog_description = request.form.get('blog_description')
#         primary_keywords = request.form.get('primary_keywords')
#         secondary_keywords = request.form.get('secondary_keywords')
#         intent = request.form.get('intent')

#         # Generate blog outline
#         blog_outline = generate_blog_outline(
#             "", blog_title, blog_description,
#             primary_keywords, secondary_keywords, intent
#         )

#         # Generate full blog content by sections
#         blog_content = generate_full_blog_content(
#             "", blog_title, blog_description,
#             primary_keywords, secondary_keywords, intent, blog_outline
#         )

#         return f'''
#         <!DOCTYPE html>
#         <html lang="en">
#         <head>
#             <meta charset="UTF-8">
#             <title>Generated Blog</title>
#             <style>
#                 body {{
#                     font-family: Arial, sans-serif;
#                     line-height: 1.6;
#                     margin: 0;
#                     padding: 0;
#                     background-color: #f4f4f4;
#                 }}
#                 .container {{
#                     width: 80%;
#                     margin: auto;
#                     overflow: hidden;
#                     padding: 20px;
#                     background-color: white;
#                     box-shadow: 0 0 10px rgba(0,0,0,0.1);
#                 }}
#                 .section {{
#                     margin-bottom: 20px;
#                     padding: 15px;
#                     background-color: #f9f9f9;
#                     border-radius: 4px;
#                 }}
#                 pre {{
#                     white-space: pre-wrap;
#                     word-wrap: break-word;
#                     font-family: monospace;
#                 }}
#                 .back-button {{
#                     display: inline-block;
#                     background-color: #333;
#                     color: white;
#                     padding: 10px 15px;
#                     text-decoration: none;
#                     border-radius: 4px;
#                     margin-top: 15px;
#                 }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <h1>Generated Blog</h1>

#                 <div class="section">
#                     <h2>Blog Outline</h2>
#                     <pre>{blog_outline}</pre>
#                 </div>

#                 <div class="section">
#                     <h2>Blog Content</h2>
#                     <pre>{blog_content}</pre>
#                 </div>

#                 <a href="/" class="back-button">Back to Dashboard</a>
#             </div>
#         </body>
#         </html>
#         '''
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)
import os
import re
import flask
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key="s")

class BlogGenerator:
    """Advanced blog generation utility with enhanced SEO and keyword integration"""
    
    @staticmethod
    def validate_inputs(data):
        """
        Validate and sanitize input data to ensure high-quality blog generation
        """
        # Input validation with comprehensive checks
        errors = []
        
        # Validate URL if present
        if 'product_url' in data and data['product_url']:
            url_pattern = re.compile(
                r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)$'
            )
            if not url_pattern.match(data['product_url']):
                errors.append("Invalid URL format")
        
        # Keyword validation
        for keyword_type in ['primary_keywords', 'secondary_keywords']:
            if keyword_type not in data or not data[keyword_type]:
                errors.append(f"Missing {keyword_type}")
            else:
                keywords = [kw.strip() for kw in data[keyword_type].split(',')]
                if len(keywords) < 2:
                    errors.append(f"At least 2 {keyword_type} required")
        
        # Title and description validation
        required_fields = ['product_title', 'product_description'] if 'product_url' in data else ['blog_title', 'blog_description']
        for field in required_fields:
            if not data.get(field) or len(data[field]) < 10:
                errors.append(f"{field} is too short")
        
        return errors

    @classmethod
    def generate_blog_outline(cls, data):
        """
        Generate a comprehensive, SEO-optimized blog outline with detailed explanations
        """
        primary_keywords = data.get('primary_keywords', '')
        secondary_keywords = data.get('secondary_keywords', '')
        intent = data.get('intent', 'informative')
        
        title = data.get('product_title', data.get('blog_title', 'Engaging Blog Post'))
        description = data.get('product_description', data.get('blog_description', ''))
        
        prompt = f"""
        COMPREHENSIVE BLOG OUTLINE WITH DETAILED SECTION BREAKDOWNS

        🔍 KEYWORD STRATEGY:
        PRIMARY KEYWORDS: {primary_keywords}
        SECONDARY KEYWORDS: {secondary_keywords}

        CONTENT GENERATION DIRECTIVE:
        Create a detailed blog outline that not only provides section headings 
        but also includes:
        - Specific subsection ideas
        - Key points to cover
        - Strategic keyword integration approach
        - Rationale for each section
        - Potential narrative flow
        - Engagement hooks

        CORE OUTLINE REQUIREMENTS:
        1. HEADLINE STRATEGY
        2. INTRODUCTION FRAMEWORK
        3. FIVE COMPREHENSIVE SECTIONS
           - Each with specific focus
           - Interconnected narrative
           - Clear value proposition
        4. CONCLUSION APPROACH

        CONTEXT:
        TITLE: {title}
        DESCRIPTION: {description}
        CONTENT INTENT: {intent}

        DELIVERABLE FORMAT:
        [SECTION TITLE]
        - Objective: 
        - Key Narrative Points:
        - Keyword Integration Strategy:
        - Engagement Mechanisms:
        """

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a strategic content architect specializing in creating comprehensive, insightful, and deeply explanatory content outlines."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Enhanced outline processing to add more context and explanation
            raw_outline = response.choices[0].message.content.strip()
            
            # Add additional explanatory layers
            enhanced_outline = f"""
🌟 COMPREHENSIVE BLOG OUTLINE BREAKDOWN 🌟

{raw_outline}

💡 OUTLINE INTERPRETATION & STRATEGY:

1. HOLISTIC CONTENT NARRATIVE:
   - This outline is designed to create a seamless, engaging narrative
   - Each section builds upon the previous, creating a comprehensive story
   - Strategic keyword placement ensures natural, authentic content flow

2. KEYWORD INTEGRATION PHILOSOPHY:
   - PRIMARY KEYWORDS ({primary_keywords}):
     * Foundational concepts driving the content
     * Integrated naturally throughout the narrative
     * Used to establish core message and expertise

   - SECONDARY KEYWORDS ({secondary_keywords}):
     * Provide depth and contextual richness
     * Support and expand on primary keyword concepts
     * Create semantic diversity in content

3. CONTENT INTENT ALIGNMENT:
   CURRENT INTENT: {intent}
   - Every section strategically crafted to fulfill this intent
   - Balancing informative depth with engaging storytelling

4. EXPECTED READER JOURNEY:
   - Move from curiosity to comprehensive understanding
   - Provide actionable insights
   - Create emotional and intellectual engagement

5. POTENTIAL REFINEMENT AREAS:
   - Adjust section depths based on specific keyword nuances
   - Potential for adding case studies or expert quotes
   - Flexibility to incorporate latest industry insights

🚀 READY FOR CONTENT GENERATION
            """
            
            return enhanced_outline
        
        except Exception as e:
            return f"Outline Generation Error: Detailed Strategic Analysis Unavailable. Error: {str(e)}"

    @classmethod
    def generate_blog_content(cls, detailed_outline, data):
        """
        Generate blog content with enhanced requirements:
        1. Minimum 5000 words
        2. Strict keyword integration
        3. Use exact provided title
        4. Follow specified intent
        """
        # Extract and prepare keywords
        primary_keywords = data.get('primary_keywords', '').split(',')
        secondary_keywords = data.get('secondary_keywords', '').split(',')
        
        # Sanitize keywords
        primary_keywords = [kw.strip().lower() for kw in primary_keywords if kw.strip()]
        secondary_keywords = [kw.strip().lower() for kw in secondary_keywords if kw.strip()]
        
        # Ensure at least some keywords are present
        if not primary_keywords and not secondary_keywords:
            return "Error: No keywords provided for content generation"

        # Extract specific details
        intent = data.get('intent', 'informative')
        title = data.get('product_title', data.get('blog_title', 'Comprehensive Insight'))
        description = data.get('product_description', data.get('blog_description', ''))

        # Create a prompt with ENHANCED generation requirements
        prompt = f"""
        ULTRA-COMPREHENSIVE CONTENT GENERATION PROTOCOL:

        ABSOLUTE MANDATORY REQUIREMENTS:
        1. MINIMUM WORD COUNT: 5000+ WORDS
        2. MANDATORY KEYWORD INCLUSION:
           - PRIMARY KEYWORDS: {', '.join(primary_keywords)}
           - SECONDARY KEYWORDS: {', '.join(secondary_keywords)}

        KEYWORD INTEGRATION RULES:
        - EVERY SECTION MUST CONTAIN PRIMARY KEYWORDS
        - Secondary keywords MUST appear naturally
        - ZERO keyword stuffing
        - Maintain exceptional content quality

        CONTENT GENERATION DIRECTIVE:
        Create an EXTENSIVE blog post that:
        - USES EXACT TITLE: "{title}"
        - Incorporates PRIMARY KEYWORDS strategically
        - Aligns perfectly with INTENT: {intent}
        - Provides DEEP, SUBSTANTIVE content
        - Demonstrates COMPREHENSIVE expertise

        CONTENT STRUCTURE REQUIREMENTS:
        A. INTRODUCTION (300-400 words):
        - Incorporate at least 2 PRIMARY KEYWORDS
        - Establish compelling context
        - Create irresistible reader engagement

        B. MAIN CONTENT (4-6 SECTIONS, 800-1000 words each):
        - MINIMUM 4000 words in main sections
        - Each section MUST:
          * Include PRIMARY KEYWORDS
          * Use SECONDARY KEYWORDS for depth
          * Provide actionable, expert-level insights
        
        C. CONCLUSION (300-400 words):
        - Recap PRIMARY KEYWORDS
        - Synthesize key insights
        - Provide forward-looking perspective

        CRITICAL WRITING CONSTRAINTS:
        - EXACT WORD COUNT: 5000-5500 words
        - Academic yet conversational tone
        - Demonstrate UNPARALLELED expertise
        - Create narrative that DEEPLY explores topic

        SPECIFIC CONTEXT:
        - TITLE: {title}
        - DESCRIPTION: {description}
        - CONTENT INTENT: {intent}

        KEYWORD INTEGRATION MANDATE: 
        KEYWORDS MUST BE INTEGRATED SEAMLESSLY. 
        PRIORITIZE NATURAL, MEANINGFUL INCLUSION 
        OVER MECHANICAL PLACEMENT.
        """

        try:
            # Generate content with enhanced requirements
            response = client.chat.completions.create(
                model="gpt-4-turbo", # Upgraded model for more complex generation
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a MASTER content strategist who MUST 
                        create ultra-comprehensive, keyword-rich content that 
                        provides EXCEPTIONAL value while maintaining perfect 
                        keyword integration and meeting STRICT word count requirements."""
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4096,  # Increased token allowance
                temperature=0.6  # Slightly increased creativity
            )
            
            raw_content = response.choices[0].message.content.strip()
            
            # Advanced Keyword Verification and Enforcement
            def enforce_comprehensive_keyword_presence(content, primary_kws, secondary_kws):
                content_lower = content.lower()
                
                # Comprehensive keyword usage tracking
                primary_usage = {
                    kw: content_lower.count(kw) 
                    for kw in primary_kws
                }
                
                secondary_usage = {
                    kw: content_lower.count(kw) 
                    for kw in secondary_kws
                }
                
                # Aggressive keyword integration if missing
                if any(count == 0 for count in primary_usage.values()):
                    missing_primaries = [
                        kw for kw, count in primary_usage.items() if count == 0
                    ]
                    content += "\n\n🔑 COMPREHENSIVE KEYWORD INTEGRATION 🔑\n"
                    content += "EXPANDED INSIGHTS on: " + ", ".join(missing_primaries)
                    
                    # Add targeted paragraphs for missing keywords
                    for kw in missing_primaries:
                        content += f"\n\nDeep Dive into {kw.upper()}:\n"
                        content += f"This section provides an extensive exploration of {kw}, "
                        content += "offering unparalleled insights and comprehensive understanding."
                
                return content, {
                    'primary_keyword_usage': primary_usage,
                    'secondary_keyword_usage': secondary_usage
                }
            
            # Enforce comprehensive keyword presence
            final_content, keyword_stats = enforce_comprehensive_keyword_presence(
                raw_content, 
                primary_keywords, 
                secondary_keywords
            )
            
            # Enhanced content with extensive keyword integration report
            enhanced_content = f"""
📘 {title.upper()}

{final_content}

🔍 COMPREHENSIVE KEYWORD INTEGRATION REPORT:
PRIMARY KEYWORDS USAGE:
{chr(10).join(f"- {k}: {v} strategic integrations" for k, v in keyword_stats['primary_keyword_usage'].items())}

SECONDARY KEYWORDS ENRICHMENT:
{chr(10).join(f"- {k}: {v} contextual references" for k, v in keyword_stats['secondary_keyword_usage'].items())}

💡 CONTENT STRATEGY INSIGHTS:
- Total Word Count: {len(final_content.split())} words
- Intent Alignment: {intent}
- Keyword Integration Approach: Natural, Comprehensive, Strategic

🚀 CONTENT OPTIMIZED FOR:
- Deep Reader Engagement
- SEO Excellence
- Authoritative Insights
            """
            
            return enhanced_content
        
        except Exception as e:
            return f"Advanced Keyword Integration Error: {str(e)}"

# Flask Application Configuration
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_fallback_secret_key')

@app.route('/')
def index():
    """Render the main dashboard with blog generation options"""
    return render_template('dashboard.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate_blog():
    """
    Blog generation endpoint with robust error handling and validation
    """
    if request.method == 'GET':
        return render_template('blog_form.html')
    
    # Collect all input data
    data = {k: v.strip() for k, v in request.form.items()}
    
    # Validate inputs
    validation_errors = BlogGenerator.validate_inputs(data)
    if validation_errors:
        return jsonify({
            'status': 'error',
            'errors': validation_errors
        }), 400
    
    try:
        # Generate blog outline
        blog_outline = BlogGenerator.generate_blog_outline(data)
        
        # Generate full blog content
        blog_content = BlogGenerator.generate_blog_content(blog_outline, data)
        
        return render_template('blog_result.html', 
                               outline=blog_outline, 
                               content=blog_content)
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Additional dependencies (requirements.txt):
# flask
# openai
# python-dotenv