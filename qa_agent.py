from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import SystemMessage
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
import streamlit as st
from langchain.agents.agent_toolkits import create_retriever_tool, create_conversational_retrieval_agent


class QAManager:
    agent_executor = None
    chain = None
    embeddings = None
    docsearch = None

    def configure(self):
        # read data from the file and put them into a variable called raw_text
        loader = TextLoader("./content.txt")
        documents = loader.load()
        text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        docs = text_splitter.split_documents(documents)

        # Download embeddings from OpenAI
        self.embeddings = OpenAIEmbeddings()

        self.docsearch = FAISS.from_documents(docs, self.embeddings)

        retriever = self.docsearch.as_retriever()
        tool = create_retriever_tool(
            retriever,
            "search_child_activities",
            "Searches and returns documents regarding the child activities and information in the kindergarten."
        )
        tools = [tool]
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)

        system_message = SystemMessage(
            content=(
                "Do your best to answer the questions. "
                "Feel free to use any tools available to look up "
                "relevant information, only if necessary"
            )
        )
        self.agent_executor = create_conversational_retrieval_agent(llm, tools, system_message=system_message,
                                                                    verbose=True)

    def run(self, query):
        answer = self.agent_executor({"input": query})
        return answer["output"]


if 'qa_manager' not in st.session_state:
    st.session_state.qa_manager = QAManager()
    st.session_state.qa_manager.configure()

# 初始化会话状态，用于存储聊天历史
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 聊天UI
st.title("子供幼稚園QA")

# 输入框
user_input = st.text_input("質問を入力してください", key="input")

if st.button("submit"):
    # 验证输入
    if not user_input.strip():
        st.error("Please enter text.")
    else:
        st.session_state.chat_history.append(f"You: {user_input}")
        try:
            with st.spinner("Please wait..."):
                answer = st.session_state.qa_manager.run(user_input)
                # 更新聊天历史
                st.session_state.chat_history.append(f"AI: {answer}")
        except Exception as e:
            st.exception(f"Exception: {e}")

# 显示聊天历史
for message in st.session_state.chat_history:
    st.text(message)
