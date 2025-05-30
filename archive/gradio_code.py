with gr.Blocks() as demo:
    gr.Markdown("# AIVerde: Multi-LLM Semantic Overlap Checker")

    prompts = gr.Textbox(label="Enter Prompts (one per line)", lines=10, placeholder="Prompt 1\nPrompt 2")
    golds = gr.Textbox(label="Enter Gold Answers (one per line, corresponding to each prompt)", lines=10)
    models = gr.Textbox(label="Enter LLM Models (comma-separated)", placeholder="gpt-4, llama3, mistral")

    output = gr.Markdown()

    run_button = gr.Button("Retrieve Results")
    run_button.click(display_results, inputs=[prompts, golds, models], outputs=[output])

demo.launch()

