import os
import re
import json
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key="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")

class BlogGenerator:
    @classmethod
    def generate_blog_outline(cls, data):
        """
        Generate a comprehensive blog outline with detailed section breakdown
        """
        primary_keywords = data.get('primary_keywords', '')
        secondary_keywords = data.get('secondary_keywords', '')
        intent = data.get('intent', 'informative')
        
        title = data.get('product_title', data.get('blog_title', 'Comprehensive Insight'))
        description = data.get('product_description', data.get('blog_description', ''))
        
        prompt = f"""
        COMPREHENSIVE BLOG OUTLINE GENERATION

        REQUIREMENTS:
        - Create a 5-section blog outline
        - Each section should be 800-1000 words
        - Ensure smooth narrative flow
        - Strategic keyword integration

        CONTEXT:
        - TITLE: {title}
        - PRIMARY KEYWORDS: {primary_keywords}
        - SECONDARY KEYWORDS: {secondary_keywords}
        - INTENT: {intent}

        OUTLINE FORMAT:
        1. Section Title
        2. Key Objectives
        3. Core Narrative Points
        4. Keyword Integration Strategy
        5. Transition Hints to Next Section
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a strategic content architect creating a comprehensive, flowing blog outline."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            # Parse and structure the outline
            raw_outline = response.choices[0].message.content.strip()
            
            # Structure the outline as a JSON for easier processing
            structured_outline = {
                'title': title,
                'primary_keywords': primary_keywords.split(','),
                'secondary_keywords': secondary_keywords.split(','),
                'intent': intent,
                'sections': []
            }
            
            # Basic parsing of sections (you might want to enhance this)
            sections = raw_outline.split('\n\n')
            for section in sections:
                if section.strip():
                    section_parts = section.split('\n')
                    structured_outline['sections'].append({
                        'title': section_parts[0].strip(),
                        'objectives': section_parts[1] if len(section_parts) > 1 else '',
                        'narrative_points': section_parts[2] if len(section_parts) > 2 else '',
                        'keywords_strategy': section_parts[3] if len(section_parts) > 3 else '',
                        'transition_hints': section_parts[4] if len(section_parts) > 4 else ''
                    })
            
            return json.dumps(structured_outline, indent=2)
        
        except Exception as e:
            return f"Outline Generation Error: {str(e)}"

    @classmethod
    def generate_section_content(cls, outline_data, section_index):
        """
        Generate content for a specific section with context awareness
        """
        # Parse the outline
        outline = json.loads(outline_data)
        
        # Get the current section and context
        current_section = outline['sections'][section_index]
        previous_sections = outline['sections'][:section_index]
        next_sections = outline['sections'][section_index+1:]
        
        # Prepare context for section generation
        context_summary = ""
        if previous_sections:
            context_summary += "PREVIOUS SECTIONS CONTEXT:\n"
            for prev_section in previous_sections:
                context_summary += f"- {prev_section['title']}: Key points covered\n"
        
        if next_sections:
            context_summary += "\nUPCOMING SECTIONS PREVIEW:\n"
            for next_section in next_sections:
                context_summary += f"- {next_section['title']}: Anticipated focus\n"
        
        # Prepare section generation prompt
        prompt = f"""
        SECTION CONTENT GENERATION PROTOCOL:

        BLOG CONTEXT:
        - TITLE: {outline['title']}
        - INTENT: {outline['intent']}
        - PRIMARY KEYWORDS: {', '.join(outline['primary_keywords'])}
        - SECONDARY KEYWORDS: {', '.join(outline['secondary_keywords'])}

        CURRENT SECTION DETAILS:
        - TITLE: {current_section['title']}
        - OBJECTIVES: {current_section['objectives']}
        - NARRATIVE POINTS: {current_section['narrative_points']}
        - KEYWORD STRATEGY: {current_section['keywords_strategy']}

        {context_summary}

        SECTION GENERATION REQUIREMENTS:
        1. Word Count: 800-1000 words
        2. Seamlessly continue from previous sections
        3. Provide smooth transition to next section
        4. Strategically integrate keywords
        5. Maintain overall blog intent and narrative flow

        CRITICAL INSTRUCTION:
        - Content must feel like a natural part of the entire narrative
        - Avoid repetition from previous sections
        - Ensure unique value in each section
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a contextually aware content generator creating a seamless, flowing narrative section."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.6
            )
            
            # Extract and process the section content
            section_content = response.choices[0].message.content.strip()
            
            return section_content
        
        except Exception as e:
            return f"Section Generation Error for Section {section_index + 1}: {str(e)}"

    @classmethod
    def generate_complete_blog(cls, data):
        """
        Generate the entire blog by creating sections sequentially
        """
        # Generate the outline first
        outline = cls.generate_blog_outline(data)
        
        # Parse the outline
        outline_data = json.loads(outline)
        
        # Generate each section
        full_blog_content = f"# {outline_data['title']}\n\n"
        
        for i in range(len(outline_data['sections'])):
            # Generate content for each section
            section_content = cls.generate_section_content(json.dumps(outline_data), i)
            
            # Add section title and content
            full_blog_content += f"## {outline_data['sections'][i]['title']}\n\n"
            full_blog_content += section_content + "\n\n"
        
        # Add keyword integration report
        keyword_report = "\n## Keyword Integration Overview\n"
        keyword_report += "### Primary Keywords\n"
        for kw in outline_data['primary_keywords']:
            keyword_report += f"- {kw}: Strategically integrated throughout the content\n"
        
        keyword_report += "\n### Secondary Keywords\n"
        for kw in outline_data['secondary_keywords']:
            keyword_report += f"- {kw}: Contextually woven into the narrative\n"
        
        full_blog_content += keyword_report
        
        return full_blog_content

# Flask Application Configuration
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_fallback_secret_key')

@app.route('/generate', methods=['POST'])
def generate_blog():
    """
    Blog generation endpoint with robust error handling
    """
    # Collect all input data
    data = {k: v.strip() for k, v in request.form.items()}
    
    try:
        # Generate complete blog
        blog_content = BlogGenerator.generate_complete_blog(data)
        
        return jsonify({
            'status': 'success',
            'content': blog_content
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)