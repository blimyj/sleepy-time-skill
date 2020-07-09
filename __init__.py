from mycroft import MycroftSkill, intent_file_handler


class SleepyTime(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('time.sleepy.intent')
    def handle_time_sleepy(self, message):
        self.speak_dialog('time.sleepy')


def create_skill():
    return SleepyTime()

