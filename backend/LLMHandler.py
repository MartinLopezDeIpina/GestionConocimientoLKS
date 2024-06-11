import json

from flask import jsonify

from config import Config
from openai import OpenAI, ChatCompletion
from langchain_core.prompts.few_shot import FewShotPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.prompts.prompt import PromptTemplate


class LLMHandler:

    def __init__(self):
        self.openai = OpenAI(api_key=Config.OPENAI_API_KEY)

    def handle(self, input_data):
        good_examples = [
            {
                "input": "I coded python for 5 years and java for 3 years. I am a software developer.",
                "output": "Java, Python"
            },
            {
                "input": "In my career, I have worked with Java, Python, and C++.",
                "output": "Java, Python, C++"
            },
            {
                "input": "I have experience with Java, Python, C++, and Flask",
                "output": "Java, Python, C++, Flask"
            }
        ]
        bad_examples = [
            {
                "input": "I have worked with Java, Python, and C++.",
                "output": "Java, Python",
                "expected_output": "Java, Python, C++",
                "explanation": "The output should include C++"
            },
            {
                "input": "I have experience with Java, Python, C++, and Flask",
                "output": "Java, Flask",
                "expected_output": "Java, Python, C++, Flask",
                "explanation": "The output should include Python and C++"
            }
        ]
        knowledge_areas = "Java,Python,C++,Flask"

        good_examples_prompt_template = PromptTemplate(
            input_variables=["input", "output"],
            template="Input: {input}\nOutput: {output}"
        )

        good_examples_prompt = FewShotPromptTemplate(
            input_variables=["knowledge_areas"],
            examples=good_examples,
            example_prompt=good_examples_prompt_template,
            prefix=f"""Given the user input, provide a list of knowledge areas that the user has experience with.
            \nThese are examples knowledge areas: {knowledge_areas} 
            \nThese are examples of good responses:""",
            suffix=" "
        )

        print(good_examples_prompt.format(knowledge_areas=knowledge_areas))

        user_prompt = PromptTemplate(
            input_variables=["input"], template="Input: {input} \nOutput:"
        )

        completion = self.openai.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[
                {"role": "system", "content": good_examples_prompt.format(knowledge_areas=knowledge_areas)},
                {"role": "user", "content": user_prompt.format(input=input_data)}
            ],
            temperature=0
        )

        print(json.dumps(completion.dict(), indent=4))

        return jsonify(completion.dict())



