
import gradio as gr
import requests
import re

API_URL = "https://web-production-ffdbc.up.railway.app/invoke"

def call_model_api(prompt, model):
    payload = {
        "prompt": prompt,
        "model": model
    }
    try:
        response = requests.post(API_URL, json=payload)
        data = response.json()
        return data.get("response", "No response")
    except Exception as e:
        return f"error: {str(e)}"

def process_prompts(prompts, gold_answers, models):
    prompts_list = prompts.strip().split("\n")
    gold_list = gold_answers.strip().split("\n")
    model_list = [m.strip() for m in models.split(",")]

    if len(prompts_list) != len(gold_list):
        return "Mismatch between prompts and gold answers!"

    results = []
    for i, prompt in enumerate(prompts_list):
        comparison = gold_list[i]
        full_prompt = f"{prompt} Compare your answer with the gold answer that {comparison} and give me a semantic overlap percentage value."
        row_results = {"Prompt": prompt, "Comparison": comparison}
        for model in model_list:
            response = call_model_api(full_prompt, model)
            match = re.search(r"(\d+(\.\d+)?)%", response)
            percentage = match.group(1) + "%" if match else "error"
            row_results[model] = {"Response": response, "Semantic Overlap": percentage}
        results.append(row_results)
    
    return results

def display_results(prompts, gold_answers, models):
    results = process_prompts(prompts, gold_answers, models)
    output = ""
    for res in results:
        output += f"### Prompt: {res['Prompt']}\n"
        output += f"**Gold Answer:** {res['Comparison']}\n"
        for model, data in res.items():
            if model in ["Prompt", "Comparison"]:
                continue
            output += f"- **{model}**: {data['Semantic Overlap']} — _{data['Response']}_\n"
        output += "\n---\n"
    return output


with gr.Blocks() as demo:
    gr.Markdown("# AIVerde: Multi-LLM Semantic Overlap Checker")

    prompts = gr.Textbox(label="Enter Prompts (one per line)", lines=10, placeholder="Prompt 1\nPrompt 2")
    golds = gr.Textbox(label="Enter Gold Answers (one per line, corresponding to each prompt)", lines=10)
    models = gr.Textbox(label="Enter LLM Models (comma-separated)", placeholder="gpt-4, llama3, mistral")

    output = gr.Markdown()

    run_button = gr.Button("Retrieve Results")
    run_button.click(display_results, inputs=[prompts, golds, models], outputs=[output])

demo.launch()

