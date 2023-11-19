import os
import json
from .session import ChatSession

if __name__ == "__main__":
    history_path = "new_history.json"
    history = None
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            history = json.load(f)

    application = ChatSession(history=history)
    # short, long = application.summarize()
    # print(short, long)
    
    print(application.welcome())
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            # Get history
            new_history = application.end_conversation()
            with open(history_path, "w") as f:
                json.dump(new_history, f)

            exit()        
            
        print("AI: ", end="")
        # Streaming
        response = application.chat(user_input, streaming=True)
        for token in response:
            print(token, end="", flush=True)
        print()
        
        # # No streaming
        # response = application.chat(user_input, streaming=False)
        # print(response)
        
