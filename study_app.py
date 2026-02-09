import streamlit as st
import json
from openai import OpenAI
from datetime import datetime, timedelta
import re
import PyPDF2
import io

# Page configuration
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'document_content' not in st.session_state:
    st.session_state.document_content = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = {}
if 'study_progress' not in st.session_state:
    st.session_state.study_progress = {}

def get_ai_response(prompt, model="arcee-ai/trinity-large-preview:free"):
    """Get response from OpenRouter API"""
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.session_state.api_key,
        )
        
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            extra_body={}
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error communicating with API: {str(e)}")
        return None

# Sidebar for API Key and Document Upload
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key Input
    api_key_input = st.text_input(
        "OpenRouter API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your API key from https://openrouter.ai/"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("API Key saved!")
    
    st.divider()
    
    # Document Upload
    st.header("📄 Document Upload")
    
    upload_method = st.radio("Choose upload method:", ["Paste Text", "Upload File"])
    
    if upload_method == "Paste Text":
        document_text = st.text_area(
            "Paste your study material here:",
            height=200,
            value=st.session_state.document_content
        )
        if st.button("Load Document"):
            st.session_state.document_content = document_text
            st.success("Document loaded successfully!")
    else:
        uploaded_file = st.file_uploader("Upload a file", type=['txt', 'md', 'pdf'])
        if uploaded_file is not None:
            try:
                if uploaded_file.type == "application/pdf":
                    # Extract text from PDF
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                    document_text = ""
                    for page_num, page in enumerate(pdf_reader.pages):
                        text = page.extract_text()
                        if text:
                            document_text += text + "\n"
                    
                    if document_text.strip():
                        st.session_state.document_content = document_text
                        st.success(f"PDF uploaded successfully! ({len(pdf_reader.pages)} pages)")
                    else:
                        st.error("Could not extract text from PDF. The PDF might be image-based or protected.")
                else:
                    # Handle text files
                    document_text = uploaded_file.read().decode('utf-8')
                    st.session_state.document_content = document_text
                    st.success("File uploaded successfully!")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    if st.session_state.document_content:
        word_count = len(st.session_state.document_content.split())
        st.info(f"📊 Document loaded: {word_count} words")

# Main App
st.title("📚 AI Study Assistant")
st.markdown("*Your comprehensive AI-powered learning companion*")

if not st.session_state.api_key:
    st.warning("⚠️ Please enter your OpenRouter API key in the sidebar to get started.")
    st.stop()

if not st.session_state.document_content:
    st.info("👈 Please upload or paste your study material in the sidebar.")
    st.stop()

# Create tabs for different features
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📝 Document Analysis",
    "❓ Question Generator",
    "📋 Cheat Sheet",
    "💬 Q&A Chat",
    "🎯 Practice Tests",
    "🧠 Memory Aids",
    "📊 Study Planner"
])

# TAB 1: Document Analysis
with tab1:
    st.header("Document Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📖 Summarization")
        summary_depth = st.select_slider(
            "Summary depth:",
            options=["Brief", "Detailed", "Comprehensive"]
        )
        
        if st.button("Generate Summary", key="summary_btn"):
            with st.spinner("Analyzing document..."):
                prompt = f"""Provide a {summary_depth.lower()} summary of the following text. 
                
For Brief: 2-3 sentences covering main points
For Detailed: 1-2 paragraphs with key concepts
For Comprehensive: Multiple paragraphs with in-depth analysis

Text: {st.session_state.document_content}"""
                
                summary = get_ai_response(prompt)
                if summary:
                    st.session_state.generated_content['summary'] = summary
                    st.success("Summary generated!")
        
        if 'summary' in st.session_state.generated_content:
            st.markdown("### Summary")
            st.write(st.session_state.generated_content['summary'])
            st.download_button(
                "Download Summary",
                st.session_state.generated_content['summary'],
                file_name="summary.txt"
            )
    
    with col2:
        st.subheader("🔑 Key Concepts")
        
        if st.button("Extract Key Concepts", key="concepts_btn"):
            with st.spinner("Extracting key concepts..."):
                prompt = f"""Extract and define the key concepts from this text. 
Format as:
**Concept Name**: Definition

Text: {st.session_state.document_content}"""
                
                concepts = get_ai_response(prompt)
                if concepts:
                    st.session_state.generated_content['concepts'] = concepts
                    st.success("Concepts extracted!")
        
        if 'concepts' in st.session_state.generated_content:
            st.markdown("### Key Concepts")
            st.write(st.session_state.generated_content['concepts'])
            st.download_button(
                "Download Concepts",
                st.session_state.generated_content['concepts'],
                file_name="key_concepts.txt"
            )
    
    st.divider()
    
    # Difficulty Assessment
    st.subheader("📊 Difficulty Assessment")
    if st.button("Assess Difficulty", key="difficulty_btn"):
        with st.spinner("Assessing difficulty..."):
            prompt = f"""Analyze the difficulty level of this text for a student. Rate it on:
1. Reading Level (Elementary/Middle School/High School/College/Graduate)
2. Concept Complexity (Low/Medium/High)
3. Prior Knowledge Required
4. Estimated Study Time

Text: {st.session_state.document_content}"""
            
            difficulty = get_ai_response(prompt)
            if difficulty:
                st.session_state.generated_content['difficulty'] = difficulty
                st.success("Assessment complete!")
    
    if 'difficulty' in st.session_state.generated_content:
        st.info(st.session_state.generated_content['difficulty'])

# TAB 2: Question Generator
with tab2:
    st.header("Question Generator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_questions = st.slider("Number of questions:", 5, 50, 10)
    with col2:
        difficulty = st.select_slider(
            "Difficulty:",
            options=["Easy", "Medium", "Hard", "Mixed"]
        )
    with col3:
        question_type = st.selectbox(
            "Question type:",
            ["Multiple Choice", "True/False", "Short Answer", "Fill in the Blank", "Mixed"]
        )
    
    if st.button("Generate Questions", key="gen_questions"):
        with st.spinner(f"Generating {num_questions} {question_type} questions..."):
            prompt = f"""Generate {num_questions} {question_type} questions from this text.
Difficulty level: {difficulty}

Format each question clearly with:
- Question number
- The question
- Options (if applicable)
- Correct answer
- Brief explanation

Text: {st.session_state.document_content}"""
            
            questions = get_ai_response(prompt)
            if questions:
                st.session_state.generated_content['questions'] = questions
                st.success("Questions generated!")
    
    if 'questions' in st.session_state.generated_content:
        st.markdown("### Generated Questions")
        st.write(st.session_state.generated_content['questions'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download Questions (TXT)",
                st.session_state.generated_content['questions'],
                file_name="study_questions.txt"
            )
        with col2:
            # Format for Anki
            st.download_button(
                "Download for Anki (TXT)",
                st.session_state.generated_content['questions'],
                file_name="anki_cards.txt",
                help="Import this file into Anki"
            )

# TAB 3: Cheat Sheet Generator
with tab3:
    st.header("Cheat Sheet Generator")
    
    cheat_sheet_format = st.selectbox(
        "Choose format:",
        ["One-Page Summary", "Flashcard Style", "Formula Sheet", "Timeline", "Comparison Table"]
    )
    
    if st.button("Generate Cheat Sheet", key="cheat_sheet_btn"):
        with st.spinner("Creating cheat sheet..."):
            prompts = {
                "One-Page Summary": f"Create a concise one-page cheat sheet with the most important information from this text. Use bullet points and clear sections.\n\nText: {st.session_state.document_content}",
                "Flashcard Style": f"Create flashcard-style content with questions on one side and answers on the other. Format as 'Q: [question]\nA: [answer]'\n\nText: {st.session_state.document_content}",
                "Formula Sheet": f"Extract all formulas, equations, and important calculations. Explain when to use each.\n\nText: {st.session_state.document_content}",
                "Timeline": f"Create a chronological timeline of events, developments, or processes mentioned in this text.\n\nText: {st.session_state.document_content}",
                "Comparison Table": f"Create a comparison table showing similarities and differences between key concepts.\n\nText: {st.session_state.document_content}"
            }
            
            cheat_sheet = get_ai_response(prompts[cheat_sheet_format])
            if cheat_sheet:
                st.session_state.generated_content['cheat_sheet'] = cheat_sheet
                st.success("Cheat sheet created!")
    
    if 'cheat_sheet' in st.session_state.generated_content:
        st.markdown("### Your Cheat Sheet")
        st.write(st.session_state.generated_content['cheat_sheet'])
        st.download_button(
            "Download Cheat Sheet",
            st.session_state.generated_content['cheat_sheet'],
            file_name=f"cheat_sheet_{cheat_sheet_format.lower().replace(' ', '_')}.txt"
        )

# TAB 4: Interactive Q&A Chat
with tab4:
    st.header("Interactive Q&A Chat")
    st.markdown("*Ask questions about your document and get instant answers*")
    
    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])
    
    # Chat input
    user_question = st.chat_input("Ask a question about the document...")
    
    if user_question:
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        with st.chat_message("user"):
            st.write(user_question)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                prompt = f"""Based on the following document, answer this question: {user_question}

If the question cannot be answered from the document, say so and provide general knowledge if helpful.

Document: {st.session_state.document_content}"""
                
                response = get_ai_response(prompt)
                if response:
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# TAB 5: Practice Tests
with tab5:
    st.header("Practice Tests")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_length = st.slider("Number of questions:", 10, 100, 25)
        time_limit = st.slider("Time limit (minutes):", 10, 120, 30)
    
    with col2:
        test_difficulty = st.select_slider(
            "Test difficulty:",
            options=["Easy", "Medium", "Hard", "Mixed"]
        )
    
    if st.button("Generate Practice Test", key="practice_test"):
        with st.spinner("Creating your practice test..."):
            prompt = f"""Create a practice test with {test_length} questions from this material.
Difficulty: {test_difficulty}
Mix question types: multiple choice, true/false, and short answer.
Include an answer key at the end.

Text: {st.session_state.document_content}"""
            
            practice_test = get_ai_response(prompt)
            if practice_test:
                st.session_state.generated_content['practice_test'] = practice_test
                st.success(f"Practice test ready! Time limit: {time_limit} minutes")
    
    if 'practice_test' in st.session_state.generated_content:
        st.info(f"⏱️ Time limit: {time_limit} minutes - Track your time!")
        st.markdown("### Practice Test")
        st.write(st.session_state.generated_content['practice_test'])
        st.download_button(
            "Download Test",
            st.session_state.generated_content['practice_test'],
            file_name="practice_test.txt"
        )

# TAB 6: Memory Aids
with tab6:
    st.header("Memory Aids & Learning Tools")
    
    memory_tool = st.selectbox(
        "Choose a memory aid:",
        ["Mnemonics", "Analogies", "Visual Associations", "Acronyms", "Story Method"]
    )
    
    if st.button("Generate Memory Aid", key="memory_aid"):
        with st.spinner(f"Creating {memory_tool.lower()}..."):
            prompts = {
                "Mnemonics": f"Create memorable mnemonics for the key concepts in this text. Explain each mnemonic.\n\nText: {st.session_state.document_content}",
                "Analogies": f"Create helpful analogies to explain difficult concepts in this text by relating them to everyday experiences.\n\nText: {st.session_state.document_content}",
                "Visual Associations": f"Suggest visual associations and mental images to help remember key information from this text.\n\nText: {st.session_state.document_content}",
                "Acronyms": f"Create acronyms to help remember lists and key points from this text.\n\nText: {st.session_state.document_content}",
                "Story Method": f"Create a memorable story that incorporates the key concepts from this text.\n\nText: {st.session_state.document_content}"
            }
            
            memory_aid = get_ai_response(prompts[memory_tool])
            if memory_aid:
                st.session_state.generated_content['memory_aid'] = memory_aid
                st.success(f"{memory_tool} created!")
    
    if 'memory_aid' in st.session_state.generated_content:
        st.markdown(f"### {memory_tool}")
        st.write(st.session_state.generated_content['memory_aid'])
        st.download_button(
            "Download Memory Aid",
            st.session_state.generated_content['memory_aid'],
            file_name=f"memory_aid_{memory_tool.lower().replace(' ', '_')}.txt"
        )
    
    st.divider()
    
    # Feynman Technique Prompts
    st.subheader("🎓 Feynman Technique")
    st.markdown("*Explain concepts in your own words to test understanding*")
    
    if st.button("Get Feynman Prompts", key="feynman"):
        with st.spinner("Generating prompts..."):
            prompt = f"""Using the Feynman Technique, create 5 prompts that ask the student to explain key concepts from this text in simple terms, as if teaching a child.

Text: {st.session_state.document_content}"""
            
            feynman = get_ai_response(prompt)
            if feynman:
                st.session_state.generated_content['feynman'] = feynman
                st.success("Prompts ready!")
    
    if 'feynman' in st.session_state.generated_content:
        st.info(st.session_state.generated_content['feynman'])

# TAB 7: Study Planner
with tab7:
    st.header("Study Planner")
    
    col1, col2 = st.columns(2)
    
    with col1:
        exam_date = st.date_input(
            "Exam/Deadline date:",
            min_value=datetime.now().date(),
            value=datetime.now().date() + timedelta(days=14)
        )
    
    with col2:
        study_hours_per_day = st.slider("Study hours per day:", 1, 8, 2)
    
    if st.button("Generate Study Plan", key="study_plan"):
        days_until_exam = (exam_date - datetime.now().date()).days
        
        with st.spinner("Creating your personalized study plan..."):
            prompt = f"""Create a detailed study plan for this material with the following constraints:
- Days until exam: {days_until_exam}
- Study hours per day: {study_hours_per_day}
- Total study hours available: {days_until_exam * study_hours_per_day}

Include:
1. Daily breakdown of topics to cover
2. Recommended study techniques for each section
3. Review sessions
4. Practice test schedule
5. Rest days

Text to study: {st.session_state.document_content}"""
            
            study_plan = get_ai_response(prompt)
            if study_plan:
                st.session_state.generated_content['study_plan'] = study_plan
                st.success("Study plan created!")
    
    if 'study_plan' in st.session_state.generated_content:
        st.markdown("### Your Personalized Study Plan")
        st.write(st.session_state.generated_content['study_plan'])
        st.download_button(
            "Download Study Plan",
            st.session_state.generated_content['study_plan'],
            file_name="study_plan.txt"
        )
    
    st.divider()
    
    # Progress Tracking
    st.subheader("📈 Progress Tracker")
    st.markdown("*Track which topics you've mastered*")
    
    topic_status = st.text_input("Enter topic name to mark as completed:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Mark as Studying"):
            st.session_state.study_progress[topic_status] = "Studying"
            st.success(f"'{topic_status}' marked as Studying")
    
    with col2:
        if st.button("Mark as Review"):
            st.session_state.study_progress[topic_status] = "Review"
            st.success(f"'{topic_status}' needs review")
    
    with col3:
        if st.button("Mark as Mastered"):
            st.session_state.study_progress[topic_status] = "Mastered"
            st.success(f"'{topic_status}' mastered!")
    
    if st.session_state.study_progress:
        st.markdown("### Your Progress")
        for topic, status in st.session_state.study_progress.items():
            emoji = "📖" if status == "Studying" else "🔄" if status == "Review" else "✅"
            st.write(f"{emoji} **{topic}**: {status}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📚 AI Study Assistant | Made with Streamlit</p>
    <p>Tip: Download your generated content to review offline!</p>
</div>
""", unsafe_allow_html=True)