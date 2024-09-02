import asyncio
import time
import random
from gemi import llm, rag_search
from typing import Dict, Any

# Define Tools/Knowledge Base
tools = {
    "node1": ['emergency', 'unrelated', 'message'],
    'node2': ['time_works', 'its_late'],
    'unrelated_check': ['unrelated', 'related']
}

async def get_input_async(prompt: str) -> str:
    return await asyncio.to_thread(input, prompt)

async def call_llm_async(prompt: str, tools: Dict[str, Any], context: str) -> Dict[str, Any]:
    return await asyncio.to_thread(llm, prompt, tools, context)

async def unrelated_message():
    return  print("AI: I don’t understand that and repeat the question/statement")
    

async def closing_node():
    print("AI: Dr. Adrin will be with you shortly.")

async def node2A():
    # Emergency Node
    emergency_ask = await get_input_async("AI: Please describe the emergency you're experiencing.\nUser: ")
    print("----------")
    user_relevancy = await call_llm_async(emergency_ask, tools['unrelated_check'],
                                          "and we have asked user to describe emergency they are facing, check it user response is related to question asked or not")
    

    while user_relevancy['response'] == "unrelated":
        await unrelated_message()
        emergency_ask = await get_input_async("Please describe the emergency you're experiencing.\nUser: ")
        print("----------")
        user_relevancy = await call_llm_async(emergency_ask, tools['unrelated_check'],
                                              "and we have asked user to describe emergency they are facing, check it user response is related to question asked or not")

    print("AI: I am checking what you should do immediately. Meanwhile, can you tell me which area you are located in right now?")
    user_location = await get_input_async("User: ")
    print("----------")
    start_time = time.time()

    doctor_toa = random.randint(5, 60)  
    print(f"Dr. Adrin will be coming to your location immediately. Estimated time of arrival is {doctor_toa} minutes.")
    user_response = await get_input_async("User: ")
    print("----------")

    response_understanding = await call_llm_async(user_response, tools['node2'],
                                                  "Check if the user finds the doctor's arrival time late or not.")
   
    end_time = time.time()
    duration = end_time - start_time

    if duration < 15:
        print("AI: Please hold, just a sec")

        if response_understanding['response'] == "its_late":
            emergency_action = rag_search(emergency_ask + " its being late")
        else:
            emergency_action = rag_search(emergency_ask)
        await asyncio.sleep(15 - duration) 
    else:
        if response_understanding['response'] == "its_late":
            emergency_action = rag_search(emergency_ask + " its being late")
        else:
            emergency_action = rag_search(emergency_ask)

    if len(emergency_action)>0:
        print(emergency_action)
        print("Don’t worry, please follow these steps, ")
print("----------")
    await closing_node()


async def node2B():
    message = await get_input_async("AI: What message do you want to forward to Dr. Adrin?\n")
    print("----------")
    print("Thanks for the message, we will forward it to Dr. Adrin")
    

async def node1(unrelated: bool = False):
    if unrelated:
        ask_user1 = await get_input_async("AI: I don’t understand that. Are you experiencing an emergency or would you like to leave a message?\nUser: ")
    else:
        ask_user1 = await get_input_async("AI: Hello, are you experiencing an emergency, or would you like to leave a message for Dr. Adrin?\nUser: ")
    print("----------")
    # Use LLM to determine user intent
    node1_result = await call_llm_async(ask_user1, tools['node1'],
                                        "and check what does user is asking about is it emergency, or some message for doctor, or something unrelated")
    
    if node1_result['response'] == "emergency":
        await node2A()
    elif node1_result['response'] == "message":
        await node2B()
    else:
        await node1(unrelated=True)

async def main():
    print("######   AI RECEPTIONIST   #####")
    print()
    await node1()


if __name__ == "__main__":
    asyncio.run(main())
