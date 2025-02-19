#!/usr/bin/env python

import json
import random
import ipywidgets as widgets
from pathlib import Path
from IPython.display import display
from collections.abc import MutableMapping


def flatten(dictionary, parent_key='', separator=' '):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


class Verbs:
    def __init__(self):
        self.path = Path() / 'data' / 'raw'
        verbs = sorted([x.parts[-1].split('.')[0] for x in self.path.iterdir() if x.is_file()])
        self.verbs_dropdown = widgets.Dropdown(options=verbs, value=None)
        self.quiz_label = widgets.Label(value='Pick a verb to start ...')
        self.answer_label = widgets.Label(value='')
        initial_answers = ['One', 'Two', 'Three', 'Four', 'Five']
        self.answers_radio_buttons = widgets.RadioButtons(options=initial_answers, disabled=True, value=None)
        self.next_button = widgets.Button(description='Next', disabled=True)
        self.progress_bar = widgets.IntProgress(value=0, min=0, max=10, step=1, bar_style='success')
        self.current_verb = None
        self.current_answer = None
        self.error_count = 0
        self.verbs_dropdown.observe(self.__verbs_dropdown_handler, names='value')
        self.answers_radio_buttons.observe(self.__answers_radio_buttons_handler, names='value') 
        self.next_button.on_click(self.__next_button_handler)

    def set_up_quiz(self):
        questions = random.sample(sorted(self.current_verb.keys()), 5)
        self.current_answer = random.choice(questions)
        self.quiz_label.value = self.current_answer
        self.answers_radio_buttons.options = [self.current_verb[x] for x in questions]
        self.answers_radio_buttons.value = None
        self.answers_radio_buttons.disabled = False
        self.next_button.disabled = True

    def __verbs_dropdown_handler(self, change):
        with open(self.path / f'{change["new"]}.json') as fp: 
            self.current_verb = flatten(json.load(fp))
            self.progress_bar.value = 0
            self.progress_bar.bar_style = 'success'
            self.progress_bar.max = len(self.current_verb.keys())
            self.quiz_label.value = 'Pick a verb to start ...'
        self.set_up_quiz()

    def __answers_radio_buttons_handler(self, change):
        if not self.answers_radio_buttons.disabled:
            self.answers_radio_buttons.disabled = True
            value = change['new']
            if value == self.current_verb[self.current_answer]:
                self.answer_label.value = ' - Correct!!!'
                self.answer_label.style.text_color = 'green'
            else:
                self.answer_label.value = f'- Incorrect!!! {self.current_verb[self.current_answer]}'
                self.answer_label.style.text_color = 'red'
                self.error_count += 1
            self.progress_bar.value += 1
            if 0 < self.error_count <= 3:
                self.progress_bar.bar_style = 'warning'
            if self.error_count > 5:
                self.progress_bar.bar_style = 'danger'
            self.next_button.disabled = False

    def __next_button_handler(self, button):
        self.answer_label.value = ''
        self.set_up_quiz()
        self.answer_label.style.text_color = 'black'

    def display(self):
        display(widgets.VBox([
            widgets.Label(value='Pick a verb to learn its conjugations ...'),
            self.verbs_dropdown,
            widgets.HBox([self.quiz_label, self.answer_label]),
            self.answers_radio_buttons,
            self.next_button,
            self.progress_bar
        ]))

    