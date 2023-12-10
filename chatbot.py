import torch

import speech_recognition as sr
#import pyttsx3

import cozmo

# import from Huggingface
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config
from transformers import get_linear_schedule_with_warmup

#Model from: https://huggingface.co/microsoft/DialoGPT-large

gpt2_large_config = GPT2Config(m_ctx=1024, n_embd=1280, n_layer=36, n_head=20)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2", padding_side='left')
model = GPT2LMHeadModel(gpt2_large_config)
model.load_state_dict(torch.load("large_ft.pkl"), strict=False)

def cozmo_program(robot: cozmo.robot.Robot):
    first_round = True
    r = sr.Recognizer()
    robot.say_text("I'm ready to talk")
    while True:    
        #encode the new user input, add the eos_token and return a tensor in Pytorch
        #Uncomment below to run chatbot through terminal:
        #user = input("You:")
        
        #NOTE: For the speech-to-text, you need to talk louder than what feels normal and
        #make sure to articulate clearly or it can't understand you.
        #Initialize the recognizer 
        #Use the microphone as source for input.
        try:
            with sr.Microphone() as source2: 
                #Wait for a second to let the recognizer
                #adjust the energy threshold based on
                #the surrounding noise level                         
                r.adjust_for_ambient_noise(source2, duration=0.2)
                #Listens for the user's input 
                audio2 = r.listen(source2)
            
                #Using google to recognize audio
                print("--Loop has restarted--")
                MyText = r.recognize_google(audio2, language='en-US')
                user = MyText.lower()
            
                print("Heard: ", MyText)
                
                if user == "goodbye":
                    robot.say_text("Goodbye").wait_for_completed()
                    break    
                user_input = tokenizer.encode(user + tokenizer.eos_token, return_tensors='pt')
                #create chat history
                if first_round == False:
                    bot_input_ids = torch.cat([chat_history_ids, user_input], dim=-1)
                else:
                    bot_input_ids = user_input
                    
                #generate a response 
                chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)
                    
                #Uncomment following for chatbot to respond via terminal:
                print("Bot: ", tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True))
                        
                #For cozmo to say response:
                response = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
                robot.say_text(response).wait_for_completed()
                if first_round == True:
                    first_round == False                
        except sr.UnknownValueError:
            robot.say_text("Can you repeat that")
    

cozmo.run_program(cozmo_program, use_viewer=False, force_viewer_on_top=False)