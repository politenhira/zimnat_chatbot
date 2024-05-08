import os
import aiofiles
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
import pickle
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import UnstructuredFileLoader
from dotenv import load_dotenv

load_dotenv()


class Chatbot:
    _template = """Given the following conversation and a follow-up question, rephrase the follow-up question to be a stand-alone question.
    You can assume that the question is about the information in a file.
    Chat History:
    {chat_history}
    Follow-up entry: {question}
    Standalone question:"""


    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

    qa_template = """"You are an AI customer assistant to answer questions based on information from a given file. 
    You are an virtual customer assistant for Zimnat. Your name is Suki, you are smart and intelligent. Your goal is 
    assist customers with the information they are looking for. Your task is respond to 
    the question politely as you are representing Zimnat. The customer may ask their account 
    information there and there, please furnish them with the information in their account details. The information 
    about their account details include their policy number, type of policy, address and account balance, 
    this information is in this context.Ensure that you do not display customer information unless it is specifically requested.
    If you don't have the answer to the question asked, please provide the user with the contact 
    details. Please do not say information is not available in the given data. In your responses do not ever mention 
    that your are getting the context information from a file. During your conversation, you can use emojis where appropriate to improve user experience
    question: {question}
    =========
    {context}
    ======= 
     """

    QA_PROMPT = PromptTemplate(template=qa_template, input_variables=["question", "context"])

    def __init__(self, model_name, temperature, vectors):
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors

    async def conversational_chat(self, query, account_details):
        """
        Starts a conversational chat with a model via Langchain
        """
        chat_history = []
        chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(model_name=self.model_name, temperature=self.temperature),
            condense_question_prompt=self.CONDENSE_QUESTION_PROMPT,
            qa_prompt=self.QA_PROMPT,
            retriever=self.vectors.as_retriever(),
        )
        # question = "The customer asks " + str(query) + ". If the customer requires their account information, respond with '" + str(account_details) + "'. Otherwise, provide assistance with the information they are seeking. Ensure that you do not display customer information unless it is specifically requested, retrieve only what's required at the moment."
        result = chain({"question": query, "chat_history": chat_history})
        chat_history.append((result["question"], result["answer"]))
        return result["answer"]


class Embedder:
    def __init__(self, vectorpath):
        self.PATH = vectorpath
        self.createEmbeddingsDir()

    def createEmbeddingsDir(self):
        """
        Creates a directory to store the embeddings vectors
        """
        if not os.path.exists(self.PATH):
            os.mkdir(self.PATH)

    async def storeDocEmbeds(self, filepath, filename):
        """
        Stores document embeddings using Langchain and FAISS
        """
        # Load the data from the file using Langchain
        loader = UnstructuredFileLoader(file_path=filepath)
        data = loader.load_and_split()
        # Create an embeddings object using Langchain
        embeddings = OpenAIEmbeddings()
        # Store the embeddings vectors using FAISS
        vectors = FAISS.from_documents(data, embeddings)
        # Save the vectors to a pickle file
        async with aiofiles.open(f"{self.PATH}/{filename}.pkl", "wb") as f:
            await f.write(pickle.dumps(vectors))

        return vectors

    async def getDocEmbeds(self, filepath, filename):
        """
        Retrieves document embeddings
        """
        if not os.path.isfile(f"{self.PATH}/{filename}.pkl"):
            vectors = await self.storeDocEmbeds(filepath, filename)
        else:
            async with aiofiles.open(f"{self.PATH}/{filename}.pkl", "rb") as f:
                vectors = pickle.loads(await f.read())
        return vectors


class Utility:
    def __init__(self, filepath, vectorpath, filename, query, account_details):
        self.filepath = filepath
        self.vectorpath = vectorpath
        self.filename = filename
        self.query = query
        self.account_details = account_details

    async def setup_chatbot(self):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """
        embeds = Embedder(self.vectorpath)
        vectors = await embeds.getDocEmbeds(self.filepath, self.filename)
        chatbot = Chatbot('gpt-3.5-turbo', 0.7, vectors)
        return chatbot

    async def answer(self):
        try:
            chatbot = await self.setup_chatbot()
            response = await chatbot.conversational_chat(self.query, self.account_details)
            return response

        except Exception as e:
            print(e.args[0])
            return "An error occurred while processing the request"
