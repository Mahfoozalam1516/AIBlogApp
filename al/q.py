import os
import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

# Configure Gemini
genai.configure(api_key="AIzaSyBcCvjXMWDDXF1-Wms-z6dhZekX54PZhKA")  # Or paste your key directly for testing

gemini_model = genai.GenerativeModel("gemini-2.0-flash")

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
    response = gemini_model.generate_content(prompt)
    return response.text

def generate_blog_content(outline, product_url, product_title, product_description,
                          primary_keywords, secondary_keywords, intent):
    sections = outline.split('\n\n')
    blog_content = []
    all_keywords = primary_keywords.split(", ") + secondary_keywords.split(", ")
    keyword_usage = {keyword: 0 for keyword in all_keywords}
    primary_keyword_target = 5  # Target usage for primary keywords
    secondary_keyword_target = 1  # Target usage for secondary keywords

    for i, section in enumerate(sections):
        previous_text = ' '.join(blog_content) if i > 0 else 'None'

        primary_keywords_instruction = (
            "\n- Use each of the following primary keywords approximately **1 time** throughout this section: "
            + ', '.join(primary_keywords.split(", ")) +
            ". Make the usage natural and contextually relevant."
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

        response = gemini_model.generate_content(section_prompt)
        section_content = response.text

        # Update keyword usage count
        for keyword in all_keywords:
            keyword_usage[keyword] += section_content.lower().count(keyword.lower())

        blog_content.append(section_content)

    # Ensure primary keywords are used 4-5 times and secondary keywords are used once
    for keyword, count in keyword_usage.items():
        if keyword in primary_keywords.split(", ") and count < primary_keyword_target:
            additional_content = f"Additionally, {keyword} plays a crucial role in enhancing the overall experience."
            blog_content.append(additional_content)
            keyword_usage[keyword] += 1
        elif keyword in secondary_keywords.split(", ") and count < secondary_keyword_target:
            additional_content = f"Moreover, {keyword} is an important aspect to consider."
            blog_content.append(additional_content)
            keyword_usage[keyword] += 1

    return '\n\n'.join(blog_content)

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
    response = gemini_model.generate_content(outline_prompt)
    return response.text

def generate_general_blog_content(outline, keywords, primary_keywords, prompt):
    sections = outline.split('\n\n')
    blog_content = []
    all_keywords = primary_keywords.split(", ") + keywords.split(", ")
    keyword_usage = {keyword: 0 for keyword in all_keywords}
    primary_keyword_target = 5  # Target usage for primary keywords
    secondary_keyword_target = 1  # Target usage for secondary keywords

    for i, section in enumerate(sections):
        previous_text = ' '.join(blog_content) if i > 0 else 'None'

        primary_keywords_instruction = (
            "\n- Use each of the following primary keywords approximately **1 time** throughout this section: "
            + ', '.join(primary_keywords.split(", ")) +
            ". Make the usage natural and contextually relevant."
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

        response = gemini_model.generate_content(section_prompt)
        section_content = response.text

        # Update keyword usage count
        for keyword in all_keywords:
            keyword_usage[keyword] += section_content.lower().count(keyword.lower())

        blog_content.append(section_content)

    # Ensure primary keywords are used 4-5 times and secondary keywords are used once
    for keyword, count in keyword_usage.items():
        if keyword in primary_keywords.split(", ") and count < primary_keyword_target:
            additional_content = f"Additionally, {keyword} plays a crucial role in enhancing the overall experience."
            blog_content.append(additional_content)
            keyword_usage[keyword] += 1
        elif keyword in keywords.split(", ") and count < secondary_keyword_target:
            additional_content = f"Moreover, {keyword} is an important aspect to consider."
            blog_content.append(additional_content)
            keyword_usage[keyword] += 1

    return '\n\n'.join(blog_content)

def humanize_content(content):
    humanize_prompt = f"""Humanize the following blog content to make it sound more natural, conversational, and engaging:

{content}

Guidelines for Humanization:
1. Use a more conversational tone
2. Add personal anecdotes or relatable examples
3. Break up complex sentences
4. Use more active voice
5. Add rhetorical questions or engaging transitions
6. Inject personality and warmth
7. Ensure the core message and key points remain intact"""

    response = gemini_model.generate_content(humanize_prompt)
    return response.text

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
<body class="bg-gray-100 p-8">
    <div class="container mx-auto max-w-4xl">
        <h1 class="text-4xl font-bold mb-8 text-center">Blog Generator Dashboard</h1>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
            <div onclick="showForm('product')" class="cursor-pointer p-6 bg-white rounded-lg shadow hover:shadow-lg transition">
                <h2 class="text-2xl font-semibold mb-2">Product-Specific Blog</h2>
                <p class="text-gray-600">Generate a blog tailored to a specific product using keywords and descriptions.</p>
            </div>
            <div onclick="showForm('general')" class="cursor-pointer p-6 bg-white rounded-lg shadow hover:shadow-lg transition">
                <h2 class="text-2xl font-semibold mb-2">General Blog</h2>
                <p class="text-gray-600">Create general blogs for topics or industries.</p>
            </div>
        </div>

        <div id="product-form-container" style="display:none;" class="bg-white p-8 rounded-lg shadow-lg">
            <h2 class="text-2xl font-bold mb-6 text-center">Generate Product Blog</h2>
            <form method="POST" action="/" class="space-y-4">
                <div>
                    <label class="block mb-2">Product URL</label>
                    <input type="text" name="product_url" required class="w-full p-2 border rounded">
                </div>
                <div>
                    <label class="block mb-2">Product Title</label>
                    <input type="text" name="product_title" required class="w-full p-2 border rounded">
                </div>
                <div>
                    <label class="block mb-2">Product Description</label>
                    <textarea name="product_description" required class="w-full p-2 border rounded" rows="4"></textarea>
                </div>
                <div>
                    <label class="block mb-2">Primary Keywords</label>
                    <input type="text" name="primary_keywords" required class="w-full p-2 border rounded">
                </div>
                <div>
                    <label class="block mb-2">Secondary Keywords</label>
                    <input type="text" name="secondary_keywords" required class="w-full p-2 border rounded">
                </div>
                <div>
                    <label class="block mb-2">Search Intent</label>
                    <input type="text" name="intent" required class="w-full p-2 border rounded">
                </div>
                <button type="submit" class="w-full bg-blue-500 text-white p-3 rounded hover:bg-blue-600">
                    Generate Blog
                </button>
            </form>
        </div>

        <div id="general-form-container" style="display:none;" class="bg-white p-8 rounded-lg shadow-lg">
            <h2 class="text-2xl font-bold mb-6 text-center">Generate General Blog</h2>
            <form method="POST" action="/general" class="space-y-4">
                <div>
                    <label class="block mb-2">Keywords</label>
                    <input type="text" name="keywords" required class="w-full p-2 border rounded">
                </div>
                <div>
                    <label class="block mb-2">Primary Keywords</label>
                    <input type="text" name="primary_keywords" required class="w-full p-2 border rounded">
                </div>
                <div>
                    <label class="block mb-2">Prompt</label>
                    <textarea name="prompt" required class="w-full p-2 border rounded" rows="4"></textarea>
                </div>
                <button type="submit" class="w-full bg-blue-500 text-white p-3 rounded hover:bg-blue-600">
                    Generate Blog
                </button>
            </form>
        </div>
    </div>
</body>
</html>
'''

RESULT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Blog Generation Result</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script>
        function copyToClipboard() {
            const content = document.getElementById('blog-content');
            navigator.clipboard.writeText(content.value).then(() => {
                alert('Content copied to clipboard!');
            });
        }
    </script>
</head>
<body class="bg-gray-100 p-8">
    <div class="container mx-auto max-w-4xl bg-white p-8 rounded-lg shadow-lg">
        <h1 class="text-3xl font-bold mb-6 text-center">Generated Blog Content</h1>

        <form method="POST" action="/humanize" id="content-form">
            <div class="mb-8">
                <h2 class="text-2xl font-semibold mb-4">Blog Outline</h2>
                <pre class="bg-gray-50 p-4 rounded border whitespace-pre-wrap">{{ outline }}</pre>
            </div>

            <div>
                <h2 class="text-2xl font-semibold mb-4">Blog Content</h2>
                <textarea id="blog-content" name="content" class="w-full bg-gray-50 p-4 rounded border min-h-[500px]">{{ content }}</textarea>
            </div>

            <div class="mt-6 flex justify-between">
                <div>
                    <a href="/" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mr-4">
                        Generate Another Blog
                    </a>
                    <button type="button" onclick="copyToClipboard()" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 mr-4">
                        Copy Content
                    </button>
                </div>
                <button type="submit" class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
                    Humanize Content
                </button>
            </div>
        </form>
    </div>
</body>
</html>
'''

HUMANIZED_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Humanized Blog Content</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script>
        function copyToClipboard() {
            const content = document.getElementById('humanized-content');
            navigator.clipboard.writeText(content.value).then(() => {
                alert('Content copied to clipboard!');
            });
        }
    </script>
</head>
<body class="bg-gray-100 p-8">
    <div class="container mx-auto max-w-4xl bg-white p-8 rounded-lg shadow-lg">
        <h1 class="text-3xl font-bold mb-6 text-center">Humanized Blog Content</h1>

        <form>
            <div>
                <h2 class="text-2xl font-semibold mb-4">Humanized Content</h2>
                <textarea id="humanized-content" class="w-full bg-gray-50 p-4 rounded border min-h-[500px]" readonly>{{ humanized_content }}</textarea>
            </div>

            <div class="mt-6 flex justify-between">
                <a href="/" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 mr-4">
                    Generate Another Blog
                </a>
                <button type="button" onclick="copyToClipboard()" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                    Copy Humanized Content
                </button>
            </div>
        </form>
    </div>
</body>
</html>
'''

# Routes
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

@app.route('/humanize', methods=['POST'])
def humanize():
    content = request.form.get('content')
    
    try:
        humanized_content = humanize_content(content)
        
        return render_template_string(HUMANIZED_TEMPLATE, 
                                      humanized_content=humanized_content)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)