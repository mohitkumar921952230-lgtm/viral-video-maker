import threading
import json
import urllib.request
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window

# Dark studio background
Window.clearcolor = (0.08, 0.09, 0.11, 1)

class InputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        title = Label(
            text="[b]AI VIDEO STUDIO[/b]", 
            markup=True, 
            font_size='22sp', 
            size_hint_y=None, 
            height=40,
            color=(0.2, 0.8, 1, 1)
        )
        layout.add_widget(title)

        self.api_input = TextInput(
            hint_text="Gemini API Key yahan paste karein", 
            password=True, 
            multiline=False, 
            size_hint_y=None, 
            height=45
        )
        layout.add_widget(self.api_input)

        self.niche_input = TextInput(
            hint_text="Channel Topic / Niche (e.g. Bal Ganesha 3D Stories)", 
            multiline=False, 
            size_hint_y=None, 
            height=45
        )
        layout.add_widget(self.niche_input)

        self.sec_input = TextInput(
            hint_text="Video Duration (Seconds, e.g. 30 ya 60)", 
            text="30", 
            multiline=False, 
            size_hint_y=None, 
            height=45
        )
        layout.add_widget(self.sec_input)

        gen_btn = Button(
            text="Create Script & Video Pipeline", 
            size_hint_y=None, 
            height=50,
            background_color=(0, 0.6, 0.9, 1),
            bold=True
        )
        gen_btn.bind(on_release=self.start_pipeline)
        layout.add_widget(gen_btn)

        layout.add_widget(Label())  # Spacer
        self.add_widget(layout)

    def start_pipeline(self, instance):
        api_key = self.api_input.text.strip()
        niche = self.niche_input.text.strip()
        sec = self.sec_input.text.strip()

        if not api_key or not niche:
            return

        studio_app = App.get_running_app()
        studio_app.pipeline_data = {"api_key": api_key, "niche": niche, "seconds": sec}
        self.manager.current = "processing"
        self.manager.get_screen("processing").run_generation()


class ProcessingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        self.status_label = Label(
            text="Connecting to AI Pipeline...", 
            font_size='18sp', 
            color=(0.9, 0.9, 0.9, 1)
        )
        self.layout.add_widget(self.status_label)

        self.progress = ProgressBar(max=100, size_hint_y=None, height=20)
        self.layout.add_widget(self.progress)

        self.sub_label = Label(
            text="Processing request on background thread...", 
            font_size='13sp', 
            color=(0.6, 0.6, 0.6, 1)
        )
        self.layout.add_widget(self.sub_label)

        self.add_widget(self.layout)

    def run_generation(self):
        self.progress.value = 15
        self.status_label.text = "Crafting Script & Visual Cues..."
        threading.Thread(target=self._fetch_gemini_data, daemon=True).start()

    def _fetch_gemini_data(self):
        app = App.get_running_app()
        data = app.pipeline_data
        api_key = data["api_key"]
        niche = data["niche"]
        sec = data["seconds"]

        prompt = (
            f"Act as a professional viral video producer. Create a detailed production package for a {sec}-second short about: {niche}. "
            f"Provide output in this format:\n"
            f"[HOOK / TITLE]: A viral catchy title\n\n"
            f"[VOICEOVER SCRIPT]: Hindi/Hinglish line-by-line script with timestamps\n\n"
            f"[AI IMAGE/VIDEO PROMPTS]: 3D Pixar/realistic image generation prompts for each scene\n\n"
            f"[AUDIO & MUSIC]: Background audio mood and pacing cues."
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            Clock.schedule_once(lambda dt: self.update_progress(45, "Rendering scenes via Gemini 1.5 Flash..."), 0)
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                raw_text = result["candidates"][0]["content"]["parts"][0]["text"]

            Clock.schedule_once(lambda dt: self.finish_success(raw_text), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.finish_error(str(e)), 0)

    def update_progress(self, val, text):
        self.progress.value = val
        self.status_label.text = text

    def finish_success(self, generated_text):
        self.progress.value = 100
        editor = self.manager.get_screen("editor")
        editor.load_content(generated_text)
        self.manager.current = "editor"

    def finish_error(self, err_msg):
        self.status_label.text = "Pipeline Failed!"
        self.sub_label.text = f"Error: {err_msg[:120]}"


class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        header = Label(
            text="[b]Production Studio (Script & Prompts Editor)[/b]", 
            markup=True, 
            size_hint_y=None, 
            height=35,
            color=(0.2, 0.8, 1, 1)
        )
        layout.add_widget(header)

        scroll = ScrollView()
        self.editor_input = TextInput(
            text="", 
            multiline=True, 
            font_size='14sp', 
            background_color=(0.14, 0.15, 0.18, 1), 
            foreground_color=(1, 1, 1, 1)
        )
        scroll.add_widget(self.editor_input)
        layout.add_widget(scroll)

        btn_box = BoxLayout(size_hint_y=None, height=45, spacing=10)
        back_btn = Button(text="Create New", background_color=(0.4, 0.4, 0.4, 1))
        back_btn.bind(on_release=self.go_back)
        btn_box.add_widget(back_btn)

        layout.add_widget(btn_box)
        self.add_widget(layout)

    def load_content(self, text):
        self.editor_input.text = text

    def go_back(self, instance):
        self.manager.current = "input"


class AIStudioApp(App):
    pipeline_data = {}

    def build(self):
        sm = ScreenManager()
        sm.add_widget(InputScreen(name="input"))
        sm.add_widget(ProcessingScreen(name="processing"))
        sm.add_widget(EditorScreen(name="editor"))
        return sm

if __name__ == "__main__":
    AIStudioApp().run()
        
