import os
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle

LabelBase.register(name="NotoSans", fn_regular="fonts/NotoSansKR-Regular.otf")

DATA_FOLDER = "data"

class MainScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.load_exam_list, 0.1)

    def load_exam_list(self, *args):
        """ 시험 회차 리스트를 드롭다운(Spinner)으로 표시 """
        spinner = self.ids.exam_spinner
        spinner.values = []
        if not os.path.exists(DATA_FOLDER):
            return
        exams = sorted([d for d in os.listdir(DATA_FOLDER) if os.path.isdir(os.path.join(DATA_FOLDER, d))])
        spinner.values = exams
        self.selected_exam = exams[0] if exams else None

    def set_selected_exam(self, exam_name):
        """ 선택한 회차 저장 """
        self.selected_exam = exam_name

    def start_exam(self):
        """ 시험 시작 버튼 클릭 시 선택된 회차의 시험 페이지로 이동 """
        if self.selected_exam:
            exam_screen = self.manager.get_screen("exam")
            exam_screen.load_exam(self.selected_exam)
            self.manager.current = "exam"

class ExamScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_question = 1
        self.current_page = 0  # ✅ 현재 시험지 페이지
        self.exam_images = []  # ✅ 시험지 이미지 리스트
        self.user_answers = {i: 0 for i in range(1, 51)}

    def load_exam(self, exam_name):
        """ 선택한 회차의 시험을 로드 """
        self.selected_exam = exam_name
        exam_folder = os.path.join(DATA_FOLDER, exam_name)
        self.exam_images = sorted(
            [f for f in os.listdir(exam_folder) if f.endswith(".png")]
        )
        print(f"🔍 선택한 시험: {exam_name}")
        self.current_page = 0  #
        self.show_exam_page() 
        self.update_question()
        self.update_answer_buttons()
    
    def show_exam_page(self):
        """ 현재 페이지의 시험지 이미지를 표시 """
        if not self.exam_images:
            print("❌ 오류: 시험지 이미지가 없습니다! (show_exam_page)")
            return

        image_path = os.path.join(DATA_FOLDER, self.selected_exam, self.exam_images[self.current_page])
        print(f"✅ 현재 시험지 이미지 경로: {image_path}")

        if not os.path.exists(image_path):
            print(f"❌ 오류: {image_path} 파일이 존재하지 않습니다!")
            return

        self.ids.exam_image.source = image_path  # ✅ 이미지 업데이트
        self.ids.exam_image.reload()  # ✅ Kivy에서 이미지 다시 로드
        self.ids.current_page.text = f"P.{self.current_page+1}"

    def prev_page(self):
        """ 이전 시험지 페이지 """
        if self.current_page > 0:
            self.current_page -= 1
            self.show_exam_page()

    def next_page(self):
        """ 다음 시험지 페이지 """
        if self.current_page < len(self.exam_images) - 1:
            self.current_page += 1
            self.show_exam_page()

    def update_question(self):
        """ 현재 문항 번호 업데이트 """
        self.ids.question_number.text = f"{self.current_question}번"

    def prev_question(self):
        """ 이전 문항 이동 """
        if self.current_question > 1:
            self.current_question -= 1
            self.update_question()
            self.update_answer_buttons()

    def next_question(self):
        """ 다음 문항 이동 """
        if self.current_question < 50:
            self.current_question += 1
            self.update_question()
            self.update_answer_buttons()

    def select_answer(self, answer):
        """ 정답 선택 """
        self.user_answers[self.current_question] = answer
        self.update_answer_buttons()

    def update_answer_buttons(self):
        """ 선택한 정답 버튼 강조, 선택 안 했으면 초기화 """
        selected_answer = self.user_answers.get(self.current_question, 0)
        for i in range(1, 5):
            btn = self.ids[f"answer_btn_{i}"]
            btn.background_color = (0.8, 0.8, 0.8, 1) if i != selected_answer else (0, 0.6, 1, 1)

    def reset(self):
        """ 홈으로 돌아가고 모든 데이터 초기화 """
        self.manager.current = "main"

    def submit_exam(self):
        """ 시험 종료 후 채점 페이지로 이동 """
        result_screen = self.manager.get_screen("result")
        result_screen.selected_exam = self.selected_exam
        result_screen.load_results(self.user_answers)
        self.manager.current = "result"

class ResultScreen(Screen):           
    def load_results(self, user_answers):
        correct_answers = self.get_correct_answers()

        # ✅ 정답 비교 및 점수 계산
        score = sum(2 for q, ans in user_answers.items() if ans == correct_answers.get(q, 0))
        self.ids.score_label.text = f"정답 개수: {score // 2} / 오답 개수: {50 - (score // 2)} / 점수: {score}점"

        result_table = self.ids.result_table
        result_table.clear_widgets()

        row_height = 40  # ✅ 각 행의 높이 설정

        for i in range(1, 51):
            correct = correct_answers.get(i, 0)
            user = user_answers.get(i, 0)

            num_label = Label(
                text=str(i),
                font_size=18,
                font_name="NotoSans",
                size_hint_y=None,
                height=row_height,
                bold=True,
                color=(0, 0, 0, 1)
            )

            user_box = BoxLayout(size_hint_y=None, height=row_height)
            with user_box.canvas.before:
                user_box.canvas.before.clear()
                with user_box.canvas.before:
                    Color(1, 0.3, 0.3, 1) if user != correct else Color(0.6, 1, 0.6, 1)
                    Rectangle(pos=user_box.pos, size=user_box.size)

            user_label = Label(
                text=str(user),
                font_size=18,
                font_name="NotoSans",
                size_hint_y=None,
                height=row_height,
                color=(0, 0, 0, 1)
            )
            user_box.add_widget(user_label)  # ✅ Label을 BoxLayout 내부에 추가

            # ✅ 정답 (Label)
            correct_label = Label(
                text=str(correct),
                font_size=18,
                font_name="NotoSans",
                size_hint_y=None,
                height=row_height,
                color=(0, 0, 0, 1)
            )

            # ✅ `GridLayout`에 추가
            result_table.add_widget(num_label)
            result_table.add_widget(user_box)
            result_table.add_widget(correct_label)
    
    def get_correct_answers(self):
        """ 정답 로드 (파일에서 불러오기) """
        answer_path = os.path.join(DATA_FOLDER, self.selected_exam,"answer_key.json")
        if os.path.exists(answer_path):
            print("읽음")
            with open(answer_path, "r", encoding="utf-8") as f:
                correct_answers = json.load(f)
                correct_answers = {int(k): v for k, v in correct_answers.items()}
                return correct_answers
            
        return {i: 0 for i in range(1, 51)}

    def return_to_exam(self):
        """ 시험 페이지로 돌아가서 기존 선택 유지 """
        self.manager.current = "exam"

    def reset(self):
        """ 홈으로 돌아가고 모든 데이터 초기화 """
        self.manager.current = "main"

class CBTApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(ExamScreen(name="exam"))
        sm.add_widget(ResultScreen(name="result"))
        return sm

if __name__ == "__main__":
    CBTApp().run()
