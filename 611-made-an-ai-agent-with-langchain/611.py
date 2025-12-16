from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain, SimpleSequentialChain
from dotenv import load_dotenv

from prompts import description_prompt, script_prompt

# loads the .env file
load_dotenv()

# initialize the language model
llm = ChatOpenAI(model_name="gpt-3.5-turbo")

# create the chains
description_chain = LLMChain(llm=llm, prompt=description_prompt)
script_chain = LLMChain(llm=llm, prompt=script_prompt)

# create the sequential chain
tiktok_chain = SimpleSequentialChain(
    chains=[description_chain, script_chain],
    verbose=True
)

# run the chain
script = tiktok_chain.run("cats are cool")  # เปลี่ยนทัวร์เป็นบท้วดโที่ผู้ใช้เฮ็ดต้องการ

print(script)