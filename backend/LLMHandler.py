import json
import os
import re

from flask import jsonify
from pydantic_core import from_json

import utils
from config import Config
from langchain_openai import ChatOpenAI
from langchain_core.prompts.few_shot import FewShotPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain.globals import set_debug
from langchain_core.output_parsers import JsonOutputParser
import modelTools as modelTools


class LLMHandler:

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, verbose=True)
        set_debug(True)

    def handle(self, input_data):

        knowledge_tree = utils.llm_json_tree()
        knowledge_tree = knowledge_tree.json
        knowledge_tree = json.dumps(knowledge_tree, ensure_ascii=False)

        good_examples = [
            {
                "input":
                """
My experience includes 5 years of coding in Python and 3 years of coding in Java. I am a software developer.
I have experience with Java, Python, C++, and Node. 
                """,
                "output": """ 
{
    "ids": [
    {id:10,name:"Java"},
    {id:16,name:"Python"},
    {id:18,name:"C++"},
    {id:34,name:"Node"}
    ]
}
                """
            },
            {
                "input":
                    f"""
                    {utils.read_data_from_file(os.path.join(Config.STATIC_FOLDER, 'CV', 'cv1.txt'))}
                    """,
                "output": """
{
    "ids": [
    {id:10,name:"Java"},
    {id:14,name:"JavaScript"},
    {id:15,name:"TypeScript"},
    {id:16,name:"Python"},
    {id:19,name:"C#"},
    {id:32,name:"Spring Boot"},
    {id:33,name:"Spring Framework"},
    {id:46,name:"ReactJS"},
    {id:48,name:"Angular"},
    {id:55,name:"Node.js"},
    {id:84,name:"MySQL"},
    {id:85,name:"PostgreSQL"},
    {id:97,name:"Mongo DB"},
    {id:107,name:"Scrum"},
    {id:109,name:"Kanban"},
    {id:133,name:"Jenkins"},
    {id:139,name:"Git"},
    {id:151,name:"Docker"},
    {id:153,name:"Kubernetes"},
    {id:209,name:"REST"},
    {id:297,name:"AWS (Amazon Web Services)"},
    {id:395,name:"Azure"},
    {id:432,name:"Spring"},
    {id:433,name:"Contenedores Kubernetes"},    
    {id:450,name:"Jenkins"},
    {id:463,name:"Jenkinsfile"}
    ]
}
                    """
            }
        ]

        for example in good_examples:
            example["output"] = self.remove_spaces_inside_quotes(example["output"].replace('\n', ''))

        good_examples_prompt_template = ChatPromptTemplate.from_messages(
            [
                "{input} \nOutput: {output}"
            ]
        )

        good_examples_prompt = FewShotChatMessagePromptTemplate(
            examples=good_examples,
            example_prompt=good_examples_prompt_template,
        )

        system_prompt = PromptTemplate(
            input_variables=["knowledge_tree"],
            template="""
Given the knowledge tree of the company LKS and a worker's curriculum, provide an array with the identifiers that represent the subtree of the knowledge tree  
that the worker has experience with. The returned subtree must be a subset of the knowledge tree of the company LKS, there must not be skills that don't belong to the tree,
and there must not be skills that the worker doesn't have experience with.
It is considered that a worker has experience with a skill if it is mentioned as a skill in the worker's curriculum.
If a it has a proyect in which the worker used a skill, it is considered that the worker has experience with that skill.
For example, the subtree: 
{{
  "id": 1,
  "skill": "LKS",
  "sub_skill": [
    {{
      "id": 7,
      "skill": "Consultoría tecnológica",
      "sub_skill": [
        {{
          "id": 8,
          "skill": "Desarrollo",
          "sub_skill": [
            {{
              "id": 9,
              "skill": "Lenguajes de programación",
              "sub_skill": [
                {{
                  "id": 10,
                  "skill": "Java"
                }},
                {{
                  "id": 16,
                  "skill": "Python"
                }}
              ]
            }}
         ]
        }}
     ]
    }}
  ]
}}
Stands for the following list: 
{{
    "id": [10,16]
}}
There is no need to include id's 9,8,7,1, since they are already included with it's children.
Output must only contain the required list in required JSON format.
Use the example's format to provide the output, and use the tree's real id's.
\nThis is the knowledge tree of the company LKS: {knowledge_tree}
            """
        )

        user_prompt = PromptTemplate(
            input_variables=["input"], template="""
\nInput:\n{input}
\nOutput:
"""
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=system_prompt.format(knowledge_tree=knowledge_tree)
            ),
            SystemMessage(
                content="These are examples of good responses:\n"
                + good_examples_prompt.format()
            ),
            user_prompt.format(input=input_data)
        ])

        #print(prompt.format())
        #return 'done'

        llm_chain = prompt | self.llm
        output = llm_chain.invoke(input={"input": input_data})
        output_content = output.content
        print(output_content)
        parsed_json = from_json(output_content, allow_partial=True)
        print(parsed_json)
        return parsed_json

    def remove_spaces_inside_quotes(self, text):
        return re.sub(r'"[^"]*"', lambda m: m.group().replace(' ', ''), text)


def handle(self, input_data):

    knowledge_tree = utils.llm_json_tree()
    knowledge_tree = knowledge_tree.json
    knowledge_tree = json.dumps(knowledge_tree, ensure_ascii=False)

    good_examples = [
        {
            "input":
                """
My experience includes 5 years of coding in Python and 3 years of coding in Java. I am a software developer.
I have experience with Java, Python, C++, and Node. 
                """,
            "output": """ 
{
"id": [10,16,18,34]
}
            """
        },
        {
            "input":
                f"""
            {utils.read_data_from_file(os.path.join(Config.STATIC_FOLDER, 'CV', 'cv1.txt'))}
            """,
            "output": """
{
"id": [10,14,16,19,32,33,46,48,55,84,85,97,107,108,109,133,139,151,153,209,297,395,432,433,451,463]
"id": [10,16,18,34]
}
            """
        }
    ]

    for example in good_examples:
        example["output"] = self.remove_spaces_inside_quotes(example["output"].replace('\n', ''))

    good_examples_prompt_template = ChatPromptTemplate.from_messages(
        [
            "{input} \nOutput: {output}"
        ]
    )

    good_examples_prompt = FewShotChatMessagePromptTemplate(
        examples=good_examples,
        example_prompt=good_examples_prompt_template,
    )

    system_prompt = PromptTemplate(
        input_variables=["knowledge_tree"],
        template="""
Given the knowledge tree of the company LKS and a worker's curriculum, provide an array with the identifiers that represent the subtree of the knowledge tree  
that the worker has experience with. The returned subtree must be a subset of the knowledge tree of the company LKS, there must not be skills that don't belong to the tree,
and there must not be skills that the worker doesn't have experience with.
Make sure to include all the skills that the worker has experience with, and only those.
For example, the subtree: 
{{
"id": 1,
"skill": "LKS",
"sub_skill": [
{{
  "id": 7,
  "skill": "Consultoría tecnológica",
  "sub_skill": [
    {{
      "id": 8,
      "skill": "Desarrollo",
      "sub_skill": [
        {{
          "id": 9,
          "skill": "Lenguajes de programación",
          "sub_skill": [
            {{
              "id": 10,
              "skill": "Java"
            }},
            {{
              "id": 16,
              "skill": "Python"
            }}
          ]
        }}
     ]
    }}
 ]
}}
]
}}
Stands for the following list: 
{{
"id": [10,16]
}}
There is no need to include id's 9,8,7,1, since they are alredy included with it's children.
Ouput must only contain the required list in required JSON format.
Use the example's format to provide the output, and use the tree's real id's.
\nThis is the knowledge tree of the company LKS: {knwowledge_tree}
        """
    )

    user_prompt = PromptTemplate(
        input_variables=["input"], template="""
\nInput:\n{input}
\nOutput:
"""
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=system_prompt.format(knwowledge_tree=knowledge_tree)
        ),
        SystemMessage(
            content="These are examples of good responses:\n"
                    + good_examples_prompt.format()
        ),
        user_prompt.format(input=input_data)
    ])

    #print(prompt.format())
    #return 'done'

    llm_chain = prompt | self.llm
    output = llm_chain.invoke(input={"input": input_data})
    output_content = output.content
    print(output_content)
    parsed_json = from_json(output_content, allow_partial=True)
    print(parsed_json)
    return parsed_json


def remove_spaces_inside_quotes(self, text):
    return re.sub(r'"[^"]*"', lambda m: m.group().replace(' ', ''), text)


