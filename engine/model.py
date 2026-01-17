from llama_cpp.llama_types import ChatCompletion
from llama_cpp import Llama, LlamaDiskCache
class Model:
    def __init__(self, max_tokens=512):
        self.llm = Llama.from_pretrained(
            repo_id="Qwen/Qwen2.5-1.5B-Instruct-GGUF",
            filename="qwen2.5-1.5b-instruct-fp16.gguf",
            verbose=False
        )

        cache = LlamaDiskCache(cache_dir="./llama_cache_moon")
        self.llm.set_cache(cache)
        self.max_tokens = max_tokens
        self.system_prompt = """Fix spelling errors. Keep original wording and style. Return only corrected text."""
        return

    def guess_words(self, input:str, context:str | None, cursor_pos:int):
        # Use a Few-Shot prompt to 'teach' the model the expected output format
        prompt = f"""Task: Predict the most likely word
        Format: Output only the word.

        Context: {context} {input}
        Answer:"""

        try:
            output = self.llm.create_completion(
                prompt=prompt,
                max_tokens=5, # Predicting one word usually needs < 5 tokens
                stop=["\n", " "], # Stop at a newline OR the next space
                # temperature=0.1,  # Low temperature is critical for prediction
                echo=False
            )

            # Clean the result
            guess = output["choices"][0]["text"].strip()

            # Basic validation: ensure we didn't get an empty string
            return guess if guess else input

        except Exception as e:
            print(f"LLM Error: {e}")
            return input

    def suggestion(self, input):
        context = []

        if len(context) < 1:
            context = None
        prompt = f"""
        {self.system_prompt}
        context: {context}
        Fix spelling and grammar: {input}
        """

        print(f"Prompt: {prompt}")

        output  = self.llm(
            prompt,
            max_tokens=self.max_tokens,
            stop=["\n"],
            echo=False,
            stream=False
        )
        print(f"Output: {output}")

        if type(output) is not ChatCompletion:
            return input

        print(f"Choices: {output["choices"]}")
        print(f"Text 0: {output["choices"][0]}")
        return output["choices"][0]["text"]
