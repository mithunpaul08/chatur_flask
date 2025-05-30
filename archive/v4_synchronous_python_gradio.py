import asyncio
import aiohttp
import pandas as pd
import gradio as gr
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

# Process all prompts asynchronously
async def process_all_prompts_async(prompts, golds, models):
    prompts_list = prompts.strip().split("\n")
    golds_list = golds.strip().split("\n")
    model_list = [m.strip() for m in models.split(",") if m.strip()]

    if len(prompts_list) != len(golds_list):
        raise ValueError("Mismatch between number of prompts and gold answers")

    all_results = []
    async with aiohttp.ClientSession() as session:
        for i in range(len(prompts_list)):
            prompt = prompts_list[i]
            gold = golds_list[i]
            full_prompt = f"{prompt} Compare your answer with the gold answer that {gold} and give me a semantic overlap percentage value."
            row = {"Prompt": prompt, "Gold": gold}
            tasks = [fetch_response(session, full_prompt, model) for model in model_list]
            results = await asyncio.gather(*tasks)
            for model, response, percentage in results:
                row[f"{model} - %"] = percentage
                row[f"{model} - Response"] = response
            all_results.append(row)
    return pd.DataFrame(all_results)

# Wrapper for Gradio
def process_inputs(prompts, golds, models):
    df = asyncio.run(process_all_prompts_async(prompts, golds, models))
    return df

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# AIVerde Async Multi-LLM Comparator")

    with gr.Row():
        prompts = gr.Textbox(label="Prompts (one per line)", lines=10)
        golds = gr.Textbox(label="Gold Answers (one per line, matching prompts)", lines=10)

    models = gr.Textbox(label="Models (comma-separated)", placeholder="gpt-4, llama3, mistral")

    submit_btn = gr.Button("Compare with LLMs")
    output_df = gr.Dataframe(headers=None, interactive=False, wrap=True, max_rows=100, max_cols=100)

    submit_btn.click(fn=process_inputs, inputs=[prompts, golds, models], outputs=output_df)

if __name__ == "__main__":
    demo.launch()
