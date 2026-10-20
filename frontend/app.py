import requests
import streamlit as st

BASE_API = "http://127.0.0.1:8000"
CHAT_API = f"{BASE_API}/chat"
LOGIN_API = f"{BASE_API}/login"
REGISTER_API = f"{BASE_API}/register"

st.set_page_config(page_title="LegalBuddy AI", page_icon="⚖️", layout="wide")
st.title("⚖️ LegalBuddy AI Assistant")


def init_state():
    defaults = {
        "user": None,
        "messages": [],
        "sessions": [],
        "active_session_id": None,
        "auth_mode": "login",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def api_error(response):
    try:
        return response.json().get("detail", "Something went wrong.")
    except Exception:
        return "Unable to reach backend."


def load_sessions():
    if not st.session_state.user:
        return

    response = requests.get(f"{BASE_API}/history/{st.session_state.user['id']}", timeout=30)
    if response.ok:
        st.session_state.sessions = response.json().get("sessions", [])


def load_session_messages(session_id):
    user_id = st.session_state.user["id"]
    response = requests.get(f"{BASE_API}/history/{user_id}/{session_id}", timeout=30)
    if response.ok:
        st.session_state.messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in response.json().get("messages", [])
        ]
        st.session_state.active_session_id = session_id


def render_register():
    st.subheader("Create Your Account")
    with st.form("register_form"):
        name = st.text_input("Full Name")
        city = st.text_input("City / Village")
        state = st.text_input("State")
        phone = st.text_input("Mobile Number")
        email = st.text_input("Email")
        age = st.number_input("Age", min_value=1, max_value=100, value=18)
        profession = st.selectbox(
            "You are",
            ["Student / Learner", "Need Legal Help", "Lawyer"],
        )
        language = st.selectbox("Preferred Language", ["English", "Hindi"])
        password = st.text_input("Create Password", type="password")
        submitted = st.form_submit_button("Create Account")

    if submitted:
        payload = {
            "name": name.strip(),
            "city": city.strip(),
            "state": state.strip(),
            "phone": phone.strip() or None,
            "email": email.strip() or None,
            "age": age,
            "profession": profession,
            "language": language,
            "password": password,
        }
        response = requests.post(REGISTER_API, json=payload, timeout=30)
        if response.ok:
            st.success("Account created. Please log in.")
            st.session_state.auth_mode = "login"
            st.rerun()
        else:
            st.error(api_error(response))


def render_login():
    st.subheader("Login")
    with st.form("login_form"):
        identifier = st.text_input("Mobile Number or Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        response = requests.post(
            LOGIN_API,
            json={"identifier": identifier.strip(), "password": password},
            timeout=30,
        )
        if response.ok:
            data = response.json()
            st.session_state.user = data["user"]
            st.session_state.sessions = data.get("sessions", [])
            st.session_state.messages = []
            st.session_state.active_session_id = None
            st.rerun()
        else:
            st.error(api_error(response))


def render_auth():
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", use_container_width=True):
            st.session_state.auth_mode = "login"
    with col2:
        if st.button("Register", use_container_width=True):
            st.session_state.auth_mode = "register"

    if st.session_state.auth_mode == "register":
        render_register()
    else:
        render_login()


def format_answer(data):
    output = data["answer"]

    if data.get("case_type"):
        output += f"\n\n**Case Type:** {data['case_type'][0]}"
        if data.get("case_type_explanation"):
            output += f"\n{data['case_type_explanation']}"

    if data.get("recommended_lawyers"):
        output += "\n\n**Recommended Lawyer:**\n"
        for lawyer in data["recommended_lawyers"]:
            output += f"- {lawyer}\n"

    if data.get("case_insights"):
        output += "\n\n**Relevant Judgments:**\n"
        for case in data["case_insights"]:
            url = f"{BASE_API}/get_pdf?file={case['file']}&year={case['year']}"
            output += f"\n- **{case['file']} ({case['year']})**\n"
            output += f"[Open Judgment]({url})\n"

    return output


def render_sidebar():
    user = st.session_state.user
    st.sidebar.subheader("Profile")
    st.sidebar.write(f"**Name:** {user['name']}")
    st.sidebar.write(f"**Location:** {user['city']}, {user['state']}")
    st.sidebar.write(f"**Role:** {user['profession']}")

    if st.sidebar.button("New Chat", use_container_width=True):
        st.session_state.active_session_id = None
        st.session_state.messages = []
        st.rerun()

    if st.sidebar.button("Refresh History", use_container_width=True):
        load_sessions()
        st.rerun()

    st.sidebar.subheader("Chat History")
    if not st.session_state.sessions:
        st.sidebar.caption("No previous chats yet.")

    for session in st.session_state.sessions:
        label = session["title"] or f"Chat {session['id']}"
        if st.sidebar.button(label, key=f"session_{session['id']}", use_container_width=True):
            load_session_messages(session["id"])
            st.rerun()

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.sessions = []
        st.session_state.active_session_id = None
        st.rerun()


def render_chat():
    render_sidebar()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask your legal question...")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your case..."):
            response = requests.post(
                CHAT_API,
                json={
                    "query": user_input,
                    "user_id": st.session_state.user["id"],
                    "session_id": st.session_state.active_session_id,
                },
                timeout=120,
            )

            if not response.ok:
                error_message = api_error(response)
                st.error(error_message)
                return

            data = response.json()
            output = format_answer(data)
            st.markdown(output)

            st.session_state.active_session_id = data.get("session_id", st.session_state.active_session_id)
            st.session_state.messages.append({"role": "assistant", "content": output})
            load_sessions()


init_state()

if st.session_state.user:
    render_chat()
else:
    render_auth()
