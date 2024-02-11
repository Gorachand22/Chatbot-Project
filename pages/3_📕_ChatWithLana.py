"""In this file the chate bot will take the file as input and return the results"""
import streamlit as st
import pandasai
from pandasai.llm import OpenAI
from API import API
from pandasai import SmartDataframe
from numpy.random import choice
from numpy import arange as ar
import os
import shutil

st.set_page_config(page_title="Chat With Lana", page_icon="🗨️", layout= "wide")

st.title("Talk With Lana🤖")

if "openai" not in st.session_state:
    st.session_state["openai"] = None

if st.session_state["openai"] is None:
    st.session_state["openai"] = API.verify_api()

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hi I am Lana. How can I help you?"}]

if "data" not in st.session_state:
    st.session_state["data"] = None

if st.session_state["data"] is None:
    st.session_state["data"] = API.import_data()

if st.session_state["data"] is not None:
    col1, col2 = st.columns([3,2])

    with col1:
            with st.expander("🔎 Dataframe Preview"):
                st.dataframe(st.session_state["data"], use_container_width=True)
    
    with col2:
        if st.session_state["openai"] is not None and st.session_state["data"] is not None:
            for message in st.session_state["messages"]:
                with st.chat_message(message["role"]):
                    try:
                        if type(message['content']) == pandasai.smart_dataframe.SmartDataframe:
                            st.dataframe(message["content"], use_container_width=True)
                        
                        elif message['content'].endswith(".png"):
                            image_path = f"images/{message['content']}"
                            st.image(image_path, width= 300)
                        else:
                            st.markdown(message["content"])
                    except Exception as e:
                        st.error(e)

            if prompt := st.chat_input("For imgae use plot in start"):
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                st.session_state["messages"].append({"role": "user", "content": prompt})

                with st.chat_message("assistant"):
                    try:
                        box = st.empty()
                        llm = OpenAI(api_token=st.session_state["openai"])

                        df = SmartDataframe(st.session_state["data"], config={"llm": llm})

                        if prompt.lower().startswith("plot"):
                            try:
                                df.chat(prompt)
                                number = choice(ar(100), replace = False)
                                image_number = str(number)+".png"
                                st.session_state["messages"].append({"role": "assistant", "content": image_number})
                                source_file_path = f"exports/charts/temp_chart.png"
                                destination_folder_path = "images"
                                try:
                                    shutil.move(source_file_path, destination_folder_path)
                                except Exception as e:
                                    st.error(e)
                                
                                old_path = f"images/temp_chart.png"
                                new_path = f"images/{image_number}"
                                try:
                                    os.rename(old_path, new_path)
                                except Exception as e:
                                    st.error(e)

                                box.image(f"images/{image_number}", width=300)
                                
                                API.save_image(f"images/{image_number}")

                            except Exception as e:
                                st.error(e)
                        
                        else:
                            try:
                                full_response = df.chat(prompt)
                                box.markdown(full_response)
                                st.session_state["messages"].append({"role": "assistant", "content": full_response})
                            except Exception as e:
                                st.write(e)

                    except Exception as e:
                        st.error(e)

    if st.session_state["openai"] is not None and st.session_state["data"] is not None:
        if st.button("reset"):
            st.session_state["data"] = None
            st.session_state["messages"] = [{"role": "assistant", "content": "Hi I am Lana. How can I help you?"}]
            
        
        