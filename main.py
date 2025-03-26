import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client with API key from .env
client = OpenAI(api_key=os.getenv("API_KEY"))

app = Flask(__name__)

def generate_blog_outline(product_url, product_title, product_description,
                         primary_keywords, secondary_keywords, intent):
    """
    Generate an SEO-friendly blog outline ensuring all primary and secondary keywords are used
    """
    primary_keywords_list = [kw.strip() for kw in primary_keywords.split(',')]
    secondary_keywords_list = [kw.strip() for kw in secondary_keywords.split(',')]
    primary_keywords_str = ', '.join(primary_keywords_list)
    secondary_keywords_str = ', '.join(secondary_keywords_list)

    prompt = f"""
    Create a comprehensive, SEO-friendly blog outline for a product blog post with the following details:

    Product URL: {product_url}
    Product Title: {product_title}
    Product Description: {product_description}
    Primary Keywords: {primary_keywords_str}
    Secondary Keywords: {secondary_keywords_str}
    Blog Intent: {intent}

    Requirements for the outline:
    1. Headline: Include ALL primary keywords ({primary_keywords_str}) at least once each and ALL secondary keywords ({secondary_keywords_str}) at least once each in a compelling title.
    2. Structure: Include 5 main sections, each addressing a unique aspect of {product_title} based on {product_description}.
    3. Per Section: Use EACH primary keyword ({primary_keywords_str}) at least 2 times and EACH secondary keyword ({secondary_keywords_str}) at least 3 times within every section.
    4. Introduction: Write a strong introduction using EACH primary keyword ({primary_keywords_str}) once and EACH secondary keyword ({secondary_keywords_str}) twice, setting the stage for {intent}.
    5. Conclusion: Write a strong conclusion using EACH primary keyword ({primary_keywords_str}) once and EACH secondary keyword ({secondary_keywords_str}) twice, reinforcing {intent}.
    6. Subsections: Suggest 1-2 subsections per main section, each incorporating ALL primary keywords ({primary_keywords_str}) and ALL secondary keywords ({secondary_keywords_str}) at least once.
    7. Frequency: Ensure ALL secondary keywords ({secondary_keywords_str}) appear more often than ALL primary keywords ({primary_keywords_str}) across the outline, distributed evenly.
    8. Integration: Use keywords naturally while explicitly meeting the minimum usage requirements for EVERY keyword.
    9. URL Reference: Mention {product_url} at least once in a section for context (e.g., linking to the product).
    10. Tone: Use a conversational and engaging tone to make the content more relatable.
    11. Storytelling: Include personal anecdotes or stories to make the content more engaging.

    Output the outline in a structured, markdown-like format (e.g., # for headline, ## for sections, ### for subsections).
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert SEO content strategist and blog outline creator. You must explicitly use ALL provided primary and secondary keywords the specified number of times, especially prioritizing secondary keywords."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating outline: {str(e)}"

def generate_section(content_type, word_count, product_url, product_title, product_description,
                     primary_keywords, secondary_keywords, intent, section_title=""):
    """
    Generate a single section (e.g., intro, main section, conclusion) with specified word count
    """
    primary_keywords_list = [kw.strip() for kw in primary_keywords.split(',')]
    secondary_keywords_list = [kw.strip() for kw in secondary_keywords.split(',')]
    primary_keywords_str = ', '.join(primary_keywords_list)
    secondary_keywords_str = ', '.join(secondary_keywords_list)

    prompt = f"""
    Generate a {content_type} section for a blog post with the following details:

    Product URL: {product_url}
    Product Title: {product_title}
    Product Description: {product_description}
    Primary Keywords: {primary_keywords_str}
    Secondary Keywords: {secondary_keywords_str}
    Blog Intent: {intent}
    Section Title (if applicable): {section_title}

    Requirements:
    1. Word Count: The section must be approximately {word_count} words (within ±10% of {word_count}).
    2. Tone: Use a conversational yet professional tone aligned with {intent}.
    3. Keyword Usage:
       - Use EACH primary keyword ({primary_keywords_str}) at least {2 if content_type == 'main' else 1} times.
       - Use EACH secondary keyword ({secondary_keywords_str}) at least {3 if content_type == 'main' else 2} times.
    4. Placement: Incorporate keywords naturally in the section title (if applicable), opening sentences, and body text.
    5. Structure: Use short paragraphs (3-5 sentences). For main sections, include 1-2 subsections with subheadings.
    6. Content: Draw from {product_title} and {product_description} to provide value aligned with {intent}.
    7. {f'URL: Include {product_url} once as a natural link suggestion.' if content_type == 'main' else ''}
    8. Output: Use markdown-like format (e.g., ## for section title, ### for subsections if applicable).
    9. Storytelling: Include personal anecdotes or stories to make the content more engaging.
    10. Calls-to-Action: Include clear calls-to-action to encourage readers to take the next step.

    Ensure the content is engaging and meets the word count and keyword requirements.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert blog writer creating SEO-optimized content. Meet the specified word count and keyword usage requirements."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=int(word_count * 1.5),  # Tokens ≈ 1.5 * words to account for markdown and buffer
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating {content_type} section: {str(e)}"

def generate_full_blog_content(product_url, product_title, product_description,
                              primary_keywords, secondary_keywords, intent, blog_outline):
    """
    Generate a full 1200-word blog by creating sections separately and combining them
    """
    try:
        # Parse the outline to extract section titles (assuming 5 main sections)
        outline_lines = blog_outline.split('\n')
        main_section_titles = [line.strip('# ').strip() for line in outline_lines if line.startswith('## ') and 'Introduction' not in line and 'Conclusion' not in line]
        if len(main_section_titles) != 5:
            main_section_titles = [f"Section {i+1}" for i in range(5)]  # Fallback if outline parsing fails

        # Distribute 1200 words: 200 for intro, 200 each for 5 sections, 200 for conclusion
        content_parts = []

        # Generate Introduction (200 words)
        intro = generate_section(
            "introduction", 200, product_url, product_title, product_description,
            primary_keywords, secondary_keywords, intent
        )
        content_parts.append(intro)

        # Generate 5 Main Sections (200 words each)
        for title in main_section_titles[:5]:  # Ensure exactly 5 sections
            section = generate_section(
                "main", 200, product_url, product_title, product_description,
                primary_keywords, secondary_keywords, intent, title
            )
            content_parts.append(section)

        # Generate Conclusion (200 words)
        conclusion = generate_section(
            "conclusion", 200, product_url, product_title, product_description,
            primary_keywords, secondary_keywords, intent
        )
        content_parts.append(conclusion)

        # Combine all parts with the headline from the outline
        headline = next((line for line in outline_lines if line.startswith('# ')), '# Blog Post')
        full_content = headline + '\n\n' + '\n\n'.join(content_parts)

        # Verify total word count
        total_words = len(full_content.split())
        if total_words < 1150 or total_words > 1250:
            full_content = f"Generated content is {total_words} words, slightly off the 1200-word target (±50 words).\n\n{full_content}"

        return full_content
    except Exception as e:
        return f"Error generating full blog content: {str(e)}"

@app.route('/', methods=['GET'])
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Blog Generation App</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }
            .container {
                width: 80%;
                margin: auto;
                overflow: hidden;
                padding: 20px;
                background-color: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            form {
                display: flex;
                flex-direction: column;
            }
            label {
                margin-top: 10px;
            }
            input, textarea, select {
                margin-bottom: 15px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                padding: 10px;
                background-color: #333;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Blog Generation App</h1>
            <form action="/generate_blog" method="post">
                <label for="product_url">Product URL:</label>
                <input type="url" id="product_url" name="product_url" required>

                <label for="product_title">Product Title:</label>
                <input type="text" id="product_title" name="product_title" required>

                <label for="product_description">Product Description:</label>
                <textarea id="product_description" name="product_description" required></textarea>

                <label for="primary_keywords">Primary Keywords (comma-separated):</label>
                <input type="text" id="primary_keywords" name="primary_keywords" required>

                <label for="secondary_keywords">Secondary Keywords (comma-separated):</label>
                <input type="text" id="secondary_keywords" name="secondary_keywords" required>

                <label for="intent">Blog Intent:</label>
                <select id="intent" name="intent" required>
                    <option value="informative">Informative</option>
                    <option value="persuasive">Persuasive</option>
                    <option value="review">Review</option>
                    <option value="comparison">Comparison</option>
                </select>

                <button type="submit">Generate Blog</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/generate_blog', methods=['POST'])
def generate_blog():
    try:
        # Collect form data
        product_url = request.form.get('product_url')
        product_title = request.form.get('product_title')
        product_description = request.form.get('product_description')
        primary_keywords = request.form.get('primary_keywords')
        secondary_keywords = request.form.get('secondary_keywords')
        intent = request.form.get('intent')

        # Generate blog outline
        blog_outline = generate_blog_outline(
            product_url, product_title, product_description,
            primary_keywords, secondary_keywords, intent
        )

        # Generate full blog content by sections
        blog_content = generate_full_blog_content(
            product_url, product_title, product_description,
            primary_keywords, secondary_keywords, intent, blog_outline
        )

        return f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Generated Blog</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    width: 80%;
                    margin: auto;
                    overflow: hidden;
                    padding: 20px;
                    background-color: white;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }}
                .section {{
                    margin-bottom: 20px;
                    padding: 15px;
                    background-color: #f9f9f9;
                    border-radius: 4px;
                }}
                pre {{
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-family: monospace;
                }}
                .back-button {{
                    display: inline-block;
                    background-color: #333;
                    color: white;
                    padding: 10px 15px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Generated Blog</h1>

                <div class="section">
                    <h2>Blog Outline</h2>
                    <pre>{blog_outline}</pre>
                </div>

                <div class="section">
                    <h2>Blog Content</h2>
                    <pre>{blog_content}</pre>
                </div>

                <a href="/" class="back-button">Generate Another Blog</a>
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
