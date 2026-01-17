from PySide6.QtWidgets import QApplication
from engine.factory import EngineFactory
import gi.repository.GLib
from engine.moon_engine import MoonEngine
from engine.model import Model
import gi
from textblob import TextBlob
import sys


from gi.repository import IBus, GObject, GLib






if __name__ == "__main__":
    factory = EngineFactory()
    mainloop = GLib.MainLoop()

    try:
        mainloop.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        mainloop.quit()
        sys.exit(0)
