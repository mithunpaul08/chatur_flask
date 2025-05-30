# works brilliantly-run this code using: 
# streamlit run v3_asynchronous_python_streamlit.py

import asyncio
import aiohttp
import pandas as pd
import streamlit as st
import re

API_URL = "https://web-production-ffdbc.up.railway.app/invoke"

# Async call to the model API
async def fetch_response(session, prompt, model):
    payload = {"prompt": prompt, "model": model}
    try:
        async with session.post(API_URL, json=payload) as resp:
            result = await resp.json()
            response_text = result.get("response", "No response")
            match = re.search(r"(\d+(\.\d+)?)%", response_text)
            percentage = match.group(1) + "%" if match else "error"
            return model, response_text, percentage
    except Exception as e:
        return model, f"error: {str(e)}", "error"

# Main async processing logic
async def process_all(prompts, golds, models, placeholder):
    prompts_list = prompts.strip().split("\n")
    golds_list = golds.strip().split("\n")
    model_list = [m.strip() for m in models.split(",") if m.strip()]

    if len(prompts_list) != len(golds_list):
        st.error("Mismatch between number of prompts and gold answers")
        return

    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(len(prompts_list)):
            prompt = prompts_list[i]
            gold = golds_list[i]
            full_prompt = f"{prompt} Compare your answer with the gold answer that {gold} and give me a semantic overlap percentage value."
            for model in model_list:
                model_name, response, percentage = await fetch_response(session, full_prompt, model)
                results.append({
                    "Prompt": prompt,
                    "Gold": gold,
                    "Model": model_name,
                    "Response": response,
                    "% Overlap": percentage
                })
                df = pd.DataFrame(results)
                placeholder.dataframe(df, use_container_width=True)

# Streamlit UI
st.title("AIVerde Async Multi-LLM Comparator (Streaming)")

prompts_input = st.text_area("Prompts (one per line)", height=200)
golds_input = st.text_area("Gold Answers (one per line, matching prompts)", height=200)
models_input = st.text_input("Models (comma-separated)", value="gpt-4, llama3, mistral")

run_button = st.button("Compare with LLMs")
placeholder = st.empty()

if run_button:
    asyncio.run(process_all(prompts_input, golds_input, models_input, placeholder))
