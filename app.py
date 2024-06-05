from groq import Groq
import groq
import streamlit as st
st.set_page_config(page_title="Studium®", page_icon="🌐", layout="wide")
from openai import OpenAI
import json
from groq_response import groq_response
import streamlit.components.v1 as components
from youtube_transcript_api import YouTubeTranscriptApi
from youtubesearchpython import VideosSearch
import os
import queue
from mi import update_miro_content, get_connector_mappings, get_end_item, add_shape, get_frame_items, get_tags
import re
import tempfile
import threading
import requests
from bs4 import BeautifulSoup
from open_api import retrival_openai
import streamlit_authenticator as stauth  # pip install streamlit-authenticator

# --- USER AUTHENTICATION ---
import yaml
from yaml.loader import SafeLoader

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)
authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
#------------------------------------------------------------
if st.session_state["authentication_status"]:
    st.session_state.selected_language = st.radio("Choose your language",["English", "Deutsch"], horizontal=True)    
    ass_id = "asst_uiXLXNB6fSB2FAgKZk9nAce6"
    os.environ['OPENA_AI_API_KEY'] = "sk-proj-LbV3MWdpwjke6F78YaxnT3BlbkFJCLyvrwidEnZm25W3jap"
    os.environ['GROQ_API_KEY'] = "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"
    
        
    client_groq = Groq(api_key=os.environ['GROQ_API_KEY'])
    client_openai = OpenAI(api_key=os.environ['OPENA_AI_API_KEY'] )
    
    link_custom_functions = [
        {
            'name': 'extract_website_url',
            'description': 'Get the website url',
            'parameters': {
                'type': 'object',
                'properties': {
                    'link': {'type': 'string', 'description': 'website url'},
            }
        }
        }
    ]
    
    
    # Initialize your clients with API keys
    client_openai = OpenAI(api_key=os.environ['OPENA_AI_API_KEY'])
    client_groq = Groq(api_key=os.environ['GROQ_API_KEY'])
    client_groq_one = Groq(api_key=os.environ['GROQ_API_KEY'])
    
    # Define your custom functions for OpenAI
    scenario_custom_functions = [
        {
            'name': 'extract_scenario_info',
            'description': 'Get the individual scenarios text in english or german whicherever they are already in, do not change the language',
            'parameters': {
                'type': 'object',
                'properties': {
                    'scenario_1': {'type': 'string', 'description': 'scenario number 1 full text'},
                    'scenario_2': {'type': 'string', 'description': 'scenario number 2 full text'},
                    'scenario_3': {'type': 'string', 'description': 'scenario number 3 full text'},
                    'scenario_4': {'type': 'string', 'description': 'scenario number 4 full text'},
                }
            }
        }
    ]
    
    scenario_keyword_functions = [
        {
            'name': 'extract_scenario_info',
            'description': 'Get the individual scenarios text',
            'parameters': {
                'type': 'object',
                'properties': {
                    'keyword_1': {'type': 'string', 'description': 'keyword 1'},
                    'keyword_2': {'type': 'string', 'description': 'keyword 2'},
                    'keyword_3': {'type': 'string', 'description': 'keyword 3'},
                    'keyword_4': {'type': 'string', 'description': 'keyword 4'},
                }
            }
        }
    ]
    
    video_custom_functions = [
        {
            'name': 'extract_video_id',
            'description': 'Get the video ID',
            'parameters': {
                'type': 'object',
                'properties': {
                    'video_id': {'type': 'string', 'description': 'video ID'},
            }
        }
        }
    ]
    # Initialize a string to store all transcripts
    all_video_transcripts = ""
    
    molecule_custom_functions = [
        {
            'name': 'extract_molecule_info',
            'description': 'Get the molecule name',
            'parameters': {
                'type': 'object',
                'properties': {
                    'molecule_name': {'type': 'string', 'description': 'name of the molecule'},
            }
        }
        }
    ]
    
    keyword_custom_functions = [
        {
            'name': 'extract_keyword_info',
            'description': 'Get the search query keyword',
            'parameters': {
                'type': 'object',
                'properties': {
                    'keyword': {'type': 'string', 'description': 'keyword of teh search query'},
            }
        }
        }
    ]
    # Streamlit UI
    st.title("Materials Science")
    image_variable = None
    # Session states initialization
    if 'prompt' not in st.session_state:
        st.session_state.prompt = ''
    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = []
    if 'selected_options_reaction' not in st.session_state:
        st.session_state.selected_options_reaction = []
    if 'selected_language' not in st.session_state:
        st.session_state.selected_language = []    
    
    
    # User inputs
    st.session_state.selected_options = st.multiselect("Select options", ["fun based", "context based", "real world based", "conceptual textbook based"])
    st.session_state.prompt = st.text_input("Enter your prompt")
    check_box = st.checkbox("Open Chem Sketcher")
    check_box_frame = st.checkbox("Run Miro Frame Items")
    if check_box_frame:
        get_frame_items(3458764589119443158)    
    
    with st.sidebar:
        st.sidebar.title("Chat with the assistant 🤖")
        # Input for search query
        search_query = st.sidebar.text_input("Enter your video search query")
        if search_query:
            prompt = search_query
            content = "please correct the spelling and write the precise one search keyword for and only give teh keyword, only 1 and nothing else other that that : "
            response = groq_response(content, prompt)
            response_functions = client_openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{'role': 'user', 'content': response}],
                    functions=keyword_custom_functions,
                    function_call='auto'
                )
            data = json.loads(response_functions.choices[0].message.function_call.arguments)
            keyword = data['keyword']
            st.sidebar.write(keyword)
            # Perform the search
            videosSearch = VideosSearch(search_query, limit=3)
            video_one = VideosSearch(search_query, limit=1)
            for video in video_one.result()['result']:
                video_one_id = video['id']
            
            for video in videosSearch.result()['result']:
                video_id = video['id']  # Extract video ID
                
                # Display the video thumbnail
                #st.image(video['thumbnails'][0]['url'])
                
                # Display the video title
                #st.write(f"**{video['title']}**")
                
                try:
                    # Fetch the transcript for the video ID
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                    
                    # Concatenating all text from the transcript
                    transcript_text = "\n".join([t['text'] for t in transcript_list])
                    
                    # Concatenate the transcript to the all_video_transcripts variable
                    all_video_transcripts += f"\n---\nTranscript for Video ID {video_id}:\n{transcript_text}\n---\n"
                    
                except Exception as e:
                    error_message = "Transcript not available or error in fetching transcript."
                    # Concatenate the error message to the all_video_transcripts variable
                    all_video_transcripts += f"\n---\nTranscript for Video ID {video_id}:\n{error_message}\n---\n"
    
        # At this point, all_video_transcripts contains transcripts for all videos concatenated as a single string.
        # You can display it or process it as needed.
        # Here's an example of displaying the combined transcripts:
        video_id = ""
        if all_video_transcripts:
            #st.text_area("All Video Transcripts", all_video_transcripts, height=300)
            prompt = all_video_transcripts
            content = "write a one sentence summary for the the given videos and always preserve and give me the vido_id always "
            video_compression = groq_response(content, prompt)
            compressed_transcripts = video_compression
            prompt = compressed_transcripts
            content = "give me the best video with maximum content and the best keywords from the transcript and always preserve and give me teh vido_id always "
            chat_completion = groq_response(content, prompt)
            #st.write(chat_completion.choices[0].message.content)
            video_id_fetch = chat_completion
            #st.write(video_id_fetch)
            response_functions = client_openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{'role': 'user', 'content': video_id_fetch}],
                    functions=video_custom_functions,
                    function_call='auto'
                )
            data = json.loads(response_functions.choices[0].message.function_call.arguments)
            video_id = data['video_id']
            st.video(f"https://www.youtube.com/watch?v={video_id}")
    
        messages = st.container(height=630)
        if image_variable:
            messages.chat_message("assistant").write(f"When you react {reactant_1} with {reactant_2} using {reagent_3}, you get {product_4} and {product_5}" + " here is the reaction in 2D bond representation:")
            messages.image(image_variable)
        if check_box:
            messages.chat_message("assistant").write("Here is the Chem Sketcher for you to draw the molecule:")
            with messages.chat_message("assistant"):
                components.iframe("https://miro.com/app/live-embed/uXjVKLxF5x8=/?moveToViewport=5001,-1914,880,1211&embedId=486265033244", height=600)     
        prompt_sidebar = st.chat_input("Say something")
        if prompt_sidebar:
            messages.chat_message("user").write(prompt_sidebar)
            prompt = prompt_sidebar
            sidebar_chat = retrival_openai(prompt, instructions="Please answer this query")
            if sidebar_chat is None:
                sidebar_chat = groq_response("please answer this query : ", prompt)
            messages.chat_message("assistant").write(sidebar_chat)
    tab1, tab2 = st.tabs(["Main Page","Miro"])
    with tab1:
        st.header("Main Page")
        if st.session_state.prompt:
                prompt = st.session_state.prompt
                selected_options = " ".join(st.session_state.selected_options)
                response = retrival_openai(prompt, instructions=f"Please create a brief detailed explaination of the query and give back information from the book and teh user wants to learn the topic in a {selected_options} ")
                language = " ".join(st.session_state.selected_language)
                messages = [
                    {"role": "user", "content": f"create a {selected_options} scenarios based task question for learning matrial science from teh given explaination of teh topic, create 4 scenarios each time and number them: {response} and the language in which you need to create teh scenarios is {language}"},
                ]
                chat_completion = client_groq.chat.completions.create(
                    messages=messages,
                    model="mixtral-8x7b-32768",
                )
                response = chat_completion.choices[0].message.content
        
                if response:
                    response_functions = client_openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{'role': 'user', 'content': response}],
                        functions=scenario_custom_functions,
                        function_call='auto'
                    )
                    data = json.loads(response_functions.choices[0].message.function_call.arguments)
        
                    # Tabs for scenarios
                    scenario_tabs = ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4']
                    tabs = st.tabs(scenario_tabs)
                    for i, tab in enumerate(tabs):
                        with tab:
                            st.header(scenario_tabs[i])
                            scenario_text = data[f'scenario_{i+1}']
                            st.write(scenario_text)
                            prompt = scenario_text
                            content = "subdivide this scenario into three subquestions and only give the questions in the " + language + ". The scenario is: "
                            chat_completion_subquestions = groq_response(content, prompt)
                            scenario_generated = chat_completion_subquestions
                            st.write(scenario_generated)
                            prompt = scenario_generated
                            content = f"give a sample ideal step-by-step format to attempt to answer this scenario question as a hint in the {language} language . Scenario: "
                            chat_completion_hint = groq_response(content, prompt)
                            st.text_area("Enter your answer here", key=f'answer_{i}')
                            
                            with st.expander("See hint for answering the question" + str(i+1) + "😀"): 
                                st.write(chat_completion_hint)
                            # Upload PDF button
                            uploaded_file = st.file_uploader("Upload your answer (PDF)", type="pdf", key=f"pdf_uploader_{i}")
                            if uploaded_file is not None:
                                st.success("File uploaded successfully!")
                                
        
                            col1, col2 = st.columns(2)
                            with col1:
                                with st.expander("See explanation 3D"):
                                    components.iframe("https://embed.molview.org/v1/?mode=balls&cid=124527813")
                            with col2:
                                with st.expander("See explanation 2D"):
                                    components.iframe("https://marvinjs.chemicalize.com/v1/fcc0cc8570204c48a6447859c71cf611/editor.html?frameId=2cd5fd97-f496-4b6f-8cbc-417acc66684f&origin=https%3A%2F%2Fwww.rcsb.org")
        
        # Example of error handling with client_groq API callss
    with tab2:
        st.header("Miro")
        components.iframe('https://miro.com/app/live-embed/uXjVKHDu73g=/?moveToViewport=-454,-189,1278,578&embedId=8541893250', height=800, scrolling=True)
        
