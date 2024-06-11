import json

from flask import jsonify

import utils
from config import Config
from langchain_openai import OpenAI
from langchain_core.prompts.few_shot import FewShotPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.prompts.prompt import PromptTemplate


class LLMHandler:

    def __init__(self):
        self.openai = OpenAI(api_key=Config.OPENAI_API_KEY)

    def handle_example(self, input_data):
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
            prefix=f"""
            Given the user input, provide a list of knowledge areas that the user has experience with.
            \nThese are examples knowledge areas: {knowledge_areas} 
            \nThese are examples of good responses:
            """,
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

    def handle(self, input_data):

        knwowledge_tree = json.dumps(utils.llm_json_tree().json, indent=5)
        knwowledge_tree = knwowledge_tree.replace('{', '{{').replace('}', '}}')

        good_examples = [
            {
                "input":
                """
My experience includes 5 years of coding in Python and 3 years of coding in Java. I am a software developer.
I have experience with Java, Python, C++, and Flask. 
                """,
                "output": """
{
  "skill": "LKS",
  "sub_skill": [
    {
      "skill": "Consultoría tecnológica",
      "sub_skill": [
        {
          "skill": "Desarrollo",
          "sub_skill": [
            {
              "skill": "Lenguajes de programación",
              "sub_skill": [
                {
                  "skill": "Java"
                }
              ]
            }
         ]
        }
     ]
    }
  ]
}
                """
            }

        ]

        good_examples_prompt_template = PromptTemplate(
            input_variables=["input", "output"],
            template="Input: {input}\nOutput: {output}"
        )

        good_examples_prompt = FewShotPromptTemplate(
            input_variables=["knowledge_tree", "input"],
            examples=good_examples,
            example_prompt=good_examples_prompt_template,
            prefix=f"""
Given the knowledge tree of the company LKS and a worker's curriculum, provide a subtree of the knowledge tree
that the worker has experience with. The returned subtree must be a subset of the knowledge tree of the company LKS, with the
same structure and format. Use the example's format to provide the output.
\nThis is the knowledge tree of the company LKS: {knwowledge_tree}
\nThese are examples of good responses:
            """,
            suffix="User's input: {input} \nOutput:"
        )

        print(good_examples_prompt.format(knowledge_tree=knwowledge_tree))


        llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0)
        llm_chain = good_examples_prompt_template.format(input=input_data, knwowledge_tree=knwowledge_tree) | llm

       # completion = self.openai.chat.completions.create(
       #     model=Config.LLM_MODEL,
       #     messages=[
       #         {"role": "system", "content": good_examples_prompt.format(knowledge_areas=knowledge_areas)},
       #         {"role": "user", "content": user_prompt.format(input=input_data)}
       #     ],
       #     temperature=0
       # )

       # print(json.dumps(completion.dict(), indent=4))
#
#        return jsonify(completion.dict())


