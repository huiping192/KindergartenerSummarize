from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains.mapreduce import MapReduceChain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.llms import Ollama

class KindergartenSummarizer:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        # self.llm = Ollama(base_url="http://localhost:11435",model="mistral")
        self.prompt_template = """
Summarize the daily activities of a kindergartener based on the content of the daily communication emails IN japanese. Also, highlight any points that require special attention.
CONCISE SUMMARY ONLY IN japanese.

Suggestions:

1.Include details about the child's academic activities, such as what they learned or any homework they have.
2.Mention any special events or activities that took place, such as field trips or celebrations.
3.Highlight any behavioral observations or concerns brought up in the emails.
4.Split info by date and Summarize things from the same day and dont repeat date
5. no need useless info

format like:

date and week: (example: 2023-10-30 月曜日)

今日やったこと
 -  list of child activities in  kindergarten
お知らせ
 - list of other infos

date and week: (example: 2023-10-31 火曜日)

今日やったこと
 -  list of child activities in  kindergarten
お知らせ
 - list of other infos



------
{text}
 ----
"""

    def summarize_emails(self, email_bodies):
        docs = [Document(page_content=t) for t in email_bodies]
        prompt = PromptTemplate(template=self.prompt_template, input_variables=["text"])
        chain = load_summarize_chain(self.llm, chain_type="stuff", prompt=prompt, verbose=True)
        return chain.run(docs)