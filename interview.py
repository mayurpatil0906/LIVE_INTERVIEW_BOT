from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime
import csv

app = Flask(__name__)

# Define questions for different roles
questions = {
    "java_developer": {
        "mcq": [
            {"question": "What is the default value of a boolean in Java?", "options": ["true", "false", "null", "undefined"]},
            {"question": "What is JVM in Java?", "options": ["Java Virtual Machine", "Java Verified Mode", "Java Vendor Model", "Java Visual Monitor"]},
        ],
        "qa": [
            "Explain the concept of inheritance in Java.",
            "What are the key features of Java 8?"
        ]
    },
    "mern_stack_developer": {
        "mcq": [
            {"question": "What does MERN stand for?", "options": ["MongoDB, Express, React, Node", "MySQL, Express, Ruby, Node", "MongoDB, EJS, Redux, Node", "MongoDB, Express, React Native, Node"]},
            {"question": "Which of the following is used for server-side programming in MERN?", "options": ["MongoDB", "Express", "React", "Redux"]},
        ],
        "qa": [
            "Explain the structure of a MERN stack application.",
            "How does Node.js handle asynchronous operations?"
        ]
    },
    "full_stack_developer": {
        "mcq": [
            {"question": "Which language is primarily used for styling web pages?", "options": ["JavaScript", "CSS", "Python", "SQL"]},
            {"question": "Which framework is commonly used with Node.js for web development?", "options": ["Flask", "Django", "Express", "Laravel"]},
        ],
        "qa": [
            "Explain the difference between front-end and back-end development.",
            "What are the pros and cons of using React over Angular?"
        ]
    },
    "aiml_developer": {
        "mcq": [
            {"question": "What is the purpose of a neural network?", "options": ["Data storage", "Image processing", "Learning from data", "Hardware acceleration"]},
            {"question": "Which language is most commonly used in AI/ML development?", "options": ["Python", "JavaScript", "C++", "Java"]},
        ],
        "qa": [
            "What is supervised learning in machine learning?",
            "Explain the concept of a decision tree."
        ]
    }
}

# Function to log answers in CSV format
def log_answer(name, email, college, role, question_type, question, answer):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists("answers.csv")
    with open("answers.csv", "a", newline='') as csvfile:
        fieldnames = ["Timestamp", "Name", "Email", "College", "Role", "Question Type", "Question", "Answer"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "Timestamp": timestamp,
            "Name": name,
            "Email": email,
            "College": college,
            "Role": role,
            "Question Type": question_type,
            "Question": question,
            "Answer": answer
        })

# Route for the main page
@app.route('/')
def contact():
    return render_template('start.html') 



# Route for the Contact page
@app.route('/contact')
def default():
    return render_template('contact.html')  # Ensure contact.html is in the templates folder


# Route for form page to collect user info
@app.route('/start', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        # Get the form data
        name = request.form['name']
        email = request.form['email']
        college = request.form['college']
        role = request.form['role']  # New field for role selection

        # Redirect to the MCQ round page with the user's details
        return redirect(url_for('mcq_round', name=name, email=email, college=college, role=role, question_num=0))
    
    return render_template('start.html')

# Route for MCQ round
@app.route('/mcq_round', methods=['GET', 'POST'])
def mcq_round():
    # Get the user data from the URL parameters
    name = request.args.get('name')
    email = request.args.get('email')
    college = request.args.get('college')
    role = request.args.get('role')

    if not name or not email or not college or not role:
        return redirect(url_for('start'))

    # Load MCQ questions based on the selected role
    role_questions = questions.get(role, {})
    mcq_questions = role_questions.get("mcq", [])

    # Get the current question number from the URL
    question_num = int(request.args.get('question_num', 0))
    
    if request.method == 'POST':
        selected_answer = request.form['answer']
        log_answer(name, email, college, role, "MCQ", mcq_questions[question_num]['question'], selected_answer)
        
        if question_num + 1 < len(mcq_questions):
            return redirect(url_for('mcq_round', name=name, email=email, college=college, role=role, question_num=question_num + 1))
        else:
            return redirect(url_for('qa_round', name=name, email=email, college=college, role=role, question_num=0))

    question = mcq_questions[question_num]
    return render_template('mcq_round.html', question=question, question_num=question_num, name=name, email=email, college=college, role=role)
# Route for Q&A round
@app.route('/qa_round', methods=['GET', 'POST'])
def qa_round():
    # Get user data from URL parameters
    name = request.args.get('name')
    email = request.args.get('email')
    college = request.args.get('college')
    role = request.args.get('role')

    # Redirect to start if required data is missing
    if not name or not email or not college or not role:
        return redirect(url_for('start'))

    # Load Q&A questions based on the selected role
    role_questions = questions.get(role, {})
    qa_questions = role_questions.get("qa", [])

    # Get the current question number (default to 0 if not provided)
    question_num = int(request.args.get('question_num', 0))

    # Handle form submission for the current Q&A question
    if request.method == 'POST':
        answer = request.form['answer']  # Get the answer from the form
        # Log the answer
        log_answer(name, email, college, role, "Q&A", qa_questions[question_num], answer)

        # Move to the next question or end the interview if it was the last question
        if question_num + 1 < len(qa_questions):
            # Move to the next question
            return redirect(url_for('qa_round', name=name, email=email, college=college, role=role, question_num=question_num + 1))
        else:
            # All questions completed
            return render_template('end.html', name=name, email=email, college=college, role=role)

    # Render the current question
    question = qa_questions[question_num]
    return render_template('qa_round.html', question=question, question_num=question_num, name=name, email=email, college=college, role=role)
    

@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve user data and question number from the form
    name = request.form['name']
    email = request.form['email']
    college = request.form['college']
    role = request.form['role']  # 'role' is now passed from the form
    question_num = int(request.form['question_num'])  # Current question number
    answer = request.form['answer']  # The submitted answer

    # Retrieve the question based on the role and question number
    question = questions[role]["qa"][question_num]

    # Log the answer in the CSV file
    log_answer(name, email, college, role, "Q&A", question, answer)

    # Check if more questions are left
    if question_num + 1 < len(questions[role]["qa"]):
        # Redirect to next question
        return redirect(url_for('qa_round', name=name, email=email, college=college, role=role, question_num=question_num + 1))
    else:
        # Redirect to end page if it's the last question
        return redirect(url_for('end'))

# Route for interview completion page
@app.route('/end')
def end():
    return render_template('end.html')

if __name__ == '__main__':
    app.run(debug=True)
