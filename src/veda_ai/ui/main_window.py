from __future__ import annotations

import sys
import threading
import logging
from datetime import datetime

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from .components import SideNavigation, TopBar
from .pages import DashboardPage, PagePlaceholder, VoiceAssistantPage
from .styles import GLOBAL_STYLES
from ..bootstrap import AppContext
import platform


class VedaMainWindow(QMainWindow):
    def __init__(self, context: AppContext) -> None:
        super().__init__()
        self.context = context
        self._awaiting_task: bool = False
        self.setWindowTitle("VEDA AI")
        self.resize(1400, 920)
        self.setMinimumSize(1200, 780)
        self.setStyleSheet(GLOBAL_STYLES)
        self._build_ui()
        self._start_clock()
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(500)
        self._poll_timer.timeout.connect(self._poll_transcription)

    def _build_ui(self) -> None:
        self.sidebar = SideNavigation(self)
        self.sidebar.page_requested.connect(self._switch_page)

        self.topbar = TopBar(self)

        recog_name = "none"
        if self.context.recognizer is not None:
            try:
                recog_name = type(self.context.recognizer).__name__
            except Exception:
                recog_name = "unknown"
        self.topbar.recognizer_status.setText(f"Recognizer: {recog_name}")

        self.stack = QStackedWidget(self)
        self.voice_page = VoiceAssistantPage()
        self.voice_page.start_listening.connect(self._start_listening)
        self.voice_page.stop_listening.connect(self._stop_listening)
        self.voice_page.text_command_submitted.connect(self._handle_text_command)

        self.voice_page.set_microphone_status(self.context.recognizer is not None)
        self.voice_page.set_recognizer_status(recog_name)

        self.pages = {
            "dashboard": DashboardPage(),
            "voice": self.voice_page,
            "ai_chat": PagePlaceholder("AI Chat", "Talk to the assistant, ask for code, or generate content."),
            "automation": PagePlaceholder("Automation", "Design IF / THEN workflows and automations."),
            "file_manager": PagePlaceholder("File Manager", "Browse and manage files with a modern explorer."),
            "browser": PagePlaceholder("Browser Automation", "Automate web browsing, search, and downloads."),
            "email": PagePlaceholder("Email Automation", "Send, summarize, and automate email workflows."),
            "scheduler": PagePlaceholder("Scheduler", "Create reminders, timers, and cron jobs."),
            "analytics": PagePlaceholder("Analytics", "Monitor system health and assistant usage trends."),
            "memory": PagePlaceholder("AI Memory", "Store and recall preferences, commands, and context."),
            "settings": PagePlaceholder("Settings", "Configure theme, voice, API keys, and privacy."),
        }

        for page in self.pages.values():
            self.stack.addWidget(page)

        self.stack.setCurrentWidget(self.pages["dashboard"])

        content_frame = QFrame(self)
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.addWidget(self.topbar)
        content_layout.addWidget(self.stack)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_frame, 1)

        container = QWidget(self)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def _switch_page(self, page_key: str) -> None:
        page = self.pages.get(page_key)
        if page is not None:
            self.stack.setCurrentWidget(page)

    def _start_clock(self) -> None:
        self._update_clock()
        timer = QTimer(self)
        timer.timeout.connect(self._update_clock)
        timer.start(1000)

    def _update_clock(self) -> None:
        now = datetime.now().strftime("%I:%M:%S %p")
        self.topbar.clock.setText(now)

    def _start_listening(self) -> None:
        if self.context.recognizer is None:
            return

        try:
            self.context.recognizer.start_listening()
            self._poll_timer.start()
            self.voice_page.set_listening_state()
            self.topbar.microphone_status.setText("🟢 Listening")
            self._play_tone(start=True)
        except RuntimeError as error:
            self.voice_page.display_transcription(f"Voice error: {error}")
            self.voice_page.set_ready_state()
            self.topbar.microphone_status.setText("⚪ Idle")

    def _stop_listening(self) -> None:
        if self.context.recognizer is None:
            return

        self.context.recognizer.stop_listening()
        self._poll_timer.stop()
        self.voice_page.set_ready_state()
        self.topbar.microphone_status.setText("⚪ Idle")
        self._play_tone(start=False)

    def _play_tone(self, start: bool = True) -> None:
        # Play a short start/stop tone. Use winsound on Windows, otherwise no-op.
        def worker(freq: int, dur: int) -> None:
            try:
                if platform.system().lower() == "windows":
                    import winsound

                    winsound.Beep(freq, dur)
            except Exception:
                pass

        if start:
            threading.Thread(target=worker, args=(880, 150), daemon=True).start()
        else:
            threading.Thread(target=worker, args=(440, 150), daemon=True).start()

    def _poll_transcription(self) -> None:
        if self.context.recognizer is None:
            return

        transcript = self.context.recognizer.get_transcription()
        if transcript:
            self.voice_page.display_transcription(f"You: {transcript}")
            response = self._execute_intent(transcript)
            self.voice_page.display_response(response)

    def _handle_text_command(self, text: str) -> None:
        response = self._execute_intent(text)
        self.voice_page.display_response(response)

    def _execute_intent(self, text: str) -> str:
        # If we're awaiting a confirmation (for actions like mute/unmute), handle it first
        if getattr(self, "_awaiting_confirmation", None):
            resp = text.lower().strip()
            if any(x in resp for x in ("yes", "haan", "ha", "ok", "okay", "confirm", "confirm karo", "sure")):
                intent = self._awaiting_confirmation
                self._awaiting_confirmation = None
                if intent == "mute":
                    try:
                        self.context.automation.mute()
                        msg = "Muted."
                    except Exception:
                        logging.getLogger(__name__).exception("Failed to mute")
                        msg = "Couldn't mute the audio."
                else:
                    try:
                        self.context.automation.unmute()
                        msg = "Unmuted."
                    except Exception:
                        logging.getLogger(__name__).exception("Failed to unmute")
                        msg = "Couldn't unmute the audio."
                self._speak_response(msg)
                return msg
            else:
                # Cancel on any other response
                self._awaiting_confirmation = None
                cancel_msg = "Okay — cancelled."
                self._speak_response(cancel_msg)
                return cancel_msg

        # If we're awaiting a task (user said just the wakeword previously), treat this text as the task
        if getattr(self, "_awaiting_task", False):
            self._awaiting_task = False
            logging.getLogger(__name__).info("Received task after wakeword: %s", text)
            parse_result = self.context.intent_parser.parse(text)
            logging.getLogger(__name__).info("Parsed actions (local): %s", parse_result.to_json())
        else:
            # Wakeword handling: if user says "veda <task>", treat the remainder as the command
            import re

            wake_match = re.match(r"^\s*veda[\s,:-]+(.+)$", text, re.IGNORECASE)
            if wake_match:
                task_text = wake_match.group(1).strip()
                logging.getLogger(__name__).info("Wakeword detected, task: %s", task_text)
                parse_result = self.context.intent_parser.parse(task_text)
            else:
                # If user said only 'veda', prompt for the task and set awaiting state
                if re.match(r"^\s*veda\s*$", text, re.IGNORECASE):
                    self._awaiting_task = True
                    prompt = "Yes — what should I do?"
                    logging.getLogger(__name__).info("Wakeword only received; awaiting task.")
                    self._speak_response(prompt)
                    return prompt
                parse_result = self.context.intent_parser.parse(text)
        logging.getLogger(__name__).info("Parsed actions (local): %s", parse_result.to_json())
        result = self.context.intent_executor.execute_actions(
            parse_result.actions,
            text,
            self.context.automation,
            self.context.system,
        )
        # If the action is mute/unmute, require a short confirmation to reduce false triggers
        if parse_result.actions:
            first_intent = parse_result.actions[0].intent
            if first_intent in ("mute", "unmute"):
                # Ask for confirmation and await next utterance
                confirm_prompt = f"Do you want me to {first_intent} the audio?"
                self._awaiting_confirmation = first_intent
                self._speak_response(confirm_prompt)
                return confirm_prompt
        # If local parsing failed to produce an executable action, try AI provider
        if not result.success and getattr(self.context, "ai_provider", None) is not None:
            try:
                ai_parse = self.context.intent_parser.parse_with_ai(text, self.context.ai_provider)
                logging.getLogger(__name__).info("Parsed actions (ai): %s", ai_parse.to_json())
                if ai_parse.actions:
                    result = self.context.intent_executor.execute_actions(
                        ai_parse.actions,
                        text,
                        self.context.automation,
                        self.context.system,
                    )
            except Exception:
                logging.getLogger(__name__).exception("AI parsing failed")
        # On failure, prefer AI provider if configured, otherwise use local fallback
        if not result.success:
            fallback = self._local_fallback(text)
            self._speak_response(fallback)
            return fallback

        self._speak_response(result.message)
        return result.message

    def _local_fallback(self, text: str) -> str:
        # Very small rule-based fallback for casual phrases when AI is unavailable
        t = text.lower().strip()
        if any(g in t for g in ("hello", "hi", "hey")):
            return "Hello — I can open apps, take screenshots, search the web, or execute system commands."
        if "how are you" in t:
            return "I'm a desktop assistant — ready to help. Try saying 'open VS Code' or 'take a screenshot'."
        return "I don't have an AI provider configured. Try a concrete command like 'open VS Code' or enable an AI key in settings."

    def _speak_response(self, text: str) -> None:
        if self.context.speech_engine is None:
            return

        def worker() -> None:
            self.context.speech_engine.speak(text)

        threading.Thread(target=worker, daemon=True).start()


class VedaApp:
    def __init__(self, context: AppContext, argv: list[str] | None = None) -> None:
        self.context = context
        self._app = QApplication(argv or sys.argv)
        self._window = VedaMainWindow(context)

    def run(self) -> int:
        self._window.show()
        # Auto-start listening in offline_mode when a recognizer is available
        try:
            if getattr(self.context, "config", None) and getattr(self.context.config, "offline_mode", False):
                if self.context.recognizer is not None:
                    QTimer.singleShot(200, self._window._start_listening)
        except Exception:
            pass
        return self._app.exec()


def main(context: AppContext) -> int:
    app = VedaApp(context)
    return app.run()


if __name__ == "__main__":
    raise SystemExit("Run src.veda_ai.app instead of this module.")
