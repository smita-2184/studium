from openai import OpenAI
from groq_response import groq_response
import os

    

client = OpenAI(api_key="sk-proj-LbV3MWdpwjke6F78YaxnT3BlbkFJCLyvrwidEnZm25W3jap")
my_assistant = client.beta.assistants.retrieve("asst_uiXLXNB6fSB2FAgKZk9nAce6")
ass_id = "asst_uiXLXNB6fSB2FAgKZk9nAce6"

def retrival_openai(prompt, instructions):
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=ass_id,
        instructions=instructions
    )
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        assistant_messages = [message for message in messages.data if message.role == 'assistant']
        for message in assistant_messages:
            for content_block in message.content:
                # Check if there's a method or property to get 'value'
                if hasattr(content_block.text, 'value'):
                    return content_block.text.value                    
                else:
                    # Otherwise print the object to debug
                    #st.write(messages)
                    #st.write(content_block.text)
                    return None
    else:
        return None
    
