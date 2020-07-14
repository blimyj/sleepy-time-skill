from mycroft import MycroftSkill, intent_file_handler
import os
import vlc
from datetime import datetime, timedelta
from adapt.intent import IntentBuilder
from mycroft import intent_handler


class SleepyTime(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)
        self.custom_data_folder_name = "SleepyTimeSkill"

        self.audiobook_instance = vlc.Instance()  # '--novideo')
        self.audiobook_player = self.audiobook_instance.media_player_new()

        # State of audiobook player before it was paused due to Mycroft listening or speaking
        self.pre_pause_state_audplayer = 0

    def initialize(self):
        self.log.info("Initializing Phase 2")

        # def __init__ or initialize method
        # Refer: https://mycroft-ai.gitbook.io/docs/skill-development/skill-structure/lifecycle-methods
        self.custom_data_setup()
        self.print_files()

        # Message Handlers for Mycroft listening & speaking
        self.add_event('recognizer_loop:record_begin', self.handler_record_begin)
        self.add_event('recognizer_loop:record_end', self.handler_record_end)
        self.add_event('recognizer_loop:audio_output_start', self.handler_audio_output_start)
        self.add_event('recognizer_loop:audio_output_end', self.handler_audio_output_end)
        self.log.info("Phase 2 Complete")

    '''
    Methods for Custom Data Folder Setup
    '''
    def custom_data_setup(self):
        skill_name= "SleepyTimeSkill"
        folder_path = "MycroftSkillsUserData/" + self.custom_data_folder_name
        if self.custom_data_folder_setup(folder_path):
            self.speak_dialog("Please copy over the files to {0} for this skill.".format(folder_path))
        else:
            self.log.info('Folder Already Exists.')

    def print_files(self):
        folder_path = os.path.expanduser("~/MycroftSkillsUserData/SleepyTimeSkill")
        files = os.listdir(folder_path)
        self.log.info(files)

    '''
    Returns True if folder created
    Returns False if folder not created, either because it exists or exception raised during creation
    '''
    def custom_data_folder_setup(self, folder_path):

        home_path = os.path.expanduser('~')

        # Get home path
        home_path = os.path.expanduser('~')
        # Append custom foldername to homepath (Name:MycroftSkillsUserData/SleepyTimeSkill)
        # Create path for folder
        user_data_path = os.path.join(home_path, folder_path)

        # Check if MycroftSkillsUserData/SleepyTimeSkill folder does not exist,
        if not os.path.exists(user_data_path):
            # Try Create if doesn't
            try:
                os.makedirs(user_data_path, exist_ok=False)
                # Fail Gracefully if exception
            except Exception as e:
                print("Unexpected error: {0}".format(e))
                return False
        else:
            return False

        self.log.info("Please check the directories exist.")
        return True
    '''
    END: Methods for Custom Data Folder Setup
    '''

    '''
    Custom Data Folder Methods
    '''

    def custom_data_has_files(self):
        '''
        :return:  True if files present in custom data folder, false otherwise.
        '''
        home_path = os.path.expanduser('~')
        folder_path = "MycroftSkillsUserData/" + self.custom_data_folder_name
        user_data_path = os.path.join(home_path, folder_path)

        dir_list = os.listdir(user_data_path)
        return len(dir_list) != 0

    '''
    END: Custom Data Folder Methods
    '''

    @intent_file_handler('time.sleepy.intent')
    def handle_time_sleepy(self, message):

        # If no files print error as program cannot work without an audio file
        if not self.custom_data_has_files():
            self.log.debug("No files found in {0} folder.".format(self.custom_data_folder_name))
            self.speak_dialog("No files found in {0} folder.".format(self.custom_data_folder_name))
            self.speak_dialog("Please copy an audio file in for the skill to work.")
            return

        self.handle_timed_reader(message)

        # Bonus: Check for only audio filetypes

        # Bonus: Store audio position for one file.

        # Bonus: Include commands to list available files and switch between them
        # Bonus: Store audio position for all audio files.
        self.speak_dialog('time.sleepy')

    '''
    Audiobook reading skills
    TODO:
    - Save position everytime its stopped or pause
    - Resume from saved position
    - Set & Reset rate/playback speed
    '''
    def handle_timed_reader(self, message):
        self.handle_read_audiobook(message)

        self.log.debug('Reader Read for 1hr 30min')

        # Schedule reader pause
        read_for = timedelta(hours=0, minutes=1, seconds=0, microseconds=0)
        pause_time = datetime.now() + read_for
        self.schedule_event(self.strict_pause_reader, pause_time)

    def handle_read_audiobook(self, message):
        # Play the first file
        home_path = os.path.expanduser('~')
        folder_path = "MycroftSkillsUserData/" + self.custom_data_folder_name
        user_data_path = os.path.join(home_path, folder_path)
        dir_list = os.listdir(user_data_path)

        first_audiobook_path = os.path.join(user_data_path, dir_list[0])

        if self.audiobook_player.get_state() == 4:
            resp = self.ask_yesno('Would you like to continue where you left off?')
            if resp == 'yes':
                self.audiobook_player.play()
                return
            elif resp == 'no':
                pass  # Leads to code below to start playing audiobook from start
            else:
                return
        else:
            pass  # Leads to code below to start playing audiobook from start

        self.audiobook_player.set_mrl(first_audiobook_path)
        self.audiobook_player.set_rate(0.9)
        self.audiobook_player.audio_set_volume(100)
        self.audiobook_player.play()

    @intent_handler(IntentBuilder('PauseReaderIntent').require('pause_reader'))
    def handle_pause_reader(self, message):
        if self.audiobook_player.is_playing():
            self.audiobook_player.pause()
        self.log.debug('Reader paused')
        self.speak_dialog('Okay.')

    def strict_pause_reader(self):
        # Function to ensure the the audio player strictly pauses and does not just toggle between pause and resume.
        if self.audiobook_player.is_playing():
            self.audiobook_player.pause()

    @intent_handler(IntentBuilder('ContinueReaderIntent').require('continue_reader'))
    def handle_continue_reader(self, message):
        self.speak_dialog('ok')
        self.audiobook_player.play()
        self.log.debug('Reader continue')

    '''
    Player pause & resume for Mycroft listening & speaking intervals
    '''
    def handler_record_begin(self, message):
        self.pre_pause_state_audplayer = self.audiobook_player.get_state()

        if self.pre_pause_state_audplayer == 3: # Enum 3 is "Playing" state ref. vlc API
            self.audiobook_player.pause()

    def handler_record_end(self, message):
        if self.pre_pause_state_audplayer == 3:  # Enum 3 is "Playing" state ref. vlc API
            self.audiobook_player.play()

    def handler_audio_output_start(self, message):
        self.pre_pause_state_audplayer = self.audiobook_player.get_state()

        if self.pre_pause_state_audplayer == 3:  # Enum 3 is "Playing" state ref. vlc API
            self.audiobook_player.pause()

    def handler_audio_output_end(self, message):
        if self.pre_pause_state_audplayer == 3:  # Enum 3 is "Playing" state ref. vlc API
            self.audiobook_player.play()
    '''
    END Player pause & resume for Mycroft listening & speaking intervals
    '''
    def shutdown(self):
        # Method to prevent these player from continue playing when the skill reloads
        self.audiobook_player.stop()
        self.audiobook_instance.release()

def create_skill():
    return SleepyTime()

