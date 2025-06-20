import google.generativeai as genai
import os
import json
import sqlite3

genai.configure(api_key=os.environ["API_KEY"])

con = sqlite3.connect("memory.db")
cursor = con.cursor()

debug = True

model = genai.GenerativeModel('gemini-2.0-flash')

def generate_response(prompt, useful_info):
    if(debug):
        print("useful info ", useful_info)

    response = model.generate_content(
        f'''You are a personal assistant.
        A user sends a prompt below.
        Extract what you think that is important to store in a database so you can retrieve it in future prompts.
        Return it in JSON format, put these informations in the key "storeInfo", and the actual response in "finalResponse". Attention: If you think no useful information can be extracted, return an empty JSON object.
        Example: "userName": "John", "userAge": 30

        Doesn't store user_query. Also, if a useful_info is listed below, ignore it.

        Here is useful information extracted from past chats: {useful_info}

        Prompt: {prompt}''',
        generation_config={"response_mime_type": "application/json"}
    )
    rawResponse = json.loads(response.text)

    if debug:
        print("Raw response: ", rawResponse)
    info = rawResponse['storeInfo']

    if len(info.items()) > 0:
        info_array = [{"header": key, "value": value} for key, value in info.items()]
        info_string = ", ".join([f"('{item['header']}', '{item['value']}')" for item in info_array])
        cursor.execute(f"INSERT INTO memory (header, value) VALUES {info_string}")
        con.commit()


    return rawResponse['finalResponse']

def get_useful_info(prompt):
    infosRaw = cursor.execute("SELECT * FROM memory")
    infos = infosRaw.fetchall()
    headers = [info[1] for info in infos]


    if debug:
        print ("Headers: ", headers)

    response = model.generate_content(
        f'''You are a personal assistant. A user sends a prompt below.

        Prompt: {prompt}

        Your task is to, given some strings, you select the ones that you think that may be useful to retrieve from a memory database so the response is personalized for the user.
        If you think no information is useful, return an empty JSON object.

        Return a JSON containing an array called "data" with the texts you want to retrieve.

        Here are the possible informations you can retrieve:

        {", ".join(headers)}
        ''',
        generation_config={"response_mime_type": "application/json"}
    )
    retrives = json.loads(response.text)['data']

    if debug:
        print("Retrieves: ", retrives)

    #
    retrieve_data = [info for info in infos if info[1] in retrives]

    if debug:
        print("Retrieve data: ", retrieve_data)

    # extract values from retrieve_data and join it in a string like "key: value; key: value"
    values = "; ".join([f"{info[1]}: {info[2]}" for info in retrieve_data])

    if debug:
        print(retrieve_data)

    if debug:
        print("Values: ", values)

    return values

cursor.execute("CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, header TEXT, value TEXT)")
while True:
    prompt = input("Enter your prompt: ")
    useful_info = get_useful_info(prompt)
    response = generate_response(prompt, useful_info)
    print("Response: ", response)
