from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QCheckBox, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtCore import QTimer
import os
import random
def list_png_files(directory, file_ending):
    """ List all files in a directory that match a specific ending pattern. """
    return [f for f in os.listdir(directory) if f.endswith(file_ending)]

def match_questions_answers(questions, answers):
    """ Match questions with their corresponding answers based on filenames. """
    matched_pairs = {}
    for question in questions:
        base_name = question.replace(" Question.png", "")
        answer_key = base_name + " KEY.png"
        if answer_key in answers:
            matched_pairs[question] = answer_key
    return matched_pairs

class LSATStudyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.user_assessment = {}
        self.question_folder = ""
        self.answer_folder = ""
        self.matched_pairs = {}
        self.current_question = None
        self.initUI()
        self.remaining_questions = []
        self.total_questions_answered = 0
        self.total_correct_answers = 0
        self.incorrect_questions = []

    def initUI(self):
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('LSAT Study Tool')

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Drag and Drop Your Question Folders Here")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.img_label = QLabel(self)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.img_label)

        self.answer_button = QPushButton("Show Answer", self)
        self.answer_button.clicked.connect(self.show_answer)
        self.layout.addWidget(self.answer_button)

        self.next_button = QPushButton("Next Question", self)
        self.next_button.clicked.connect(self.next_question)

        self.layout.addWidget(self.next_button)

        self.correct_checkbox = QCheckBox("I got this correct", self)
        self.layout.addWidget(self.correct_checkbox)
        
        # Button to submit the user's assessment
        self.submit_button = QPushButton("Submit Assessment", self)
        self.submit_button.clicked.connect(self.submit_assessment)
        self.layout.addWidget(self.submit_button)
        self.setAcceptDrops(True)

        self.timer_label = QLabel("00:00", self)  # Starting time
        self.layout.addWidget(self.timer_label)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer_interval = 1000  # Timer updates every 1000 milliseconds (1 second)
        self.time_spent = 0  # Time per question in seconds


    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            folder_path = url.toLocalFile().rstrip(' /')
            folder_path = url.toLocalFile()
            print(f"Dropped folder path: {folder_path}")  # Debug
            if not self.question_folder:
                self.question_folder = folder_path
                self.label.setText("Question Folder Loaded. Drop Answer Folder.")
            elif not self.answer_folder:
                self.answer_folder = folder_path
                self.label.setText("Answer Folder Loaded. Click 'Next Question' to Start.")
                self.load_questions_answers()

    def submit_assessment(self):
        # Get the user's assessment
        is_correct = self.correct_checkbox.isChecked()
        # Record the assessment for the current question
        self.record_assessment(self.current_question, is_correct)
        self.total_questions_answered += 1
        if is_correct:
            self.total_correct_answers += 1
        else:
            self.incorrect_questions.append(self.current_question)
        self.update_percentage_display()
        self.next_question()
    
    def record_assessment(self, question, is_correct):
        self.user_assessment[question] = is_correct
        print(f"Recorded assessment for {question}: {'Correct' if is_correct else 'Incorrect'}")

    def load_questions_answers(self):
        questions = list_png_files(self.question_folder, " Question.png")
        answers = list_png_files(self.answer_folder, " KEY.png")
        self.matched_pairs = match_questions_answers(questions, answers)
        self.remaining_questions = list(self.matched_pairs.keys())
        print(f"Loaded {len(self.matched_pairs)} question-answer pairs.")
        self.next_question()

    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(900, 660, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_label.setPixmap(pixmap)

    def show_answer(self):
        if self.current_question:
            answer_file = self.matched_pairs[self.current_question]
            answer_path = os.path.join(self.answer_folder, answer_file)
            print(f"Displaying answer: {answer_file}")
            self.display_image(answer_path)

    def next_question(self):
        if self.remaining_questions:
            # Randomly select a question from the remaining questions
            self.current_question = random.choice(self.remaining_questions)
            question_path = os.path.join(self.question_folder, self.current_question)
            print(f"Displaying question: {self.current_question}")
            self.display_image(question_path)
            # Remove the selected question from the list of remaining questions

            self.time_spent = 0  # Reset the time for the new question
            self.timer_label.setText("00:00")  # Reset the timer label
            self.timer.start(self.timer_interval)  # Start the timer

        else:
            print("No more questions left.")
            # Here you can disable the next_question button or indicate the end of the session
            self.next_button.setEnabled(False)
            self.submit_button.setEnabled(False)
            # Maybe call a function to show the results or summary here
            self.show_summary()

    def update_percentage_display(self):
        # Calculate the running percentage of correct answers
        if self.total_questions_answered > 0:
            correct_percentage = (self.total_correct_answers / self.total_questions_answered) * 100
        else:
            correct_percentage = 0
        # Update the display with the new percentage
        self.label.setText(f"Correct Answers: {correct_percentage:.2f}%")

    def show_summary(self):
        # Calculate the percentage of incorrect answers
        incorrect_percentage = 100 - (self.total_correct_answers / self.total_questions_answered) * 100
        # Display the summary of incorrect questions and the percentage
        summary_message = f"You answered {incorrect_percentage:.2f}% of questions incorrectly.\n"
        summary_message += "Questions answered incorrectly:\n" + "\n".join(self.incorrect_questions)
        print(summary_message)  # Change this to display in the GUI, such as in a QMessageBox

    def update_timer(self):
        # This method is called every second
        self.time_spent+= 1
        minutes = self.time_spent // 60
        seconds = self.time_spent % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
            
    

# Main application
app = QApplication([])
window = LSATStudyApp()
window.show()
app.exec_()

