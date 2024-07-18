import json
import os
import re

from pydantic_core import from_json

import utils
from LLM.DB.chromaTools import chromaTools
from LLM.DB.modelTools import modelTools
from config import Config
from langchain_openai import ChatOpenAI
from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain.globals import set_debug
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import OpenAI
from tavily import TavilyClient
import logging


class LLMHandler:

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, verbose=False)
        set_debug(True)

        chroma_tools = chromaTools()
        self.modelTools = modelTools(chroma_tools)

    def handle_knowledges(self, input_data):

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
            example["output"] = remove_spaces_inside_quotes(example["output"].replace('\n', ''))

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

    def handle_knowledge_level(self, input_data, knowledge_skills):

        curriculum_example1 = utils.read_data_from_file(os.path.join(Config.STATIC_FOLDER, 'CV', 'cv1.txt'))
        proficency_info = self.modelTools.get_similar_info(input_data)

        knowledge_skills = knowledge_skills.replace('\n', '')
        knowledge_skills = knowledge_skills.replace('{', '{{')
        knowledge_skills = knowledge_skills.replace('}', '}}')

        good_examples = [
            {
                "input":
                """
    Curriculum:
{curriculum_example1}
    Skills:
{{"ids": [
    {{"id": 10, "name": "Java"}},
    {{"id": 14, "name": "JavaScript"}},
    {{"id": 15, "name": "TypeScript"}},
    {{"id": 16, "name": "Python"}}
    {{"id": 19, "name": "C#"}},
    {{"id": 32, "name": "Spring Boot"}},
    {{"id": 33, "name": "Spring Framework"}},
    {{"id": 46, "name": "ReactJS"}},
    {{"id": 48, "name": "Angular"}},
    {{"id": 55, "name": "Node.js"}},
    {{"id": 84, "name": "MySQL"}},
    {{"id": 85, "name": "PostgreSQL"}},
    {{"id": 97, "name": "Mongo DB"}},
    {{"id": 107, "name": "Scrum"}},
    {{"id": 109, "name": "Kanban"}},
    {{"id": 133, "name": "Jenkins"}},
    {{"id": 139, "name": "Git"}},
    {{"id": 151, "name": "Docker"}},
    {{"id": 153, "name": "Kubernetes"}},
    {{"id": 209, "name": "REST"}},
    {{"id": 297, "name": "AWS (Amazon Web Services)"}},
    {{"id": 395, "name": "Azure"}},
    {{"id": 432, "name": "Spring"}},
    {{"id": 433, "name": "Contenedores Kubernetes"}},
    {{"id": 450, "name": "Jenkins"}},
    {{"id": 463, "name": "Jenkinsfile"}}
  ]
}}
                """.format(curriculum_example1=curriculum_example1),
                "output": """
{"ids": [
    {"id":10,"name":"Java",level:3},
    {"id":14,"name":"JavaScript",level:4},
    {"id":15,"name":"TypeScript",level:4},
    {"id":16,"name":"Python",level:3},
    {"id":19,"name":"C#",level:1},
    {"id":32,"name":"Spring Boot",level:1},
    {"id":33,"name":"Spring Framework",level:1},
    {"id":46,"name":"ReactJS",level:3},
    {"id":48,"name":"Angular",level:2},
    {"id":55,"name":"Node.js",level:4},
    {"id":84,"name":"MySQL",level:2},
    {"id":85,"name":"PostgreSQL",level:2},
    {"id":97,"name":"Mongo DB",level:2},
    {"id":107,"name":"Scrum",level:4},
    {"id":109,"name":"Kanban",level:2},
    {"id":133,"name":"Jenkins",level:3},
    {"id":139,"name":"Git",level:4},
    {"id":151,"name":"Docker",level:2},
    {"id":153,"name":"Kubernetes",level:2},
    {"id":209,"name":"REST",level:3},
    {"id":297,"name":"AWS (Amazon Web Services)",level:2},
    {"id":395,"name":"Azure",level:1},
    {"id":432,"name":"Spring",level:1},
    {"id":433,"name":"Contenedores Kubernetes",level:1},    
    {"id":450,"name":"Jenkins",level:3},
    {"id":463,"name":"Jenkinsfile",level:3}
    ]
}
                """
            }
        ]

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
            input_variables=["proficency_info"],
            template="""
Given a worker's curriculum and a list of skills which represent the worker's skills mentioned in the curriculum, 
provide the list of skills with their respective level of experience.

Output must be a JSON in example format, repeating the input skills with the level of experience.

To determine the level of experience, consider the following example scale.
Give special attention to the experience time of the worker with each skill, consider the time dedicated to each skill separated, 
if a worker has 10 years of experience but only 2 with a specific skill, consider the experience level of the worker with that skill as 2:
{proficency_info}
"""
        )

        user_prompt = PromptTemplate(
            input_variables=["input", "knowledge_skills"], template="""
\nInput:\n  Curriculum:{input}\n  Skills:{knowledge_skills}
\nOutput:
"""
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=system_prompt.format(proficency_info=proficency_info)
            ),
            SystemMessage(
                content="These are examples of good responses:\n"
                        + good_examples_prompt.format()
            ),
            user_prompt.format(input=input_data, knowledge_skills=knowledge_skills)
        ])

        #print(prompt.format())
        #return prompt.format()

        llm_chain = prompt | self.llm
        output = llm_chain.invoke(input={"input": input_data})
        output_content = output.content
        print(output_content)
        parsed_json = from_json(output_content, allow_partial=True)
        print(parsed_json)
        return parsed_json


    def handle_try_tavily_search(self, input_data):
        tavily = TavilyClient(api_key=Config.TAVILY_API_KEY)
        results = tavily.search(query=input_data)
        print(results)
        return results

    async def handle_knowledge_metric_reaact(self, input_skill):
        example_output = """
          {
            "experience_area":"AWS (Amazon Web Services)",
            "levels": [
              {
                "level": 1,
                "experience": "Limited practice with AWS services",
                "technical_skills": "Familiarity with the AWS ecosystem and services. Experience with automation testing tools. Proficiency in a programming language. Knowledge of cloud architecture. Understanding of best practices.",
              },
              {
                "level": 2,
                "experience": "1-2 years of practical experience with AWS services",
                "technical_skills": "Certificates like AWS Certified Solutions Architect - Associate, AWS Certified Developer - Associate, AWS Certified SysOps Administrator - Associate, AWS Certified DevOps Engineer - Professional, AWS Certified Solutions Architect - Professional. Hands-on experience with the AWS services their team uses, such as: Deployed and managed applications using EC2, S3, and RDS",
              },
              {
                "level": 3,
                "experience": "3-5 years of practical experience with AWS services",
                "technical_skills": "Effective Communication and Team Collaboration. Comprehensive Cloud Engineering Knowledge: This includes practical experiences with AWS compute, storage, network, and database services. Scripting Skills: Proficiency in scripting languages such as Python, JavaScript, or Perl is important. Experience with Remote and Hybrid Work Models. Practical Experiences with AWS Services: This includes experiences with AWS compute, storage, network, and database services.",
              },
              {
                "level": 4,
                "experience": "6-10 years of practical experience with AWS services",
                "technical_skills": "Advanced Effective Communication and Team Collaboration. Mastery of Remote and Hybrid Work Models. Deep Knowledge of AWS Cloud Skills and Services. Ability to Follow and Implement Learning Plans",
              },
              {
                "level": 5,
                "experience": "Over 10 years of practical experience with AWS services",
                "technical_skills": "Familiarity with the AWS Ecosystem and Services: The worker should have an in-depth understanding of the AWS ecosystem and its various services. Experience with Automation Testing Tools: The worker should have extensive experience with automation testing tools, which are crucial for maintaining the quality of software in a cloud environment.",
              },
              ]
        }
                    """.replace('\n', '').replace('\t', '').replace('{', '{{').replace('}', '}}')


        good_examples = [
            {
                "input": "AWS (Amazon Web Services)",
                "thought_and_actions": """
Thought 1: I need to know which are the new skills that each level of experience with AWS has and then add it to the output following the provided format.
For that, I will need to search for each experience level the skills that a worker with that experience level has with AWS. Then, I will have to 
evaluate in each case if the skills are new or if they are already included in the previous levels. After that, I will add the new skills to the output. 

Thought 2: what are the technicals_skills of a level 1 (limited practice with AWS services) worker with AWS?
Action 1: tavily_search_results_json
Action Input: Skills in AWS a novice worker has
Observation 1: the two results are:
"Strong professional community. Good work-life balance. Skills you need for AWS. Familiarity with the AWS ecosystem and services. Experience with automation testing tools. Proficiency in a programming language. Knowledge of cloud architecture. Experience with agile development methodologies. Understanding of best practices."  
"You can focus on the AWS Cloud skills and services that are most relevant, with options to search or filter by language, domain, and skill level.\n Dive deep on any role or solution with downloadable Ramp-Up Guides and/or follow suggested learning plans designed to build your knowledge and accomplish your career goals. You can learn efficiently by following a suggested learning plan for a specific domain or job role, or you can skip around—it's flexible. Skill Builder provides 500+ free digital courses, 25+ learning plans, and 19 Ramp-Up Guides to help you expand your knowledge. Skill Builder offers training from AWS experts on AWS services, so you can keep up with the pace of innovation."
Thought 3: Based on the results, the 5 skills a novice worker with AWS has are:
1. Familiarity with the AWS ecosystem and services
2. Experience with automation testing tools
3. Proficiency in a programming language
4. Knowledge of cloud architecture
5. Understanding of best practices

Thought 4: what are the technicals_skills of a level 2 (1-2 years of practical experience with AWS services) worker with AWS?
Action 2: tavily_search_results_json
Action Input: Skills a worker with 1-2 years of practical experience with AWS services must have
Observation 2: the two results are:
"Here are some of the most popular AWS certifications to pursue for your resume: AWS Certified Solutions Architect - Associate. AWS Certified Developer - Associate. AWS Certified SysOps Administrator - Associate. AWS Certified DevOps Engineer - Professional. AWS Certified Solutions Architect - Professional."
"Showcase your experience with specific AWS services. Hiring managers want to see that you have hands-on experience with the AWS services their team uses. Rather than simply listing 'AWS' as a skill, call out the specific services you've worked with, such as: Deployed and managed applications using EC2, S3, and RDS"
Thought 5: Based on the results, a worker with 1-2 years of practical experience with AWS services must have the following skills:
1. Certificates like AWS Certified Solutions Architect - Associate, AWS Certified Developer - Associate, AWS Certified SysOps Administrator - Associate, AWS Certified DevOps Engineer - Professional, AWS Certified Solutions Architect - Professional
2. Hands-on experience with the AWS services their team uses, such as: Deployed and managed applications using EC2, S3, and RDS
Action Input: 

Thought 6: what are the technicals_skills of a level 3 (3-5 years of practical experience with AWS services) worker with AWS?
Action 3: tavily_search_results_json
Action Input: Skills a worker with 3-5 years of practical experience with AWS services must have
Observation 3: the two results are:
"Effective Communication and Team Collaboration. Effective communication and collaboration are indispensable skills for AWS Developers. The ability to articulate technical concepts to non-technical stakeholders, work closely with cross-functional teams, and contribute to a shared codebase is essential. In 2024, with remote and hybrid work models ..."
"An AWS Cloud Engineer Resume should display comprehensive cloud engineering knowledge including practical experiences with AWS compute, storage, network, and database services. It should underline scripting skills in Python, JavaScript or Perl with specific examples of improvement in cloud applications or processes."
Thought 7: Based on the results, a worker with 3-5 years of practical experience with AWS services must have the following skills:
1. Effective Communication and Team Collaboration: The ability to articulate technical concepts to non-technical stakeholders, work closely with cross-functional teams, and contribute to a shared codebase is essential.
2. Comprehensive Cloud Engineering Knowledge: This includes practical experiences with AWS compute, storage, network, and database services.
3. Scripting Skills: Proficiency in scripting languages such as Python, JavaScript, or Perl is important
4. Experience with Remote and Hybrid Work Models
5. Practical Experiences with AWS Services: This includes experiences with AWS compute, storage, network, and database services.

Thought 8: what are the technicals_skills of a level 4 (6-10 years of practical experience with AWS services) worker with AWS?
Action 4: tavily_search_results_json
Action Input: Skills a worker with 6-10 years of practical experience with AWS services must have
Observation 4: the two results are:
"Effective Communication and Team Collaboration. Effective communication and collaboration are indispensable skills for AWS Developers. The ability to articulate technical concepts to non-technical stakeholders, work closely with cross-functional teams, and contribute to a shared codebase is essential. In 2024, with remote and hybrid work models ..."
"You can focus on the AWS Cloud skills and services that are most relevant, with options to search or filter by language, domain, and skill level.\n Dive deep on any role or solution with downloadable Ramp-Up Guides and/or follow suggested learning plans designed to build your knowledge and accomplish your career goals. You can learn efficiently by following a suggested learning plan for a specific domain or job role, or you can skip around—it's flexible. Skill Builder provides 500+ free digital courses, 25+ learning plans, and 19 Ramp-Up Guides to help you expand your knowledge. Skill Builder offers training from AWS experts on AWS services, so you can keep up with the pace of innovation."
Thought 9: Based on the results, a worker with 6-10 years of practical experience with AWS services must have the following skills:
1. Advanced Effective Communication and Team Collaboration
2. Mastery of Remote and Hybrid Work Models
3. Deep Knowledge of AWS Cloud Skills and Services
4. Ability to Follow and Implement Learning Plans

Thought 10: what are the technicals_skills of a level 5 (Over 10 years of practical experience with AWS services) worker with AWS?
Action 5: tavily_search_results_json
Action Input: Skills a worker with Over 10 years of practical experience with AWS services must have
Observation 5: the two results are:
"Strong professional community. Good work-life balance. Skills you need for AWS. Familiarity with the AWS ecosystem and services. Experience with automation testing tools. Proficiency in a programming language. Knowledge of cloud architecture. Experience with agile development methodologies. Understanding of best practices."
"You can focus on the AWS Cloud skills and services that are most relevant, with options to search or filter by language, domain, and skill level.\n Dive deep on any role or solution with downloadable Ramp-Up Guides and/or follow suggested learning plans designed to build your knowledge and accomplish your career goals. You can learn efficiently by following a suggested learning plan for a specific domain or job role, or you can skip around—it's flexible. Skill Builder provides 500+ free digital courses, 25+ learning plans, and 19 Ramp-Up Guides to help you expand your knowledge. Skill Builder offers training from AWS experts on AWS services, so you can keep up with the pace of innovation."
Thought 11: Based on the results, a worker with Over 10 years of practical experience with AWS services must have the following skills:
1. Familiarity with the AWS Ecosystem and Services: The worker should have an in-depth understanding of the AWS ecosystem and its various services.  
2. Experience with Automation Testing Tools: The worker should have extensive experience with automation testing tools, which are crucial for maintaining the quality of software in a cloud environment.


                """,
                "output": f"{example_output}"
            }
        ]

        good_examples_prompt_template = ChatPromptTemplate.from_messages(
            [
                "{input}\n{thought_and_actions}\nOutput: {output}"
            ]
        )

        good_examples_prompt = FewShotChatMessagePromptTemplate(
            examples=good_examples,
            example_prompt=good_examples_prompt_template,
            input_variables=["input", "output"]
        )

        good_examples_prompt = good_examples_prompt.format()



        prompt_template = f"""
Given a skill field, provide the experience levels and the technical skills required for each level of experience with the skill.
There are 5 levels of experience with a skill. The ranges are as follows:
1. Limited practice with the skill
2. 1-2 years of experience
3. 3-5 years of experience
4. 6-10 years of experience
5. Over 10 years of experience
It is considered that a worker from level three has the skills of a worker from level three, two and one, and so on.
It is very important that the output is in a valid JSON format, no line breaks should be included, just like in the example's output.
Output must repeat the input skill with the experience levels and the technical skills required for each level of experience.
Output must contain the specified years of experience in each experience field.

It is essential to check the information for all the levels of experience to know the final answer.
You must search for the information for each level of experience with the skill, if the information for the level is not clear, you might need to search for more specific information.
You must also evaluate if the skills are new or if they are already included in the previous levels, and then also evaluate if the skills should be included in the output.
The skills evaluation must be done after searching for the information for each level, don't forget to check it for the last skill too.

You have access to the following tools: 
{{tools}}

Use the following format:

Input: the skill field
Thought: you should always think what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer because I checked the information for all the levels of experience
Final Answer: the final output JSON with the 5 levels of experience and the technical skills required for each level of experience

These are examples of good responses:
{good_examples_prompt}

Begin!

\nInput: {{input}}
\nThoughts: {{agent_scratchpad}}
        """

        prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "agent_scratchpad", "input"],
            template=prompt_template
        )

        tools = [TavilySearchResults(max_results=2)]

        agent = create_react_agent(self.llm, tools=tools, prompt=prompt)

        logging.basicConfig(level=logging.WARNING)

        log = ""

        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, return_intermediate_results=True)

        result = agent_executor.invoke({"input": input_skill})
        result['output'] = result['output'].replace('\n', '')

        print(result)
        return result


def remove_spaces_inside_quotes(text):
    return re.sub(r'"[^"]*"', lambda m: m.group().replace(' ', ''), text)






