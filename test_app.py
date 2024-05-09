import streamlit as st
import sqlite3
import requests

conn = sqlite3.connect('credentials.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT
            )''')
conn.commit()

st.sidebar.title("ComposeNow")
st.sidebar.write("Instant Creation, Seamless Communication")

st.sidebar.markdown("# Help")
st.sidebar.write("If you need any assistance or have questions, please reach out to our support team at composenow@gmail.com.")
st.sidebar.markdown("# Privacy")
st.sidebar.write("Your privacy is important to us. Here are some key points:")
st.sidebar.write("- We do not collect or store any personal data.")
st.sidebar.write("- The content you generate using the Automatic Email Generator is not stored or shared with any third parties.")
st.sidebar.write("- We employ industry-standard security measures to protect your information.")
st.sidebar.write("- For more information, please review our [Privacy Policy](https://www.example.com/privacy).")

st.title("ComposeNow")
st.header("Instant Creation, Seamless Communication")
st.markdown("Generate professional emails with ease.")
st.markdown("Save time and effort in crafting emails.")
st.markdown("Get instant email suggestions and drafts.")

if 'sign_up_info' not in st.session_state:
    st.session_state['sign_up_info'] = {}

if 'is_signed_up' not in st.session_state:
    st.title("Sign Up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

    if st.button("Sign Up", key="signup_button"):
        if password == confirm_password:
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            existing_user = c.fetchone()
            if existing_user:
                st.error("Email already exists. Please use a different email.")
            else:
                c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
                conn.commit()
                st.session_state['sign_up_info']['email'] = email
                st.session_state['sign_up_info']['password'] = password
                st.session_state['is_signed_up'] = True
                st.success("Sign up successful! Please proceed to login.")
        else:
            st.error("Passwords do not match!")

if 'is_signed_up' in st.session_state and not st.session_state.get('is_logged_in', False):
    st.title("Log In")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log In", key="login_button"):
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        if user and user[1] == password:
            st.session_state['is_logged_in'] = True
            st.success("Login successful! You can now generate emails.")
        else:
            st.error("Invalid email or password!")

if not st.session_state.get('is_logged_in', False):
    st.title("Direct Login (Existing Users)")
    c.execute("SELECT email FROM users")
    emails = [row[0] for row in c.fetchall()]
    existing_email = st.selectbox("Select your email", options=emails, key="direct_login_email")
    existing_password = st.text_input("Password", type="password", key="direct_login_password")

    if st.button("Log In (Existing User)", key="direct_login_button"):
        c.execute("SELECT * FROM users WHERE email=?", (existing_email,))
        user = c.fetchone()
        if user and user[1] == existing_password:
            st.session_state['is_logged_in'] = True
            st.success("Login successful! You can now generate emails.")
        else:
            st.error("Invalid email or password!")

if st.session_state.get('is_logged_in', False):
    st.title("Generate Email")

    # Input fields
    prompt = st.text_area("Email Prompt", "Write an email for sick leave from office")
    token_count = st.slider("Token Count", min_value=50, max_value=1000, value=500)
    temperature = st.slider("Temperature", min_value=0.1, max_value=1.0, value=0.6, step=0.1)
    n_gen = st.number_input("Number of Emails to Generate", min_value=1, max_value=10, value=2, step=1)
    keywords = st.text_input("Keywords (comma-separated)", "office, sick, leave").split(",")

    # Button to generate emails
    if st.button("Generate Emails"):
        # Prepare data for API request
        data = {
            "prompt": prompt,
            "token_count": token_count,
            "temperature": temperature,
            "n_gen": n_gen,
            "keywords": keywords
        }

        # Make API request
        response = requests.post('http://a682-35-233-156-194.ngrok-free.app/generate', json=data)

        # Check if request was successful
        if response.status_code == 200:
            # Display generated emails
            generated_emails = response.json().get('ai_results', [])
            st.header("Generated Emails:")
            for i, email in enumerate(generated_emails):
                st.subheader(f"Email {i+1}:")
                st.write(email['generated_text'])
        else:
            st.error(f"Error: {response.status_code} - {response.reason}")

conn.close()