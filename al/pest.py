# import os
# from flask import Flask, render_template_string, request, jsonify
# from openai import OpenAI
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# app = Flask(__name__)

# # Initialize OpenAI Client
# client = OpenAI(api_key="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")

# def generate_blog_outline(product_url, product_title, product_description,
#                            primary_keywords, secondary_keywords, intent):
#     """
#     Generate a detailed blog outline using OpenAI's API
#     """
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
# - Incorporate keywords naturally
# - Focus on solving customer problems
# - Maintain a balanced, objective tone
# - Highlight unique aspects of the product
# - Provide detailed sub-points under each main section to elaborate on the content

# Provide a detailed, structured outline that follows these requirements."""

#     response = client.chat.completions.create(
#         model="gpt-4-turbo",
#         messages=[
#             {"role": "system", "content": "You are an expert content strategist specializing in detailed product blog outlines."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=1000,
#         temperature=0.7
#     )

#     return response.choices[0].message.content

# def generate_blog_content(outline, product_url, product_title, product_description,
#                            primary_keywords, secondary_keywords, intent):
#     """
#     Generate detailed blog content based on the outline, ensuring keywords are included.
#     """
#     prompt = f"""
# You are an expert content writer. Write a detailed and engaging 1200-word blog post using the following outline and product details.

# **Outline:**
# {outline}

# **Product Details:**
# - Product URL: {product_url}
# - Product Title: {product_title}
# - Product Description: {product_description}
# - Primary Keywords: {primary_keywords}
# - Secondary Keywords: {secondary_keywords}
# - Search Intent: {intent}

# **Instructions:**
# - The blog must be approximately 1200 words long.
# - **Include all primary keywords at least 2-3 times each.**
# - **Include all secondary keywords at least once each.**
# - Use primary keywords in the introduction and conclusion.
# - Bold or highlight primary keywords where possible.
# - Write in a professional yet engaging tone.
# - Provide actionable tips and practical examples.
# - Ensure smooth transitions and natural keyword placement.
# - Focus on solving customer pain points.
# - Avoid fluff and make each section valuable.

# At the end of the blog, include a brief bullet point list showing how many times each primary and secondary keyword was used (for verification).
# """

#     response = client.chat.completions.create(
#         model="gpt-4-turbo",
#         messages=[
#             {"role": "system", "content": "You are an expert content writer specializing in SEO and product-focused blog posts."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=1800,
#         temperature=0.7
#     )

#     return response.choices[0].message.content

# # HTML Templates
# INDEX_TEMPLATE = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Product Blog Generator</title>
#     <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
# </head>
# <body class="bg-gray-100 p-8">
#     <div class="container mx-auto max-w-2xl bg-white p-8 rounded-lg shadow-lg">
#         <h1 class="text-3xl font-bold mb-6 text-center">Product Blog Generator</h1>
#         <form method="POST" class="space-y-4">
#             <div>
#                 <label class="block mb-2">Product URL</label>
#                 <input type="text" name="product_url" required class="w-full p-2 border rounded">
#             </div>
#             <div>
#                 <label class="block mb-2">Product Title</label>
#                 <input type="text" name="product_title" required class="w-full p-2 border rounded">
#             </div>
#             <div>
#                 <label class="block mb-2">Product Description</label>
#                 <textarea name="product_description" required class="w-full p-2 border rounded" rows="4"></textarea>
#             </div>
#             <div>
#                 <label class="block mb-2">Primary Keywords</label>
#                 <input type="text" name="primary_keywords" required class="w-full p-2 border rounded">
#             </div>
#             <div>
#                 <label class="block mb-2">Secondary Keywords</label>
#                 <input type="text" name="secondary_keywords" required class="w-full p-2 border rounded">
#             </div>
#             <div>
#                 <label class="block mb-2">Search Intent</label>
#                 <input type="text" name="intent" required class="w-full p-2 border rounded">
#             </div>
#             <button type="submit" class="w-full bg-blue-500 text-white p-3 rounded hover:bg-blue-600">
#                 Generate Blog
#             </button>
#         </form>
#     </div>
# </body>
# </html>
# '''

# RESULT_TEMPLATE = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Blog Generation Result</title>
#     <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
# </head>
# <body class="bg-gray-100 p-8">
#     <div class="container mx-auto max-w-4xl bg-white p-8 rounded-lg shadow-lg">
#         <h1 class="text-3xl font-bold mb-6 text-center">Generated Blog Content</h1>

#         <div class="mb-8">
#             <h2 class="text-2xl font-semibold mb-4">Blog Outline</h2>
#             <pre class="bg-gray-50 p-4 rounded border whitespace-pre-wrap">{{ outline }}</pre>
#         </div>

#         <div>
#             <h2 class="text-2xl font-semibold mb-4">Blog Content</h2>
#             <div class="prose max-w-none">
#                 <pre class="bg-gray-50 p-4 rounded border whitespace-pre-wrap">{{ content }}</pre>
#             </div>
#         </div>

#         <div class="mt-6 text-center">
#             <a href="/" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
#                 Generate Another Blog
#             </a>
#         </div>
#     </div>
# </body>
# </html>
# '''

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Collect form data
#         product_url = request.form.get('product_url')
#         product_title = request.form.get('product_title')
#         product_description = request.form.get('product_description')
#         primary_keywords = request.form.get('primary_keywords')
#         secondary_keywords = request.form.get('secondary_keywords')
#         intent = request.form.get('intent')

#         try:
#             # Generate blog outline
#             blog_outline = generate_blog_outline(
#                 product_url, product_title, product_description,
#                 primary_keywords, secondary_keywords, intent
#             )

#             # Generate blog content
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

# if __name__ == '__main__':
#     app.run(debug=True)


import os
from flask import Flask, render_template_string, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI Client
client = OpenAI(api_key="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")

def generate_blog_outline(product_url, product_title, product_description,
                           primary_keywords, secondary_keywords, intent):
    """
    Generate a detailed blog outline using OpenAI's API
    """
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
- Incorporate keywords naturally
- Focus on solving customer problems
- Maintain a balanced, objective tone
- Highlight unique aspects of the product
- Provide detailed sub-points under each main section to elaborate on the content

Provide a detailed, structured outline that follows these requirements."""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are an expert content strategist specializing in detailed product blog outlines."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.7
    )

    return response.choices[0].message.content

def generate_blog_content(outline, product_url, product_title, product_description,
                           primary_keywords, secondary_keywords, intent):
    """
    Generate detailed blog content section by section, ensuring a consistent flow and no repetition.
    """
    sections = outline.split('\n\n')  # Assuming sections are separated by double newlines
    blog_content = []
    used_keywords = set()

    for i, section in enumerate(sections):
        previous_text = ' '.join(blog_content) if i > 0 else 'None'
        
        # Extract unique keywords to avoid repetition
        new_keywords = set(primary_keywords.split(", ") + secondary_keywords.split(", "))
        unique_keywords = ', '.join(new_keywords - used_keywords)
        used_keywords.update(new_keywords)

        section_prompt = f"""Generate a detailed section for a blog post while ensuring no repetition.
        
Section Outline:
{section}

Product Details:
- Product URL: {product_url}
- Product Title: {product_title}
- Product Description: {product_description}
- Unique Keywords to Use: {unique_keywords}
- Search Intent: {intent}

Guidelines:
- Word count for this section: Approximately {1200 // len(sections)} words
- Avoid repeating points from previous sections
- Focus on new insights, examples, and fresh perspectives
- Ensure smooth transitions from previous sections
- Maintain a professional and engaging tone

Previous Sections Summary:
{previous_text}

Generate the content for this section."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert content writer specializing in product-focused blog posts."},
                {"role": "user", "content": section_prompt}
            ],
            max_tokens=500,  # Increased to ensure enough detail per section
            temperature=0.7
        )

        section_content = response.choices[0].message.content
        blog_content.append(section_content)

    # Combine all sections into a single blog post
    full_blog_content = '\n\n'.join(blog_content)
    return full_blog_content

# HTML Templates
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Product Blog Generator</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 p-8">
    <div class="container mx-auto max-w-2xl bg-white p-8 rounded-lg shadow-lg">
        <h1 class="text-3xl font-bold mb-6 text-center">Product Blog Generator</h1>
        <form method="POST" class="space-y-4">
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
</head>
<body class="bg-gray-100 p-8">
    <div class="container mx-auto max-w-4xl bg-white p-8 rounded-lg shadow-lg">
        <h1 class="text-3xl font-bold mb-6 text-center">Generated Blog Content</h1>

        <div class="mb-8">
            <h2 class="text-2xl font-semibold mb-4">Blog Outline</h2>
            <pre class="bg-gray-50 p-4 rounded border whitespace-pre-wrap">{{ outline }}</pre>
        </div>

        <div>
            <h2 class="text-2xl font-semibold mb-4">Blog Content</h2>
            <div class="prose max-w-none">
                <pre class="bg-gray-50 p-4 rounded border whitespace-pre-wrap">{{ content }}</pre>
            </div>
        </div>

        <div class="mt-6 text-center">
            <a href="/" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                Generate Another Blog
            </a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect form data
        product_url = request.form.get('product_url')
        product_title = request.form.get('product_title')
        product_description = request.form.get('product_description')
        primary_keywords = request.form.get('primary_keywords')
        secondary_keywords = request.form.get('secondary_keywords')
        intent = request.form.get('intent')

        try:
            # Generate blog outline
            blog_outline = generate_blog_outline(
                product_url, product_title, product_description,
                primary_keywords, secondary_keywords, intent
            )

            # Generate blog content
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

if __name__ == '__main__':
    app.run(debug=True)
