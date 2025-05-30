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

# Async generator that streams results as they arrive
async def stream_results(prompts, golds, models):
    prompts_list = prompts.strip().split("\n")
    golds_list = golds.strip().split("\n")
    model_list = [m.strip() for m in models.split(",") if m.strip()]

    if len(prompts_list) != len(golds_list):
        yield pd.DataFrame([{"Error": "Mismatch between number of prompts and gold answers"}])
        return

    async with aiohttp.ClientSession() as session:
        for i in range(len(prompts_list)):
            prompt = prompts_list[i]
            gold = golds_list[i]
            full_prompt = f"{prompt} Compare your answer with the gold answer that {gold} and give me a semantic overlap percentage value."
            for model in model_list:
                model_name, response, percentage = await fetch_response(session, full_prompt, model)
                row = pd.DataFrame([{
                    "Prompt": prompt,
                    "Gold": gold,
                    "Model": model_name,
                    "Response": response,
                    "% Overlap": percentage
                }])
                yield row

# Wrapper to call the async generator
async def process_inputs_stream(prompts, golds, models):
    async for row in stream_results(prompts, golds, models):
        yield gr.Dataframe.update(value=row, append=True)

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# AIVerde Async Multi-LLM Comparator (Streaming)")

    with gr.Row():
        prompts = gr.Textbox(label="Prompts (one per line)", lines=10)
        golds = gr.Textbox(label="Gold Answers (one per line, matching prompts)", lines=10)

    models = gr.Textbox(label="Models (comma-separated)", placeholder="gpt-4, llama3, mistral")

    submit_btn = gr.Button("Compare with LLMs")
    output_df = gr.Dataframe(headers=["Prompt", "Gold", "Model", "Response", "% Overlap"],
                             interactive=False, wrap=True, visible=True)

    submit_btn.click(fn=process_inputs_stream, inputs=[prompts, golds, models], outputs=output_df)

if __name__ == "__main__":
    demo.launch()
