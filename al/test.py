from flask import Flask, render_template, request, jsonify
import os
import json
import random
import re
import requests
import time
import nltk
from groq import Groq

from dotenv import load_dotenv
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize
from typing import List, Dict, Any  # Import List, Dict, and Any from typing

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure OpenAI with your API key
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("Missing GROQ_API_KEY environment variable")

client = Groq(api_key=api_key)

# Ensure NLTK resources are downloaded
try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)

def humanize_with_hix(content: str, api_key: str) -> str:
    """
    Humanize content using HIX.AI API

    Args:
        content: The AI-generated content to humanize
        api_key: HIX.AI API key

    Returns:
        Humanized version of the content
    """
    # API Endpoints
    submit_url = "https://bypass.hix.ai/api/hixbypass/v1/submit"
    obtain_url = "https://bypass.hix.ai/api/hixbypass/v1/obtain"

    # API headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Step 1: Submit the task (POST)
    submit_payload = {
        "input": content,
        "mode": "Aggressive"
    }

    print("Submitting content to HIX.AI for humanization...")
    submit_response = requests.post(submit_url, json=submit_payload, headers=headers)
    submit_data = submit_response.json()

    if submit_data.get("err_code") == 0:
        task_id = submit_data["data"]["task_id"]
        print(f"Task submitted. Task ID: {task_id}")

        # Step 2: Polling the result (GET)
        while True:
            params = {"task_id": task_id}
            obtain_response = requests.get(obtain_url, params=params, headers=headers)

            if obtain_response.status_code != 200:
                print(f"Error! Status Code: {obtain_response.status_code}")
                print("Raw response:\n", obtain_response.text)
                return content  # Return original content if error

            try:
                obtain_data = obtain_response.json()
            except requests.exceptions.JSONDecodeError:
                print("Failed to decode JSON. Raw response:")
                print(obtain_response.text)
                return content  # Return original content if error

            if obtain_data.get("err_code") == 0:
                task_status = obtain_data["data"]["subtask_status"]
                if task_status == "completed":
                    humanized_content = obtain_data["data"]["output"]
                    print("Content successfully humanized with HIX.AI")
                    return humanized_content
                else:
                    print("Task still processing, waiting...")
                    time.sleep(3)
            else:
                print("Error obtaining task result:", obtain_data.get("err_msg"))
                return content  # Return original content if error
    else:
        print("Error submitting task:", submit_data.get("err_msg"))
        return content  # Return original content if error

def synonym_replacement(word, pos=None):
    """Find a synonym for a word, considering parts of speech if provided."""
    # Filter synsets by POS if available
    if pos:
        pos_map = {'NN': 'n', 'JJ': 'a', 'VB': 'v', 'RB': 'r'}
        pos_filter = pos_map.get(pos[:2])

        if pos_filter:
            synsets = [s for s in wordnet.synsets(word) if s.pos() == pos_filter]
        else:
            synsets = wordnet.synsets(word)
    else:
        synsets = wordnet.synsets(word)

    # Return original word if no synonyms found
    if not synsets:
        return word

    # Get all lemmas across all synsets
    all_lemmas = []
    for synset in synsets:
        all_lemmas.extend(synset.lemmas())

    # Filter out the original word and duplicates
    filtered_lemmas = [lemma.name() for lemma in all_lemmas if lemma.name().lower() != word.lower()]

    # Return original if no suitable synonyms
    if not filtered_lemmas:
        return word

    # Choose a random synonym
    synonym = random.choice(filtered_lemmas)
    return synonym.replace('_', ' ')

def vary_contractions(text):
    """Randomly convert words to contractions and vice versa."""
    # Dictionary of contractions and their expanded forms
    contractions = {
        'can not': "can't", 'cannot': "can't", 'do not': "don't", 'does not': "doesn't",
        'did not': "didn't", 'is not': "isn't", 'are not': "aren't", 'was not': "wasn't",
        'were not': "weren't", 'has not': "hasn't", 'have not': "haven't", 'had not': "hadn't",
        'will not': "won't", 'would not': "wouldn't", 'should not': "shouldn't",
        'could not': "couldn't", 'I am': "I'm", 'you are': "you're", 'he is': "he's",
        'she is': "she's", 'it is': "it's", 'we are': "we're", 'they are': "they're"
    }

    # Reverse mapping
    expansions = {v: k for k, v in contractions.items()}

    # Find all contractions and expanded forms
    for pattern, replacement in list(contractions.items()) + list(expansions.items()):
        # Only replace with a certain probability
        if random.random() < 0.3:
            # Use word boundary regex to avoid partial matches
            text = re.sub(r'\b' + re.escape(pattern) + r'\b', replacement, text, count=1)

    return text

def introduce_blog_language(text):
    """Add blog-friendly phrases and transitions."""
    blog_transitions = [
        ", interestingly enough,",
        ", surprisingly,",
        ", notably,",
        ", here's the thing,",
        ", the best part is,",
        ", let's be honest,",
        ", I should mention,",
        ", it's worth pointing out that,",
        ", as it turns out,",
        ", this is crucial,"
    ]

    sentences = sent_tokenize(text)
    modified_sentences = []

    for sentence in sentences:
        if len(sentence) > 20 and random.random() < 0.15:
            words = sentence.split()
            if len(words) > 7:
                insert_pos = random.randint(2, min(len(words) - 2, 8))
                transition = random.choice(blog_transitions)
                words.insert(insert_pos, transition)
                sentence = ' '.join(words)

        modified_sentences.append(sentence)

    return ' '.join(modified_sentences)

def add_reader_engagement(text):
    """Add reader engagement elements typical in blog posts."""
    paragraphs = text.split('\n\n')
    modified_paragraphs = []

    engagement_phrases = [
        "Have you experienced something similar?",
        "What do you think about this approach?",
        "If you've tried this before, you know exactly what I'm talking about.",
        "This might seem counterintuitive at first, but bear with me.",
        "You might be wondering if this actually works. Trust me, it does.",
        "Here's where things get really interesting.",
        "Now, I know what you're thinking..."
    ]

    for i, paragraph in enumerate(paragraphs):
        if not paragraph.strip():
            modified_paragraphs.append(paragraph)
            continue

        # Skip headings
        if paragraph.startswith('#'):
            modified_paragraphs.append(paragraph)
            continue

        # Add reader engagement to some paragraphs
        if i > 0 and i < len(paragraphs) - 1 and random.random() < 0.15:
            paragraph += " " + random.choice(engagement_phrases)

        modified_paragraphs.append(paragraph)

    return '\n\n'.join(modified_paragraphs)

def humanize_content(content: str) -> str:
    """
    Transform AI-generated content to sound more natural and human-written,
    using advanced techniques like synonym replacement, sentence restructuring,
    and blog-style elements.

    Args:
        content: The AI-generated content to humanize

    Returns:
        A more natural, human-like version of the content
    """
    # Process the content at multiple levels

    # 1. First, preserve the document structure
    sections = []
    current_section = []
    in_list = False
    list_items = []

    for line in content.split('\n'):
        # Handle blank lines
        if not line.strip():
            # Process any accumulated content
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []

            # Process any list items
            if in_list and list_items:
                sections.append('\n'.join(list_items))
                list_items = []
                in_list = False

            sections.append('')
            continue

        # Preserve headings, code blocks, and formatting elements
        if (line.startswith('#') or line.startswith('```') or
            line.startswith('---') or line.startswith('>')):

            # Process any accumulated content
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []

            # Process any list items
            if in_list and list_items:
                sections.append('\n'.join(list_items))
                list_items = []
                in_list = False

            sections.append(line)
            continue

        # Handle list items
        if line.strip().startswith(('- ', '* ', '1. ', '2. ', '3. ')):
            in_list = True
            list_items.append(line)
            continue

        # Process regular text
        current_section.append(line)

    # Add any remaining content
    if current_section:
        sections.append('\n'.join(current_section))

    if in_list and list_items:
        sections.append('\n'.join(list_items))

    # 2. Process each section appropriately
    processed_sections = []

    for section in sections:
        if not section.strip():
            processed_sections.append(section)
            continue

        # Skip processing for structural elements
        if (section.startswith('#') or section.startswith('```') or
            section.startswith('---') or section.startswith('>')):
            processed_sections.append(section)
            continue

        # Skip processing for list items
        if section.strip().startswith(('- ', '* ', '1. ', '2. ', '3. ')):
            processed_sections.append(section)
            continue

        # Process paragraph content
        sentences = sent_tokenize(section)

        # For content longer than 3 sentences, process each sentence
        if len(sentences) > 3:
            humanized_sentences = []

            for i, sentence in enumerate(sentences):
                # Skip very short sentences
                if len(sentence.split()) < 4:
                    humanized_sentences.append(sentence)
                    continue

                # Tag parts of speech for important words
                if random.random() < 0.3:  # Only process some sentences
                    tokens = nltk.word_tokenize(sentence)
                    tagged = nltk.pos_tag(tokens)

                    modified_tokens = []
                    for word, pos in tagged:
                        # Only replace some content words
                        if (len(word) > 4 and word.isalpha() and
                            pos in ['NN', 'NNS', 'JJ', 'RB', 'VB', 'VBG', 'VBN'] and
                            random.random() < 0.2):
                            modified_tokens.append(synonym_replacement(word, pos))
                        else:
                            modified_tokens.append(word)

                    sentence = ' '.join(modified_tokens)

                # Apply varied contractions
                if random.random() < 0.4:
                    sentence = vary_contractions(sentence)

                humanized_sentences.append(sentence)

            # Join sentences back into paragraph
            humanized_paragraph = ' '.join(humanized_sentences)

            # Add blog-style language
            if random.random() < 0.5:
                humanized_paragraph = introduce_blog_language(humanized_paragraph)

            # Break up very long paragraphs
            if len(humanized_paragraph.split()) > 100:
                words = humanized_paragraph.split()
                midpoint = len(words) // 2

                # Find a sentence end near the midpoint
                sentence_end_indices = []
                current_text = ' '.join(words[:midpoint+20])
                sentences = sent_tokenize(current_text)

                char_count = 0
                for sent in sentences[:-1]:  # Exclude the last sentence which might be cut off
                    char_count += len(sent) + 1  # +1 for the space
                    sentence_end_indices.append(char_count)

                # Find the closest sentence end to our desired midpoint
                if sentence_end_indices:
                    text_midpoint = len(' '.join(words[:midpoint]))
                    closest_index = min(sentence_end_indices, key=lambda x: abs(x - text_midpoint))

                    # Split at this point
                    first_part = ' '.join(words)[:closest_index]
                    second_part = ' '.join(words)[closest_index+1:]  # +1 to skip the space

                    processed_sections.append(first_part)
                    processed_sections.append(second_part)
                else:
                    processed_sections.append(humanized_paragraph)
            else:
                processed_sections.append(humanized_paragraph)
        else:
            # For short sections, apply simple processing
            if random.random() < 0.3:
                section = vary_contractions(section)
            processed_sections.append(section)

    # 3. Reconstruct the document
    humanized_content = '\n\n'.join(processed_sections)

    # 4. Add reader engagement elements
    humanized_content = add_reader_engagement(humanized_content)

    # 5. Clean up any double spaces
    humanized_content = re.sub(r'\s{2,}', ' ', humanized_content)

    return humanized_content

def generate_blog_outline(
    primary_keyword: str,
    intent: str,
    associated_keywords: List[str]
) -> Dict[str, Any]:
    """
    Generate a comprehensive blog post outline using OpenAI API.

    Args:
        primary_keyword: The main keyword for the blog post
        intent: The search intent (informational, transactional, etc.)
        associated_keywords: List of related keywords

    Returns:
        Dictionary containing the generated outline
    """
    # Format the associated keywords list for better prompt readability
    keywords_formatted = "\n".join([f"- {keyword}" for keyword in associated_keywords])

    # Using the exact prompt from the input
    prompt = """Objective: Create a comprehensive and detailed outline for a blog post. This outline should serve as a robust framework for writing an in-depth and informative article.

Instructions:
Understand the Primary Keyword and Intent:
Primary Keyword: This is the central focus of the blog post. It should be the most important keyword from the list and will guide the title and content of the post.
Intent: This defines the purpose or goal of the user's search. It could be informational, investigational, transactional, etc. Understanding the intent helps in tailoring the content to meet the reader's expectations.

Analyze the Keywords:
Review the list of keywords associated with the primary keyword.
Identify subtopics, themes, and specific questions that emerge from these keywords.
Group related keywords to form coherent sections and subsections.

Structure the Outline:
Introduction:
Hook: Start with an engaging hook to grab the reader's attention. This could be a surprising fact, a question, or a compelling statement.
Background: Provide brief background information on the primary keyword.
Purpose: Clearly state the purpose of the blog post.
Preview: Give a preview of what the reader will learn or gain from reading the post.

Main Sections:
Break down the blog post into 3-5 main sections.
Each section should address a specific subtopic or theme identified from the keywords.
Ensure the sections flow logically from one to the next, building a coherent narrative.

Subsections:
Within each main section, include 2-3 subsections.
These subsections should provide more detailed information, examples, case studies, or step-by-step guides related to the main section.
Use bullet points, numbered lists, or tables to present complex information clearly.

Conclusion:
Summary: Summarize the key points discussed in the blog post.
Implications: Discuss the broader implications of the topic.
Call to Action: Provide a clear call to action or next steps for the reader. This could be further reading, trying out a tool, or sharing the post.

Incorporate Keywords Naturally:
Ensure that the keywords are incorporated naturally into the outline.
Avoid keyword stuffing; the focus should be on providing valuable and engaging information.
Use variations of the keywords to enhance readability and SEO.

Primary Keyword: """ + primary_keyword + """
Intent: """ + intent + """
Associated Keywords:
""" + keywords_formatted

    # Generate content with OpenAI
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a professional content strategist and SEO expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )

        # Process the response
        outline_text = response.choices[0].message.content

        # Format the result as a dictionary
        result = {
            "primary_keyword": primary_keyword,
            "intent": intent,
            "associated_keywords": associated_keywords,
            "outline": outline_text
        }

        return result

    except Exception as e:
        print(f"Error generating outline: {e}")
        return {
            "error": str(e),
            "primary_keyword": primary_keyword,
            "intent": intent,
            "associated_keywords": associated_keywords
        }

def generate_blog_content(outline: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate detailed blog content based on the provided outline using OpenAI API.
    Args:
        outline: The outline dictionary containing the primary keyword, intent, associated keywords, and outline text
    Returns:
        Dictionary containing the generated blog content
    """
    # Extract the outline text
    outline_text = outline.get("outline", "")

    # Create a detailed prompt for generating content with a focus on humanization
    prompt = f"""
Objective: Craft a highly engaging, professional, and human-like blog post based on the provided outline. The content should read as though written by a knowledgeable expert with a unique voice and perspective.
Instructions:
- Follow the outline structure closely, but add a conversational tone and personality to the writing.
- Vary sentence structure to avoid monotony and maintain reader interest.
- Address the reader directly and include rhetorical questions.
- Avoid overusing keywords; prioritize readability and flow.
- Maintain a balance between professionalism and approachability.
- Ensure the content feels authentic and avoids generic or overly formal language.
Outline:
{outline_text}
    """
    # Generate content with OpenAI
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a professional content writer with a unique voice and deep expertise in the topic."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.8  # Slightly higher temperature for creativity
        )
        # Process the response
        content_text = response.choices[0].message.content

        # Post-process the content to further humanize it
        content_text = humanize_content(content_text)

        # Format the result as a dictionary
        result = {
            "primary_keyword": outline["primary_keyword"],
            "intent": outline["intent"],
            "associated_keywords": outline["associated_keywords"],
            "content": content_text
        }
        return result
    except Exception as e:
        print(f"Error generating content: {e}")
        return {
            "error": str(e),
            "primary_keyword": outline["primary_keyword"],
            "intent": outline["intent"],
            "associated_keywords": outline["associated_keywords"]
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    page_name = request.form['page_name']
    detailed_prompt = request.form['detailed_prompt']

    # Hardcoded keywords, intent, and primary keyword
    clusters = [ {
            'primary_keyword': page_name,
            'intent': detailed_prompt,
            'keywords': [

]
}]

    # Process clusters
    for cluster in clusters:
        print(f"\nProcessing cluster for primary keyword: {cluster['primary_keyword']}")

        # Generate the outline
        outline = generate_blog_outline(
            cluster['primary_keyword'],
            cluster['intent'],
            cluster['keywords']
        )

        # Generate the content based on the outline
        content = generate_blog_content(outline)

        # Humanize the content using HIX.AI
        hix_api_key = os.environ.get("HIX_API_KEY")
        if hix_api_key:
            print(f"Found HIX_API_KEY in environment variables. Proceeding with content humanization...")
            humanized_content = humanize_with_hix(content['content'], hix_api_key)
        else:
            print("HIX_API_KEY not provided in environment variables. Skipping content humanization.")
            humanized_content = content['content']

        return render_template('result.html', content=humanized_content)

if __name__ == '__main__':
    app.run(debug=True)
