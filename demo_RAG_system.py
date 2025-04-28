import streamlit as st
import os
from streamlit_chat import message
import pandas as pd
import re
st.header("FAQ")
st.sidebar.header("Options")
from core_llm import run_llm, listen_from_mic, generate_thai_answer, generate_thai_tts
from original_core_llm import origi_llm
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
            response_origi = origi_llm(query=prompt)
            answer_origi = response_origi['messages'][-1].content
            answer_origi = 'Original answer : ' + answer_origi
            st.markdown(answer_origi)
           
            response = run_llm(query=prompt)
            answer = response['messages'][-1].content 
            answer = 'SAR Enhance answer : ' + answer
            st.markdown(answer)
            
            st.session_state["chat_history"].append({"role": "assistant", "content": answer_origi})
            st.session_state["chat_history"].append({"role": "assistant", "content": answer})
        with st.expander("🔍 Show Source Of FAQ"):
            df = pd.read_csv("Expanded_nt_QA.csv", index_col=0)
            st.dataframe(df)
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
            #audio_answer = generate_thai_answer(answer)
            audio_answer, sample_rate = generate_thai_tts(answer)
            st.audio(audio_answer, sample_rate= sample_rate)
            st.markdown(answer)
        with st.expander("🔍 Show Source Of FAQ"):
            df = pd.read_csv("Expanded_nt_QA.csv", index_col=0)
            st.dataframe(df)
