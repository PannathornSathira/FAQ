from core_llm import run_llm, listen_from_mic
import streamlit as st
from streamlit_chat import message
import re


st.header("FAQ")
st.sidebar.header("Options")


plot_choice = st.sidebar.radio("Choose plot type:", ["Chat FAQ", "Voice FAQ"])
if plot_choice == "Chat FAQ":
    st.write("You are in Chat FAQ mode")
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "greeting_displayed" not in st.session_state:
        st.session_state["greeting_displayed"] = False  
    # Display chat messages from history on app rerun
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    # Hello message for a new users
    if not st.session_state["greeting_displayed"]:
        with st.chat_message("assistant"):
            st.markdown("สวัสดีครับ ผมคือ NT Assistant ผมสามารถช่วยคุณได้ในการตอบคำถามเกี่ยวกับ NT ครับ")
        st.session_state["greeting_displayed"] = True
    # Accept user input
    if prompt := st.chat_input("Say something"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state["chat_history"].append({"role": "user", "content": prompt})

        # Generate assistant response
        with st.chat_message("assistant"):
            response = run_llm(query=prompt)
            answer = response['messages'][-1].content # Get the AIassistant's response, 0 is Human message
            st.markdown(answer)
            # Add assistant response to chat history
            st.session_state["chat_history"].append({"role": "assistant", "content": answer})
        # Optional: Display sources or additional context
        try:
            sources = response['messages'][-2].content
            print(sources)
            print("-----------------------------")
            if sources:
                formatted_sources = re.findall(r'Content: .*?(?=\nSource:|\Z)', sources, re.DOTALL)
                formatted_sources = "\n".join(formatted_sources)
                if len(formatted_sources) > 0:
                    st.markdown(f"**Sources:**\n\n {formatted_sources}")
                else:
                    st.markdown(f"**Sources:**\n\n There is no source for this answer.")
        except:
            st.markdown(f"**Sources:**\n\n There is no source for this answer.")
        
       
else:
    st.write("You are in Voice FAQ mode")
    audio_value = st.audio_input("Say something")
    if audio_value:
        st.audio(audio_value)
        users_prompt = listen_from_mic(audio_value, )
        with st.chat_message("user"):
                st.markdown(users_prompt)
        with st.chat_message("assistant"):
            response = run_llm(query=users_prompt)
            answer = response['messages'][-1].content # Get the AIassistant's response, 0 is Human message
            st.markdown(answer)
            try:
                sources = response['messages'][-2].content
                if sources:
                    formatted_sources = re.findall(r'Content: .*?(?=\nSource:|\Z)', sources, re.DOTALL)
                    formatted_sources = "\n".join(formatted_sources)
                    if len(formatted_sources) > 0:
                        st.markdown(f"**Sources:**\n\n {formatted_sources}")
                    else:
                        st.markdown(f"**Sources:**\n\n There is no source for this answer.")
            except:
                st.markdown(f"**Sources:**\n\n There is no source for this answer.")
   
    
