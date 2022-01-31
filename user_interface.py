import multiprocessing
import readline

from api import API
from challenge_color import Challenge_Color
from challenge_handler import Challenge_Handler
from config import load_config
from logo import LOGO
from matchmaking import Matchmaking
from variant import Variant


class UserInterface:
    def __init__(self) -> None:
        self.config = load_config()
        self.api = API(self.config['token'])
        self.manager = multiprocessing.Manager()
        self.is_running = self.manager.Value(bool, True)
        self.accept_challenges = self.manager.Value(bool, True)

    def start(self) -> None:
        print(LOGO)
        self.game_semaphore = multiprocessing.Semaphore(self.config['challenge']['concurrency'])

        self.challenge_handler = Challenge_Handler(
            self.config, self.is_running, self.accept_challenges, self.game_semaphore)

        challenge_handler_process = multiprocessing.Process(target=self.challenge_handler.start)
        challenge_handler_process.start()

        self.matchmaking_process = None
        self.matchmaking_process_is_running = self.manager.Value(bool, False)

        completer = Autocompleter(['abort', 'challenge', 'matchmaking', 'quit', 'stop', 'upgrade'])
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')

        print('accepting challenges ...')

        while self.is_running.value:
            command = input()

            if command == 'stop':
                if not self.matchmaking_process:
                    print('matchmaking isn\'t currently running ...')
                    continue

                self.matchmaking_process_is_running.value = False
                print('Stopping matchmaking ...')
                self.matchmaking_process.join()
                self.matchmaking_process = None
                self.game_semaphore.release()
                self.accept_challenges.value = True
                print('Matchmaking has been stopped. And challenges are resuming ...')

            elif command == 'quit':
                self.is_running.value = False
                self.matchmaking_process_is_running.value = False
                print('Terminating programm ...')
                if self.matchmaking_process:
                    self.matchmaking_process.join()
                challenge_handler_process.join()

            elif command.startswith('matchmaking'):
                command_parts = command.split()
                if len(command_parts) > 2:
                    print('Usage: matchmaking [VARIANT]')
                elif len(command_parts) == 2:
                    self._start_matchmaking(Variant(command_parts[1]))
                else:
                    self._start_matchmaking(Variant.STANDARD)

            elif command.startswith('abort'):
                game_id = command.split()[1]
                self.api.abort_game(game_id)

            elif command.startswith('challenge'):
                command_parts = command.split()
                command_length = len(command_parts)
                if command_length < 2 or command_length > 6:
                    print('Usage: challenge USERNAME [INITIAL_TIME] [INCREMENT] [COLOR] [RATED]')
                    continue

                opponent_username = command_parts[1]
                initial_time = int(command_parts[2]) if command_length > 2 else 60
                increment = int(command_parts[3]) if command_length > 3 else 0
                color = Challenge_Color(command_parts[4].lower()) if command_length > 4 else Challenge_Color.RANDOM
                rated = command_parts[5].lower() == 'true' if command_length > 5 else True

                self.api.create_challenge(opponent_username, initial_time, increment,
                                          rated, color, Variant.STANDARD, 20)

            elif command == 'upgrade':
                print('This will upgrade your account to a bot account.')
                print('WARNING: This is irreversible. The account will only be able to play as a Bot.')
                approval = input('Do you want to continue? [y/N]: ')

                if approval.lower() not in ['y', 'yes']:
                    print('Upgrade aborted.')
                    continue

                outcome = 'successful' if self.api.upgrade_account() else 'failed'
                print(f'Upgrade {outcome}.')

            else:
                print('Press <TAB><TAB> to see all valid options!')

    def _start_matchmaking(self, variant: Variant) -> None:
        if self.matchmaking_process:
            print('matchmaking already running ...')
            return

        self.accept_challenges.value = False
        print('Waiting for all games to finish ...')
        self.game_semaphore.acquire()
        print('Starting matchmaking ...')

        self.matchmaking_process_is_running.value = True
        self.matchmaking = Matchmaking(self.config, self.matchmaking_process_is_running, variant)
        self.matchmaking_process = multiprocessing.Process(target=self.matchmaking.start)
        self.matchmaking_process.start()


class Autocompleter:
    def __init__(self, options: list[str]) -> None:
        self.options = options

    def complete(self, text: str, state: int) -> str | None:
        if state == 0:
            if text:
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:
                self.matches = self.options[:]

        try:
            return self.matches[state]
        except IndexError:
            return None


if __name__ == '__main__':
    ui = UserInterface()
    ui.start()