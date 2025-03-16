#!/usr/bin/env python

import json
from pathlib import Path

import ipywidgets as widgets
from IPython.display import display

from quiz import SingleVerbChallenge, Quiz


class Verbs:
    DEFAULT_QUIZ_LABEL = 'Pick a verb to start ...'

    def __init__(self, focus: list | None = None):
        super().__init__()
        self.focus = focus
        self.path = Path() / 'data' / 'raw'
        self.path.mkdir(parents=True, exist_ok=True)
        self.title = widgets.Label(value='Pick a verb to learn its conjugations ...')
        verbs = sorted([x.parts[-1].split('.')[0] for x in self.path.iterdir() if x.is_file()])
        self.verbs_dropdown = widgets.Dropdown(options=verbs, value=None)
        self.quiz_label = widgets.Label(value=Verbs.DEFAULT_QUIZ_LABEL)
        self.answer_label = widgets.Label(value='')
        initial_answers = ['pick a verb'] * 5
        self.answers_dropdown = widgets.Dropdown(options=initial_answers, disabled=True, value=None)
        self.next_button = widgets.Button(description='Next', disabled=True)
        self.progress_bar = widgets.IntProgress(value=0, min=0, max=10, step=1, bar_style='success')
        self.single_verb_challenge: SingleVerbChallenge|None = None
        self.verbs_dropdown.observe(self.__verbs_dropdown_handler, names='value')
        self.answers_dropdown.observe(self.__answers_radio_buttons_handler, names='value')
        self.next_button.on_click(self.__next_button_handler)

    def next_question(self, advance=True):
        if advance: self.single_verb_challenge.advance_to_next_quiz()
        current_quiz: Quiz = self.single_verb_challenge.get_current_quiz()
        self.answers_dropdown.value = None
        self.next_button.disabled = True
        if current_quiz:
            self.quiz_label.value = current_quiz.question
            self.answers_dropdown.options = current_quiz.answer_choices
            self.answers_dropdown.disabled = False
        else:
            self.quiz_label.value = Verbs.DEFAULT_QUIZ_LABEL
            self.answers_dropdown.options = ['pick a verb'] * 5
            self.answers_dropdown.disabled = True

    def __verbs_dropdown_handler(self, change: dict):
        with open(self.path / f'{change["new"]}.json') as fp: 
            self.single_verb_challenge = SingleVerbChallenge(json.load(fp), self.focus)
            self.single_verb_challenge.start()
            self.progress_bar.value = 0
            self.progress_bar.bar_style = 'success'
            self.progress_bar.max = self.single_verb_challenge.size
            self.quiz_label.value = Verbs.DEFAULT_QUIZ_LABEL
        self.next_question(False)

    def __answers_radio_buttons_handler(self, change: dict):
        if not self.answers_dropdown.disabled:
            self.answers_dropdown.disabled = True
            if self.single_verb_challenge.get_current_quiz().answer(change['new']):
                self.answer_label.value = ' - Correct!!!'
                self.answer_label.style.text_color = 'green'
            else:
                correct_answer = self.single_verb_challenge.get_current_quiz().correct_answer
                self.answer_label.value = f'- Incorrect!!! {correct_answer}'
                self.answer_label.style.text_color = 'red'
            self.progress_bar.value += 1
            if 0 < self.single_verb_challenge.get_error_count() <= 1:
                self.progress_bar.bar_style = 'warning'
            if self.single_verb_challenge.get_error_count() > 2:
                self.progress_bar.bar_style = 'danger'
            self.next_button.disabled = False

    def __next_button_handler(self, button):
        self.answer_label.value = ''
        self.next_question()
        self.answer_label.style.text_color = 'black'

    # doesn't work all the way for radio buttons and dropdown
    def set_font_size(self, font_size: int):
        for _, value in self.__dict__.items():
            if isinstance(value, widgets.Widget):
                value.style = {'font_size': f'{font_size}px'}

    def display(self):
        display(widgets.VBox([
            self.title,
            self.verbs_dropdown,
            widgets.HBox([self.quiz_label, self.answer_label]),
            self.answers_dropdown,
            self.next_button,
            self.progress_bar
        ]))
