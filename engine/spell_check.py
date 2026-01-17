from typing import List
from symspellpy.suggest_item import SuggestItem
from symspellpy.symspellpy import SymSpell

from symspellpy import SymSpell, Verbosity
from importlib import resources

class MoonSpellCheckerEngine:
    def __init__(self):
        self.symspell = SymSpell()
        dictionary = resources.files("symspellpy") / "frequency_dictionary_en_82_765.txt"
        with resources.as_file(dictionary) as path:
            self.symspell.load_dictionary(str(path), term_index=0, count_index=1)
        pass
    def suggestions(self, text) -> List[SuggestItem]:
        s = self.symspell.lookup(
            text, Verbosity.CLOSEST, max_edit_distance=2, include_unknown=True
        )

        return s[:5]
