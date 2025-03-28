# import os
# import google.generativeai as genai
# from flask import Flask, render_template_string, request, jsonify
# from dotenv import load_dotenv

# # Load .env variables
# load_dotenv()

# # Initialize Flask
# app = Flask(__name__)

# # Configure Gemini
# genai.configure(api_key="AIzaSyBQi4LrGW9pFirEiTnFw3RONXz39nUpghQ")
# gemini_model = genai.GenerativeModel("gemini-2.0-flash")


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
# - Incorporate keywords naturally
# - Focus on solving customer problems
# - Maintain a balanced, objective tone
# - Highlight unique aspects of the product
# - Provide detailed sub-points under each main section to elaborate on the content
# """

#     response = gemini_model.generate_content(prompt)
#     return response.text


# def generate_blog_content(outline, product_url, product_title, product_description,
#                           primary_keywords, secondary_keywords, intent):
#     sections = outline.split('\n\n')
#     blog_content = []
#     used_keywords = set()

#     for i, section in enumerate(sections):
#         previous_text = ' '.join(blog_content) if i > 0 else 'None'
#         new_keywords = set(primary_keywords.split(", ") + secondary_keywords.split(", "))
#         unique_keywords = ', '.join(new_keywords - used_keywords)
#         used_keywords.update(new_keywords)

#         section_prompt = f"""Generate a detailed section for a blog post while ensuring no repetition.

# Section Outline:
# {section}

# Product Details:
# - Product URL: {product_url}
# - Product Title: {product_title}
# - Product Description: {product_description}
# - Unique Keywords to Use: {unique_keywords}
# - Search Intent: {intent}

# Guidelines:
# - Word count for this section: Approximately {1200 // len(sections)} words
# - Avoid repeating points from previous sections
# - Focus on new insights, examples, and fresh perspectives
# - Ensure smooth transitions from previous sections
# - Maintain a professional and engaging tone

# Previous Sections Summary:
# {previous_text}

# Generate the content for this section."""

#         response = gemini_model.generate_content(section_prompt)
#         blog_content.append(response.text)

#     return '\n\n'.join(blog_content)


# INDEX_TEMPLATE = '''
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Blog Generator Dashboard</title>
#     <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
#     <script>
#         function showForm(type) {
#             if (type === 'product') {
#                 document.getElementById('form-container').style.display = 'block';
#             } else {
#                 alert('General blog feature coming soon!');
#             }
#         }
#     </script>
# </head>
# <body class="bg-gray-100 p-8">
#     <div class="container mx-auto max-w-4xl">
#         <h1 class="text-4xl font-bold mb-8 text-center">Blog Generator Dashboard</h1>

#         <!-- Dashboard Cards -->
#         <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
#             <div onclick="showForm('product')" class="cursor-pointer p-6 bg-white rounded-lg shadow hover:shadow-lg transition">
#                 <h2 class="text-2xl font-semibold mb-2">Product-Specific Blog</h2>
#                 <p class="text-gray-600">Generate a blog tailored to a specific product using keywords and descriptions.</p>
#             </div>
#             <div onclick="showForm('general')" class="cursor-pointer p-6 bg-white rounded-lg shadow hover:shadow-lg transition">
#                 <h2 class="text-2xl font-semibold mb-2">General Blog</h2>
#                 <p class="text-gray-600">Coming Soon: Create general blogs for topics or industries.</p>
#             </div>
#         </div>

#         <!-- Product-Specific Blog Form -->
#         <div id="form-container" style="display:none;" class="bg-white p-8 rounded-lg shadow-lg">
#             <h2 class="text-2xl font-bold mb-6 text-center">Generate Product Blog</h2>
#             <form method="POST" class="space-y-4">
#                 <div>
#                     <label class="block mb-2">Product URL</label>
#                     <input type="text" name="product_url" required class="w-full p-2 border rounded">
#                 </div>
#                 <div>
#                     <label class="block mb-2">Product Title</label>
#                     <input type="text" name="product_title" required class="w-full p-2 border rounded">
#                 </div>
#                 <div>
#                     <label class="block mb-2">Product Description</label>
#                     <textarea name="product_description" required class="w-full p-2 border rounded" rows="4"></textarea>
#                 </div>
#                 <div>
#                     <label class="block mb-2">Primary Keywords</label>
#                     <input type="text" name="primary_keywords" required class="w-full p-2 border rounded">
#                 </div>
#                 <div>
#                     <label class="block mb-2">Secondary Keywords</label>
#                     <input type="text" name="secondary_keywords" required class="w-full p-2 border rounded">
#                 </div>
#                 <div>
#                     <label class="block mb-2">Search Intent</label>
#                     <input type="text" name="intent" required class="w-full p-2 border rounded">
#                 </div>
#                 <button type="submit" class="w-full bg-blue-500 text-white p-3 rounded hover:bg-blue-600">
#                     Generate Blog
#                 </button>
#             </form>
#         </div>
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


# if __name__ == '__main__':
#     app.run(debug=True)
import os
import google.generativeai as genai
from flask import Flask, render_template_string, request, jsonify
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

# Configure Gemini
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai.configure(api_key="AIzaSyBQi4LrGW9pFirEiTnFw3RONXz39nUpghQ")

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

    for i, section in enumerate(sections):
        previous_text = ' '.join(blog_content) if i > 0 else 'None'

        keyword_usage_instruction = "\n- Use the following keywords repeatedly and naturally throughout this section: " + ', '.join(all_keywords)

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
- Maintain a professional and engaging tone{keyword_usage_instruction}

Previous Sections Summary:
{previous_text}

Generate the content for this section."""

        response = gemini_model.generate_content(section_prompt)
        blog_content.append(response.text)

    return '\n\n'.join(blog_content)


INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Blog Generator Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <script>
        function showForm(type) {
            if (type === 'product') {
                document.getElementById('form-container').style.display = 'block';
            } else {
                alert('General blog feature coming soon!');
            }
        }
    </script>
</head>
<body class="bg-gray-100 p-8">
    <div class="container mx-auto max-w-4xl">
        <h1 class="text-4xl font-bold mb-8 text-center">Blog Generator Dashboard</h1>

        <!-- Dashboard Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
            <div onclick="showForm('product')" class="cursor-pointer p-6 bg-white rounded-lg shadow hover:shadow-lg transition">
                <h2 class="text-2xl font-semibold mb-2">Product-Specific Blog</h2>
                <p class="text-gray-600">Generate a blog tailored to a specific product using keywords and descriptions.</p>
            </div>
            <div onclick="showForm('general')" class="cursor-pointer p-6 bg-white rounded-lg shadow hover:shadow-lg transition">
                <h2 class="text-2xl font-semibold mb-2">General Blog</h2>
                <p class="text-gray-600">Coming Soon: Create general blogs for topics or industries.</p>
            </div>
        </div>

        <!-- Product-Specific Blog Form -->
        <div id="form-container" style="display:none;" class="bg-white p-8 rounded-lg shadow-lg">
            <h2 class="text-2xl font-bold mb-6 text-center">Generate Product Blog</h2>
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


if __name__ == '__main__':
    app.run(debug=True)
