import streamlit as st
import os
from streamlit_chat import message
import re
st.header("FAQ")
st.sidebar.header("Options")
from core_llm import run_llm, listen_from_mic
plot_choice = st.sidebar.radio("Choose plot type:", ["Chat FAQ", "Voice FAQ"])

if plot_choice == "Chat FAQ":
    st.write("You are in Chat FAQ mode")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "greeting_displayed" not in st.session_state:
        st.session_state["greeting_displayed"] = False
    
    # Display chat history.
    for chat in st.session_state["chat_history"]:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])
            
    if not st.session_state["greeting_displayed"]:
        with st.chat_message("assistant"):
            st.markdown("สวัสดีครับ ผมคือ NT Assistant ผมสามารถช่วยคุณได้ในการตอบคำถามเกี่ยวกับ NT ครับ")
        st.session_state["greeting_displayed"] = True
    
    # Accept user input.
    if prompt := st.chat_input("Say something"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            response = run_llm(query=prompt)
            answer = response['messages'][-1].content  # Get the latest response.
            st.markdown(answer)
            st.session_state["chat_history"].append({"role": "assistant", "content": answer})
        
        # Optionally display sources.
        try:
            sources = response['messages'][-2].content
            if sources:
                formatted_sources = "\n".join(
                    re.findall(r'Content: .*?(?=\nSource:|\Z)', sources, re.DOTALL)
                )
                st.markdown(f"**Sources:**\n\n{formatted_sources}" if formatted_sources else "**Sources:**\n\n There is no source for this answer.")
        except Exception:
            st.markdown("**Sources:**\n\n There is no source for this answer.")
else:
    st.write("You are in Voice FAQ mode")
    audio_value = st.audio_input("Say something")
    if audio_value:
        st.audio(audio_value)
        users_prompt = listen_from_mic(audio_value)
        with st.chat_message("user"):
            st.markdown(users_prompt)
        with st.chat_message("assistant"):
            response = run_llm(query=users_prompt)
            answer = response['messages'][-1].content
            st.markdown(answer)
            try:
                sources = response['messages'][-2].content
                if sources:
                    formatted_sources = "\n".join(
                        re.findall(r'Content: .*?(?=\nSource:|\Z)', sources, re.DOTALL)
                    )
                    st.markdown(f"**Sources:**\n\n{formatted_sources}" if formatted_sources else "**Sources:**\n\n There is no source for this answer.")
            except Exception:
                st.markdown("**Sources:**\n\n There is no source for this answer.")
