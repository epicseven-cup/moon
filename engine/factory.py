from engine.moon_engine import MoonEngine
from engine.model import Model
import gi
from textblob import TextBlob

gi.require_version("IBus", "1.0")
gi.require_version("GioUnix","2.0")
from gi.repository import IBus
class EngineFactory:
    def __init__(self):
        self.bus = IBus.Bus()
        connection = self.bus.get_connection()
        self.factory = IBus.Factory.new(connection)


        self.factory.add_engine("Moon", MoonEngine)

        self.bus.request_name("org.freedesktop.IBus.Moon", 0)
