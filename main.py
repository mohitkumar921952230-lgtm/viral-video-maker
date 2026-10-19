import os
import json
import threading
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.core.window import Window

Window.clearcolor = (0.07, 0.08, 0.11, 1)

CONFIG_FILE = "studio_config.json"

def load_saved_key():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("api_key", "")
        except:
            return ""
    return ""

def save_key(api_key):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"api_key": api_key}, f)
    except:
        pass


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=18, spacing=12)

        title_box = BoxLayout(orientation='vertical', size_hint_y=None, height=60, spacing=4)
        title = Label(
            text="[b]AI VIDEO STUDIO PRO[/b]", 
            markup=True, 
            font_size='22sp', 
            color=(0.2, 0.8, 1, 1)
        )
        subtitle = Label(
            text="Automated 3D Animated Shorts & Reels Pipeline", 
            font_size='12sp', 
            color=(0.6, 0.65, 0.75, 1)
        )
        title_box.add_widget(title)
        title_box.add_widget(subtitle)
        root.add_widget(title_box)

        scroll = ScrollView()
        form = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        form.add_widget(Label(text="Google Gemini API Key:", size_hint_y=None, height=22, font_size='13sp', color=(0.8, 0.8, 0.8, 1)))
        saved_key = load_saved_key()
        self.api_input = TextInput(
            text=saved_key,
            hint_text="API key yahan paste karein (Auto-saved)", 
            password=True, 
            multiline=False, 
            size_hint_y=None, 
            height=46,
            background_color=(0.13, 0.15, 0.20, 1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(self.api_input)

        form.add_widget(Label(text="Story Theme / Channel Niche:", size_hint_y=None, height=22, font_size='13sp', color=(0.8, 0.8, 0.8, 1)))
        self.niche_input = TextInput(
            text="Bal Ganesha 3D Animation Stories",
            hint_text="e.g. Bal Ganesha, Sci-Fi, EDM Tips", 
            multiline=False, 
            size_hint_y=None, 
            height=46,
            background_color=(0.13, 0.15, 0.20, 1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(self.niche_input)

        form.add_widget(Label(text="Specific Setting / Characters (Optional):", size_hint_y=None, height=22, font_size='13sp', color=(0.8, 0.8, 0.8, 1)))
        self.character_input = TextInput(
            text="Bal Ganesha and Mushak on Kailash Mountain",
            hint_text="e.g. Bal Ganesha on Kailash, Dada Ji in Village", 
            multiline=False, 
            size_hint_y=None, 
            height=46,
            background_color=(0.13, 0.15, 0.20, 1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(self.character_input)

        form.add_widget(Label(text="Video Duration (Seconds):", size_hint_y=None, height=22, font_size='13sp', color=(0.8, 0.8, 0.8, 1)))
        self.sec_input = TextInput(
            text="30", 
            multiline=False, 
            size_hint_y=None, 
            height=46,
            background_color=(0.13, 0.15, 0.20, 1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(self.sec_input)

        self.error_label = Label(text="", size_hint_y=None, height=26, color=(1, 0.3, 0.3, 1), font_size='12sp')
        form.add_widget(self.error_label)

        scroll.add_widget(form)
        root.add_widget(scroll)

        self.generate_btn = Button(
            text="Generate Complete Production Studio", 
            size_hint_y=None, 
            height=52, 
            background_color=(0, 0.65, 0.95, 1),
            bold=True,
            font_size='15sp'
        )
        self.generate_btn.bind(on_release=self.validate_and_start)
        root.add_widget(self.generate_btn)

        self.add_widget(root)

    def validate_and_start(self, instance):
        key = self.api_input.text.strip()
        niche = self.niche_input.text.strip()
        char_setting = self.character_input.text.strip()
        sec = self.sec_input.text.strip()

        if not key:
            self.error_label.text = "Error: Pehle API key dalein!"
            return
        if not niche:
            self.error_label.text = "Error: Channel niche/topic dalein!"
            return

        save_key(key)
        self.error_label.text = ""

        app = App.get_running_app()
        app.project_data = {
            "api_key": key,
            "niche": niche,
            "char_setting": char_setting,
            "seconds": sec
        }

        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "processing"
        Clock.schedule_once(lambda dt: self.manager.get_screen("processing").launch_generation(), 0.1)


class ProcessingScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=25)

        layout.add_widget(Label(size_hint_y=0.2))

        self.step_label = Label(
            text="Initialising Studio Pipeline...", 
            font_size='19sp', 
            bold=True,
            color=(0.2, 0.8, 1, 1),
            size_hint_y=None,
            height=40
        )
        layout.add_widget(self.step_label)

        self.progress = ProgressBar(max=100, value=10, size_hint_y=None, height=22)
        layout.add_widget(self.progress)

        self.detail_label = Label(
            text="Establishing secure Google Gemini AI connection...", 
            font_size='13sp', 
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=30
        )
        layout.add_widget(self.detail_label)

        layout.add_widget(Label(size_hint_y=0.5))
        self.add_widget(layout)

    def launch_generation(self):
        self.progress.value = 25
        self.step_label.text = "Structuring Story & Dialogues..."
        self.detail_label.text = "Connecting to Gemini Engine..."
        t = threading.Thread(target=self._worker_thread)
        t.daemon = True
        t.start()

    def _worker_thread(self):
        app = App.get_running_app()
        data = app.project_data

        prompt = (
            f"Act as a professional viral 3D animation shorts director.\n"
            f"Topic: {data['niche']}\n"
            f"Character & Environment: {data['char_setting']}\n"
            f"Duration: {data['seconds']} seconds.\n\n"
            f"Produce output strictly divided into these sections:\n"
            f"===SECTION: SCRIPT===\n"
            f"Title: [Engaging Catchy Title]\n"
            f"Line-by-line script in engaging Hindi/Hinglish with character dialogue, expressions, and timestamps (0s to {data['seconds']}s).\n\n"
            f"===SECTION: PROMPTS===\n"
            f"Detailed, professional 3D Pixar-style prompt for each scene (Scene 1, Scene 2, etc.) ready for Midjourney/Ideogram, maintaining consistent characters and vivid lighting.\n\n"
            f"===SECTION: AUDIO===\n"
            f"Complete background sound effects (SFX), musical mood, pacing, and voice modulation directions."
        )

        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        # Supported models list for automatic fallback
        model_endpoints = [
            ("v1beta", "gemini-1.5-flash-latest"),
            ("v1beta", "gemini-1.5-pro-latest"),
            ("v1beta", "gemini-pro"),
            ("v1", "gemini-1.5-flash")
        ]

        success = False
        last_error = ""

        for ver, mod in model_endpoints:
            url = f"https://generativelanguage.googleapis.com/{ver}/models/{mod}:generateContent?key={data['api_key']}"
            try:
                Clock.schedule_once(lambda dt, m=mod: self.update_status(65, "Rendering Production Bundle...", f"Connected via {m}..."), 0)
                res = requests.post(url, headers=headers, json=payload, timeout=40, verify=False)
                res_json = res.json()

                if "candidates" in res_json and len(res_json["candidates"]) > 0:
                    raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    Clock.schedule_once(lambda dt: self.on_complete(raw_text), 0)
                    success = True
                    break
                elif "error" in res_json:
                    last_error = res_json["error"].get("message", "API Request Failed")
            except Exception as e:
                last_error = str(e)

        if not success:
            Clock.schedule_once(lambda dt: self.on_fail(f"API Error: {last_error}"), 0)

    def update_status(self, val, step_txt, detail_txt):
        self.progress.value = val
        self.step_label.text = step_txt
        self.detail_label.text = detail_txt

    def on_complete(self, content):
        self.progress.value = 100
        editor = self.manager.get_screen("editor")
        editor.parse_and_display(content)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "editor"

    def on_fail(self, err_message):
        editor = self.manager.get_screen("editor")
        editor.display_error(err_message)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "editor"


class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.full_content = ""
        self.script_part = ""
        self.prompts_part = ""
        self.audio_part = ""

        root = BoxLayout(orientation='vertical', padding=14, spacing=8)

        header = BoxLayout(size_hint_y=None, height=42, spacing=10)
        back_btn = Button(text="< New", size_hint_x=0.25, background_color=(0.25, 0.28, 0.35, 1))
        back_btn.bind(on_release=self.go_home)
        title = Label(text="[b]Production Studio Editor[/b]", markup=True, font_size='16sp', color=(0.2, 0.8, 1, 1))
        copy_all_btn = Button(text="Copy All", size_hint_x=0.28, background_color=(0, 0.6, 0.4, 1))
        copy_all_btn.bind(on_release=self.copy_all)

        header.add_widget(back_btn)
        header.add_widget(title)
        header.add_widget(copy_all_btn)
        root.add_widget(header)

        tab_bar = BoxLayout(size_hint_y=None, height=36, spacing=6)
        self.btn_all = Button(text="All", background_color=(0, 0.6, 0.9, 1))
        self.btn_all.bind(on_release=lambda x: self.switch_view("all"))

        self.btn_script = Button(text="Script", background_color=(0.2, 0.22, 0.28, 1))
        self.btn_script.bind(on_release=lambda x: self.switch_view("script"))

        self.btn_prompts = Button(text="3D Prompts", background_color=(0.2, 0.22, 0.28, 1))
        self.btn_prompts.bind(on_release=lambda x: self.switch_view("prompts"))

        self.btn_audio = Button(text="Audio/SFX", background_color=(0.2, 0.22, 0.28, 1))
        self.btn_audio.bind(on_release=lambda x: self.switch_view("audio"))

        tab_bar.add_widget(self.btn_all)
        tab_bar.add_widget(self.btn_script)
        tab_bar.add_widget(self.btn_prompts)
        tab_bar.add_widget(self.btn_audio)
        root.add_widget(tab_bar)

        scroll = ScrollView()
        self.editor = TextInput(
            text="", 
            multiline=True, 
            font_size='14sp', 
            background_color=(0.11, 0.12, 0.16, 1), 
            foreground_color=(0.95, 0.95, 0.95, 1),
            padding=[10, 10, 10, 10]
        )
        scroll.add_widget(self.editor)
        root.add_widget(scroll)

        self.toast = Label(text="", size_hint_y=None, height=22, font_size='12sp', color=(0.3, 1, 0.4, 1))
        root.add_widget(self.toast)

        self.add_widget(root)

    def parse_and_display(self, content):
        self.full_content = content
        self.script_part = content
        self.prompts_part = ""
        self.audio_part = ""

        if "===SECTION: SCRIPT===" in content:
            try:
                parts = content.split("===SECTION: SCRIPT===")[1]
                if "===SECTION: PROMPTS===" in parts:
                    s_part, rest = parts.split("===SECTION: PROMPTS===")
                    self.script_part = s_part.strip()
                    if "===SECTION: AUDIO===" in rest:
                        p_part, a_part = rest.split("===SECTION: AUDIO===")
                        self.prompts_part = p_part.strip()
                        self.audio_part = a_part.strip()
                    else:
                        self.prompts_part = rest.strip()
            except:
                pass

        self.switch_view("all")
        self.toast.text = "Production bundle generated successfully!"

    def display_error(self, err):
        self.editor.text = f"An error occurred while communicating with Gemini AI:\n\n{err}\n\nPlease check your internet connection and verify that your API key is active."
        self.toast.text = "Failed to fetch response."

    def switch_view(self, view_type):
        active = (0, 0.6, 0.9, 1)
        inactive = (0.2, 0.22, 0.28, 1)

        self.btn_all.background_color = active if view_type == "all" else inactive
        self.btn_script.background_color = active if view_type == "script" else inactive
        self.btn_prompts.background_color = active if view_type == "prompts" else inactive
        self.btn_audio.background_color = active if view_type == "audio" else inactive

        if view_type == "all":
            self.editor.text = self.full_content
        elif view_type == "script":
            self.editor.text = self.script_part if self.script_part else self.full_content
        elif view_type == "prompts":
            self.editor.text = self.prompts_part if self.prompts_part else "No separate prompts parsed."
        elif view_type == "audio":
            self.editor.text = self.audio_part if self.audio_part else "No audio cues parsed."

    def copy_all(self, instance):
        if self.editor.text:
            Clipboard.copy(self.editor.text)
            self.toast.text = "Copied to clipboard!"

    def go_home(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "home"


class AIStudioApp(App):
    project_data = {}

    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ProcessingScreen(name="processing"))
        sm.add_widget(EditorScreen(name="editor"))
        return sm


if __name__ == "__main__":
    AIStudioApp().run()
        
