import os
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle ,Line
from kivy.animation import Animation
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


LabelBase.register(name="NotoSans", fn_regular="fonts/NotoSansKR-Regular.otf")
fn_regular="fonts/NotoSansKR-Regular.otf"
DATA_FOLDER = "data"


class GlobalState:
    def __init__(self):
        self.data_reset() 

    def data_reset(self):
        self.current_question = 1
        self.current_page = 0
        self.exam_images = []
        self.user_answers = {i: 0 for i in range(1, 51)}
        self.selected_exam = None 

    def show_exit_popup(self, screen):
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        with content.canvas.before:
            Color(1, 1, 1, 1) 
            rect = Rectangle(pos=content.pos, size=content.size)

        content.bind(pos=lambda instance, value: setattr(rect, 'pos', value))
        content.bind(size=lambda instance, value: setattr(rect, 'size', value))

        label = Label(
            text="시험을 종료하고 홈으로 돌아가시겠습니까?",
            font_size=20,
            font_name="NotoSans",
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=50
        )

        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        popup = Popup(
            title="", 
            content=content,
            size_hint=(0.7, 0.3),
            auto_dismiss=False
        )

        yes_button = Button(
            text="예",
            font_size=18,
            font_name="NotoSans",
            background_color=(0.2, 0.6, 1, 1),
            on_press=lambda instance: self.confirm_exit(screen,popup)
        )

        no_button = Button(
            text="아니오",
            font_size=18,
            font_name="NotoSans",
            background_color=(1, 0.2, 0.2, 1),
            on_press=lambda instance: popup.dismiss()  # 팝업 닫기
        )

        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)

        content.add_widget(label)
        content.add_widget(button_layout)

        popup.open()

    def confirm_exit(self,screen,popup):
        popup.dismiss()
        self.data_reset()
        screen.manager.current = "main"
 
class MainScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.load_exam_list, 0.1)

    def load_exam_list(self, *args):
        spinner = self.ids.exam_spinner
        spinner.values = []
        if not os.path.exists(DATA_FOLDER):
            return
        exams = sorted([d for d in os.listdir(DATA_FOLDER) if os.path.isdir(os.path.join(DATA_FOLDER, d))])
        spinner.values = exams

        app = App.get_running_app()
        app.global_state.selected_exam = exams[0] if exams else None  #

    def set_selected_exam(self, exam_name):
        App.get_running_app().global_state.selected_exam = exam_name

    def start_exam(self):
        app = App.get_running_app()
        if app.global_state.selected_exam:
            exam_screen = self.manager.get_screen("exam")
            exam_screen.load_exam()
            self.manager.current = "exam"

class ExamScreen(Screen):    
    def load_exam(self):
        app = App.get_running_app()
        exam_name = app.global_state.selected_exam
        if not exam_name:
            return
        
        exam_folder = os.path.join(DATA_FOLDER, exam_name)
        app.global_state.exam_images = sorted([f for f in os.listdir(exam_folder) if f.endswith(".png")])
        
        app.global_state.current_page = 0 
        self.show_exam_page()
        self.update_question()
        self.update_answer_buttons()

    def show_exam_page(self):
        app = App.get_running_app()
        if not app.global_state.exam_images:
            return

        image_path = os.path.join(DATA_FOLDER, app.global_state.selected_exam, app.global_state.exam_images[app.global_state.current_page])
        self.ids.exam_image.source = image_path
        self.ids.exam_image.reload()
        self.ids.current_page.text = f"{app.global_state.current_page + 1} 페이지"

    def prev_page(self):
        app = App.get_running_app()
        if app.global_state.current_page > 0:
            app.global_state.current_page -= 1
            self.show_exam_page()

    def next_page(self):
        app = App.get_running_app()
        if app.global_state.current_page < len(app.global_state.exam_images) - 1:
            app.global_state.current_page += 1
            self.show_exam_page()

    def update_question(self):
        app = App.get_running_app()
        self.ids.question_number.text = f"{app.global_state.current_question}번"
    
    def edit_question(self):
        """ ✅ 문제 번호를 입력할 수 있는 팝업창 생성 """
        app = App.get_running_app()

        content = BoxLayout(orientation='vertical', spacing=10, padding=20)

        text_input = TextInput(
            text=str(app.global_state.current_question),
            font_size=20,
            font_name="NotoSans",
            multiline=False,
            input_filter='int',  # ✅ 숫자만 입력 가능
            halign="center",
            size_hint_y=None,
            height=50
        )

        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.6, 0.3),
            auto_dismiss=False,
            background_color=(1, 1, 1, 1),  # ✅ 팝업 배경 흰색
            separator_color=(1, 1, 1, 1)  # ✅ 상단 바 검은색
        )

        def go_to_question(instance):
            try:
                new_question = int(text_input.text)
                if 1 <= new_question <= 50:
                    app.global_state.current_question = new_question
                    self.update_question()
                    self.update_answer_buttons()
            except ValueError:
                pass
            popup.dismiss()

        move_button = Button(
            text="이동",
            font_size=18,
            font_name="NotoSans",
            background_color=(0.2, 0.6, 1, 1),
            on_press=go_to_question
        )

        cancel_button = Button(
            text="취소",
            font_size=18,
            font_name="NotoSans",
            background_color=(1, 0.2, 0.2, 1),
            on_press=popup.dismiss
        )

        button_layout.add_widget(move_button)
        button_layout.add_widget(cancel_button)

        content.add_widget(text_input)
        content.add_widget(button_layout)

        popup.open()

    def prev_question(self):
        app = App.get_running_app()
        if app.global_state.current_question > 1:
            app.global_state.current_question -= 1
            self.update_question()
            self.update_answer_buttons()

    def next_question(self):
        app = App.get_running_app()
        if app.global_state.current_question < 50:
            app.global_state.current_question += 1
            self.update_question()
            self.update_answer_buttons()

    def select_answer(self, answer):
        app = App.get_running_app()
        app.global_state.user_answers[app.global_state.current_question] = answer
        self.update_answer_buttons()

    def update_answer_buttons(self):
        app = App.get_running_app()
        selected_answer = app.global_state.user_answers.get(app.global_state.current_question, 0)
        for i in range(1, 5):
            btn = self.ids[f"answer_btn_{i}"]
            btn.background_color = (0.8, 0.8, 0.8, 1) if i != selected_answer else (0, 0.6, 1, 1)

    def to_home(self):
        App.get_running_app().global_state.show_exit_popup(self)

    def submit_exam(self):
        app = App.get_running_app()
        result_screen = self.manager.get_screen("result")
        result_screen.load_results()
        self.manager.current = "result"

class ResultScreen(Screen):
    def load_results(self):
        app = App.get_running_app()
        correct_answers = self.get_correct_answers()
        score = sum(2 for q, ans in app.global_state.user_answers.items() if ans == correct_answers.get(q, 0))
        self.ids.score_label.text = f"정답 개수: {score // 2} / 오답 개수: {50 - (score // 2)} / 점수: {score}점"
        
        result_table = self.ids.result_table
        result_table.clear_widgets()

        for i in range(1, 51):
            correct = correct_answers.get(i, 0)
            user = app.global_state.user_answers.get(i, 0)

            data = [
                (str(i), (0, 0, 0, 1)),  
                (str(user), (1, 0, 0, 1) if user != correct else (0, 0.6, 0, 1)),  
                (str(correct), (0, 0, 0, 1)),  
            ]

            for text, color in data:
                label = Label(
                    text=text,
                    font_size=18,
                    font_name="NotoSans",
                    size_hint_y=None,
                    height=40,
                    color=color
                )

                with label.canvas.before:
                    Color(0, 0, 0, 1)  
                    Line(points=[label.x, label.y, label.x + label.width, label.y], width=1)  # 가로선

                result_table.add_widget(label)
        result_table.height = max(40 * 50, self.height * 0.6)

    def get_correct_answers(self):
        app = App.get_running_app()
        answer_path = os.path.join(DATA_FOLDER, app.global_state.selected_exam, "answer_key.json")
        if os.path.exists(answer_path):
            with open(answer_path, "r", encoding="utf-8") as f:
                return {int(k): v for k, v in json.load(f).items()}
        return {i: 0 for i in range(1, 51)}

    def to_home(self):
        App.get_running_app().global_state.show_exit_popup(self)

    def return_to_exam(self):
        self.manager.current = "exam"

class CBTApp(App):
    def build(self):
        self.global_state = GlobalState() 
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(ExamScreen(name="exam"))
        sm.add_widget(ResultScreen(name="result"))
        return sm

if __name__ == "__main__":
    CBTApp().run()
