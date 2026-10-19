import os
import json
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

class VideoCreatorApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Title
        self.layout.add_widget(Label(text="[b]AI Video Studio[/b]", markup=True, font_size='22sp', size_hint_y=None, height=40))
        
        # API Key Input
        self.api_input = TextInput(hint_text="Gemini API Key Dalein", multiline=False, size_hint_y=None, height=45, password=True)
        self.layout.add_widget(self.api_input)

        # Channel Name Input
        self.channel_input = TextInput(hint_text="Channel Ka Naam / Niche", multiline=False, size_hint_y=None, height=45)
        self.layout.add_widget(self.channel_input)

        # Video Format Dropdown
        self.format_spinner = Spinner(
            text='Shorts (9:16)',
            values=('Shorts (9:16)', 'Long-Form (16:9)'),
            size_hint_y=None,
            height=45
        )
        self.layout.add_widget(self.format_spinner)

        # Duration Input
        self.duration_input = TextInput(hint_text="Kitne seconds ki video chahiye (e.g. 30)", multiline=False, size_hint_y=None, height=45)
        self.layout.add_widget(self.duration_input)

        # Generate Button
        self.btn = Button(text="Generate Video & Guide", size_hint_y=None, height=50, background_color=(0.1, 0.6, 0.9, 1))
        self.btn.bind(on_press=self.start_process)
        self.layout.add_widget(self.btn)

        # Status & Results Box
        self.scroll = ScrollView()
        self.output_label = Label(text="Details fill karein aur Generate dabayein.", size_hint_y=None, halign="left", valign="top")
        self.output_label.bind(width=lambda *x: setattr(self.output_label, 'text_size', (self.output_label.width, None)))
        self.output_label.bind(texture_size=lambda *x: setattr(self.output_label, 'height', self.output_label.texture_size[1]))
        self.scroll.add_widget(self.output_label)
        self.layout.add_widget(self.scroll)

        return self.layout

    def start_process(self, instance):
        if not self.api_input.text or not self.channel_input.text:
            self.output_label.text = "Error: API Key aur Channel Name zaroori hai!"
            return
        self.output_label.text = "Processing... Script, Scenes aur CapCut Guide ban rahi hai..."
        threading.Thread(target=self.run_generation).start()

    def run_generation(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_input.text.strip())
            model = genai.GenerativeModel("gemini-1.5-flash")

            dur = self.duration_input.text.strip() or "30"
            fmt = self.format_spinner.text
            ch = self.channel_input.text.strip()

            prompt = f"""
            YouTube Creator Assistant:
            Channel: {ch}
            Duration: {dur} seconds
            Format: {fmt}

            Return response in clean readable text:
            1. High Retention Viral Hook & Script
            2. CapCut Human Touch Guide (Timestamps ke saath SFX, Transitions, Text Pops)
            3. Best YouTube Title & Tags
            """
            res = model.generate_content(prompt)
            Clock.schedule_once(lambda dt: self.update_ui(res.text))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_ui(f"Error aaya: {str(e)}"))

    def update_ui(self, text):
        self.output_label.text = text

if __name__ == '__main__':
    VideoCreatorApp().run()
      
