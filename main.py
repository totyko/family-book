import os
from datetime import datetime
import pytz
from supabase import create_client
from dotenv import load_dotenv
from fasthtml.common import *

# load env varibales

load_dotenv()

#initialize supabase client 
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
app, rt = fast_app(live=False)


NAME_MAX = 15
MESSAGE_MAX = 50
TIMESTAMP_FMT = "%m-%d-%Y %I:%M:%S EDT"

def get_edt_time():
    edt_tz = pytz.timezone("EST5EDT")
    return datetime.now(edt_tz)

def add_message(name, message):
    timestamp = get_edt_time().strftime(TIMESTAMP_FMT)
    supabase.table("Family").insert(
        {"name": name, "message": message, "timestamp": timestamp}
    ).execute()

def get_messages():
    response = (
        supabase.table("Family").select("*").order("id", desc=True).execute()
    )
    return response.data

def render_message(entry):
    return (
          Article(
            Header(f"Name: {entry['name']}"),
            P(f"Message: {entry['message']}"),
            Footer(Small(Em(f"Posted: {entry['timestamp']}"))),
        )
    )

def render_message_list():
        messages = get_messages()


        return Div(
                *[render_message(entry) for entry in messages],
                id="message-list",
            )

def render_content():
    form = Form(
        Fieldset(
            Input(
            type="text", 
            name="name",
            placeholder="Name",
            maxlength=NAME_MAX,
            required=True,
        ),

            Input(
            type="text", 
            name="message",
            placeholder="Message",
            maxlength=MESSAGE_MAX,
            required=True,
        ),
            
            Button("Add", type="submit"),
            role="group",
        ),
        method="post",
        hx_post="/submit-message",
        hx_target="#message-list",
        hx_swap="outerHTML",
        hx_on__after_request="this.reset()"

    )
    return Div(
        P(Em("Write you  Name and Message")),
        form,
        P("Thank You"),
        Div("Made by JC."),
    
        Hr(),
        render_message_list(),
        cls="container",

    )


@rt("/")
def home():
    return Titled("Family 📖"), render_content()


@rt("/submit-message", methods=["POST"])
def post(name: str, message: str):
    add_message(name, message)
    return render_message_list()

serve()