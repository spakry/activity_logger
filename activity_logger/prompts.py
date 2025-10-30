BASE_ACTIVITY_PROMPT = """
Analyze this screenshot and describe the high-level action being performed.
Answer briefly in one concise sentence. Focus on the high level action being performed, below are some examples:
It is important to keep the length of the response to a maximum of one concise sentence. 
Adding the product (enter product name and price) to the cart.
Sending payment to the Chase bank credit card account ending in 1234.
Entering terminal command <terminal command>
Executed the terminal command <terminal command>
Submit a ticket to (recipient here) for (purpose here)
Made a reservation to (location here) for (date and time here) for (cost here) 
Provide context on where the action is performed, what the action is.
Do not mention screenshot in the response, structure the logs as if it were server logs. 

If the user is entering a specific semanticly important command like in a CLI, make sure to log the command in full so that the user can reference it later. 
Whenever a specific semantic is important, make sure to log that semantically important text in full so that the user can reference it later. 

I want you to categorize the action into one of the following categories:
Communication, Coding, Writing, File Management, Calendar, Creative, Data_analysis, Finance, Shopping, Admin, Social, Media, Security, Learning
I want you to add the category tag to each log. Examples are below. 

The following log is not desirable:
[2025-10-16 21:22:22] The action being performed is running a command in a terminal to install a Python package using `pip install -e .`, while also inquiring about an error message that has occurred during the installation process.
because it does not specify which package is being installed. It also mentions an error message that has occurred during the installation process, without specifying what the error message is.
If information to determine which error message is being referred to is not available, do not mention it.

The following log is desirable:
[2025-10-16 21:22:22] [Coding] Running a command in a terminal to install a Python package using `pip install -e .`.
because it specifies which package is being installed. It also does not mention an error message that has occurred during the installation process, without specifying what the error message is.
If information to determine which error message is being referred to is not available, do not mention it.
"""


def build_activity_prompt(app_name=None, window_title=None):
    prefix = ""
    if app_name or window_title:
        prefix = f"Context: app={app_name or ''} title={window_title or ''}\n\n"
    return prefix + BASE_ACTIVITY_PROMPT


