from engine.spell_check import MoonSpellCheckerEngine
from symspellpy.suggest_item import SuggestItem
from typing import List
from engine.model import Model


import gi
gi.require_version("IBus", "1.0")
gi.require_version("GioUnix","2.0")
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import IBus, GLib, Gtk, Gdk
from gi.repository.IBus import LookupTable

class Cursor:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def __str__(self):
        return f"x:{self.x}, y:{self.y}, width:{self.width}, height:{self.height}"


class MoonEngine(IBus.Engine):
    LLM:Model = Model()
    SPELLCHECK: MoonSpellCheckerEngine = MoonSpellCheckerEngine()

    MODIFIER_MASK = (
        IBus.ModifierType.CONTROL_MASK |
        IBus.ModifierType.MOD1_MASK |
        IBus.ModifierType.SUPER_MASK |
        IBus.ModifierType.SHIFT_MASK
    )
    def __init__(self):
        self.word_buffer:str = ""
        self.cursor = Cursor(0 ,0 , 0, 0)
        self.lookup_table: LookupTable = IBus.LookupTable.new(
            page_size=6,
            cursor_pos=0,
            cursor_visible=True,
            round=True
        )
        self.passthrough: bool = False
        self.timer_id = GLib.timeout_add_seconds(15, self.insert_ai_suggestion)
        # self.timer_guess_id = GLib.timeout_add(1, self.ai_word_guess)
        self.current_suggestion_index = 0
        self.current_suggestion_type: str = "word"
        self.current_ai_word_guess: str = ""


    def insert_ai_suggestion(self):
        surrounding_text, p1, p2 = self.get_surrounding_text()
        print(f"Surrounding Text: {surrounding_text.text}")

        # This should only work when user is not typing and surrounding text works on the app
        if surrounding_text and len(self.word_buffer) == 0:
            ai_suggestion_buffer:str = self.LLM.suggestion(surrounding_text.text)
            print(f"AI Surrounding: {ai_suggestion_buffer}")
            self.lookup_table.clear()
            self.lookup_table.append_candidate(IBus.Text.new_from_string(ai_suggestion_buffer))
            self.update_lookup_table(self.lookup_table, True)
            self.current_suggestion_type = "ai"
        return True

    # def ai_word_guess(self):
    #     surrounding_text, cur_p, p2 = self.get_surrounding_text()
    #     # print(f"Surrounding Text: {surrounding_text.text}")
    #     extracted_text = ""
    #     if surrounding_text != None:
    #         extracted_text = surrounding_text.text
    #     # print(self.lookup_table.get_number_of_candidates())
    #     # print(len(self.word_buffer) > 0, "word")
    #     # print(self.lookup_table.get_number_of_candidates(), "number")
    #     # print(len(self.current_ai_word_guess) > 0, "ai current")

    #     if len(self.word_buffer) > 0 and self.lookup_table.get_number_of_candidates() < 6 and len(self.current_ai_word_guess) == 0:
    #         suggestion:str = self.LLM.guess_words(self.word_buffer, extracted_text, cur_p)
    #         self.current_ai_word_guess = suggestion
    #         print(f"Guess suggestion: {suggestion}")
    #         self.lookup_table.append_candidate(IBus.Text.new_from_string(suggestion))
    #         self.update_lookup_table(self.lookup_table, True)
    #     return True

    def record(self, keyval: int):
        if 33 <= keyval <= 127:
            self.current_suggestion_type = "word"
            char = IBus.keyval_to_unicode(keyval)
            self.word_buffer += char
            self.update_candidates()
            self.update_preedit_text(IBus.Text.new_from_string(self.word_buffer), len(self.word_buffer), True)
            # self.update_auxiliary_text(IBus.Text.new_from_string(self.word_buffer), True)
            self.update_lookup_table(self.lookup_table, True)
            self.current_ai_word_guess = ""
            return True

        if IBus.KEY_BackSpace == keyval and len(self.word_buffer) > 0:
            self.word_buffer = self.word_buffer[:-1]
            self.update_preedit_text(IBus.Text.new_from_string(self.word_buffer), len(self.word_buffer), True)
            self.update_lookup_table(self.lookup_table, True)
            return True

        if IBus.KEY_Left == keyval or IBus.KEY_Right == keyval:
            self.reset()
            return False
        return False


    def reset(self):
        self.word_buffer = ""
        self.update_preedit_text(IBus.Text.new_from_string(self.word_buffer), len(self.word_buffer), False)
        self.update_lookup_table(self.lookup_table, False)

    def do_set_cursor_location(self, x, y, w, h):
        self.cursor = Cursor(x, y, w, h)

    def do_focus_in(self):
        self.reset()

    def do_focus_out(self):
        self.reset()

    def do_process_key_event(self, keyval:int, keycode:int, state:int):
        key_name = IBus.keyval_name(keyval)


        is_press = (state & IBus.ModifierType.RELEASE_MASK) == 0
        if not is_press:
            return False


        if (state & IBus.ModifierType.CONTROL_MASK) != 0 and IBus.KEY_1 <= keyval <= IBus.KEY_5:
            index = keyval - IBus.KEY_1

            if index < 0 or index >= self.lookup_table.get_number_of_candidates():
                print("Invidate index")
                return True
            print("Hello")
            print(self.current_suggestion_type)

            return self.do_candidate_clicked(index, 0, 0)

        # Pass through key combo ctrl + shift + m
        if (state & IBus.ModifierType.CONTROL_MASK) != 0 and (state & IBus.ModifierType.SHIFT_MASK) != 0 and keyval == IBus.KEY_M:
            self.passthrough = not self.passthrough
            return True


        if keyval == IBus.ModifierType.CONTROL_MASK or keyval == IBus.ModifierType.SHIFT_MASK or keyval == IBus.ModifierType.MOD1_MASK or keyval == IBus.ModifierType.SUPER_MASK or keyval == IBus.KEY_Control_L:
            return False

        print("After ModifierType check")



        if (state & self.MODIFIER_MASK) != 0:
            self.reset()
            return False

        if self.passthrough:
            # Still record the words so it will be shown when we turn it back on
            self.record(keyval)
            self.update_preedit_text(IBus.Text.new_from_string(self.word_buffer), len(self.word_buffer), False)
            self.update_lookup_table(self.lookup_table, False)
            # Do not want to hanle it
            return False
        else:

            if IBus.KEY_BackSpace == keyval and len(self.word_buffer) == 0:
                self.update_preedit_text(IBus.Text.new_from_string(self.word_buffer), 0, False)
                self.update_lookup_table(self.lookup_table, False)
                return False

            if keyval == IBus.KEY_space or keyval == IBus.KEY_Return:
                self.commit_text(IBus.Text.new_from_string(self.word_buffer))
                self.reset()
                return False


            print("About to record keyval")
            return self.record(keyval)


    def update_candidates(self):
        self.lookup_table.clear()

        suggestions = self.SPELLCHECK.suggestions(self.word_buffer)
        for s in suggestions:
            self.lookup_table.append_candidate(IBus.Text.new_from_string(s.term))

        self.update_lookup_table(self.lookup_table, True)


    def do_candidate_clicked(self, index, button, state):
        if self.current_suggestion_type == "word":
            w = self.lookup_table.get_candidate(index)
            self.commit_text(w)
            self.reset()
            return True
        elif self.current_suggestion_type == "ai":
            if self.lookup_table.get_number_of_candidates() < 1:
                return True
            w = self.lookup_table.get_candidate(0)
            self.delete_surrounding_text(-len(w.text), len(w.text))
            self.commit_text(w)
            self.reset()
            return True
        return False
