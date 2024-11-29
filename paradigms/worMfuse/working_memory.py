import os
import csv
from psychopy import core, visual, event
import numpy as np
import matplotlib.pyplot as plt
import time
from pylsl import StreamInfo, StreamOutlet


class WorkingMemory(object):
    def __init__(self, n_trials: int = 120, pause: int = 30, pause_time: int = 15,
                 save_folder: str = "out", filename: str = "default_filename") -> None:

        # Experiment design
        self.n_trials = n_trials
        self.pause = pause
        self.pause_time = pause_time
        
        # Data handling
        self.save_folder = save_folder
        self.filename = filename
        
        # Generate the random sequence
        self.show_numbers, self.differences = self._generate_number_sequence(n_trials)
        # Initialize windows
        self.window_A = visual.Window(screen=0, size=(1920, 1120), pos=(0, 0), color='black', fullscr=0)
        self.window_B = visual.Window(screen=1, size=(1920, 1120), pos=(0, 0), color='black', fullscr=0)
        
        # self.window_A = visual.Window(screen=0, size=(800, 800), pos=(0, 0), color='black', fullscr=False)
        # self.window_B = visual.Window(screen=0, size=(800, 800), pos=(800, 0), color='black', fullscr=False)
        
        self.time_log_A = []
        self.time_log_B = []

        self.info = StreamInfo("WM_EEG_markers", "Markers", 1, 0, "string", "tg_eeg_channel")
        self.outlet = StreamOutlet(self.info)
        
        self._show_init_prompt()
    
    def _show_init_prompt(self) -> None:
        text_A = visual.TextStim(win=self.window_A, text="Say the result of the calculation, based on the difference. First number is 0. You go first. Press 'a'  when you have the answer.", color="white")
        text_B = visual.TextStim(win=self.window_B, text="Say the result of the calculation, based on the difference. First number is 0. You go second. Press 'l' when you have the answer.", color="white")
        text_A.draw()
        text_B.draw()
        self.window_A.flip()
        self.window_B.flip()
        core.wait(5)
    
    def _generate_number_sequence(self, n_trials: int) -> tuple[list[int], list[int]]:
        np.random.seed(0)
        n_blocks = n_trials // self.pause
        n_trials_per_block = int(n_trials / n_blocks)
        SN = []
        DIFF = []
        for n in range(n_blocks):
            number = 0
            show_numbers: list[int] = []
            differences: list[int] = []
            for _ in range(n_trials_per_block):
                show_numbers.append(number)
                D = np.random.randint(-number, 10 - number)
                while D == 0:
                    D = np.random.randint(-number, 10 - number)
                differences.append(D)
                number += D
            SN.extend(show_numbers)
            DIFF.extend(differences)
        return SN, DIFF    
    
    def _show_text(self, i: int, D: int) -> None:
        if i % 2:
            text_A = visual.TextStim(win=self.window_B, text=f"{D:+d}", color="white")
            text_B = visual.TextStim(win=self.window_A, text="", color="white")
        else:
            text_A = visual.TextStim(win=self.window_B, text="", color="white")
            text_B = visual.TextStim(win=self.window_A, text=f"{D:+d}", color="white")
        
        text_A.draw()
        text_B.draw()
        self.window_A.flip()
        self.window_B.flip()
    
    def _log(self, i: int, time_start: float) -> None:
        if i % 2 == 0:
            self.outlet.push_sample(['lpress'])
            self.time_log_A.append(time.time() - time_start)
        else:
            self.outlet.push_sample(['apress'])
            self.time_log_B.append(time.time() - time_start)
            
    def _wait_press(self, i: int, time_start: float) -> None:
        while True:
            keys = event.getKeys()
            if keys:
                if keys[0] == 'q':
                    core.quit()
                if i % 2 == 0 and keys[0] == "l":
                    break
                elif i % 2 == 1 and keys[0] == "a":
                    break
        self._log(i, time_start)
    
    def _close(self) -> None:
        self.window_A.close()
        self.window_B.close()
        core.quit()
        
    def _save(self) -> None:
        if not os.path.exists(self.save_folder):
            os.mkdir(self.save_folder)
        filepath = f"{os.path.join(self.save_folder, self.filename)}.csv"
        
        with open(filepath, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Times_A", "Times_B"])
            for tA, tB in zip(self.time_log_A, self.time_log_B):
                writer.writerow([tA, tB])
        
        
    def pause_function(self, i: int) -> None:
        if i == 0: return
        # TODO Fix indexing
        if (i + 1) % self.pause != 0: return

        flag = 0
        for t in range(self.pause_time):
            if self.pause_time - t > 5:
                if flag == 0:
                    self.outlet.push_sample(['pauseStart'])
                    flag = 1
                pause_str = "Pause" + t % 4 * "."
                text_A = visual.TextStim(win=self.window_A, text=pause_str.ljust(9), color="white")
                text_B = visual.TextStim(win=self.window_B, text=pause_str.ljust(9), color="white")


            else:
                text_A = visual.TextStim(win=self.window_A, text=f"First number is again 0\nResuming in {self.pause_time - t}", color="white")
                text_B = visual.TextStim(win=self.window_B, text=f"First number is again 0\nResuming in {self.pause_time - t}", color="white")
            text_A.draw()
            text_B.draw()


            self.window_A.flip()
            self.window_B.flip()
            if t < self.pause_time - 1:
                core.wait(1)

        self.outlet.push_sample(['pauseEnd'])
    
    def play(self) -> None:
        time_start = time.time()
        self.outlet.push_sample(['expStart'])
        for i, D in enumerate(self.differences):
            self._show_text(i, D)
            self._wait_press(i, time_start)
            self.pause_function(i)

        self.outlet.push_sample(['expEnd'])
        self._save()
        self._close()
        

if __name__ == "__main__":
    wm = WorkingMemory(save_folder="wm_out", filename="test_file")
    wm.play()