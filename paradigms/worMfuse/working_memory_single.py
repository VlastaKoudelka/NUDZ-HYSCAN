import os
import csv
from psychopy import core, visual, event
import numpy as np
import matplotlib.pyplot as plt
import time
from pylsl import StreamInfo, StreamOutlet


class WorkingMemory(object):
    def __init__(self, n_trials: int = 120, pause: int = 15, pause_time: int = 15,
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
        self.time_log_A = []
        self.time_log_B = []

        self.info = StreamInfo("WM_EEG_markers", "Markers", 1, 0, "string", "tg_eeg_channel")
        self.outlet = StreamOutlet(self.info)
        
        self._show_init_prompt()
    
    def _show_init_prompt(self) -> None:
        text_A = visual.TextStim(win=self.window_A, text="Calculate the result and enter the corresponding number [0-9]", color="white")
        text_A.draw()
        self.window_A.flip()
        text_B = visual.TextStim(win=self.window_B, text="Calculate the result and enter the corresponding number [0-9]", color="white")
        text_B.draw()
        self.window_B.flip()
        core.wait(5)
    
    def _generate_number_sequence(self, n_trials: int) -> tuple[list[int], list[int]]:
        show_numbers: list[int] = []
        differences: list[int] = []
        np.random.seed(0)
        for _ in range(n_trials):
            N = np.random.randint(0, 10)
            while True:
                D = np.random.randint(-N, 9-N)
                if D != 0: break
            show_numbers.append(N)
            differences.append(D)
        return show_numbers, differences    

    def _show_text(self, is_A_active: bool, N: int, D: int) -> None:
        if is_A_active:
            text = visual.TextStim(win=self.window_B, text="Wait", color="white")
            text.draw()
            self.window_B.flip()
            text = visual.TextStim(win=self.window_A, text=f"{N}", color="yellow")
            text.draw()
            self.window_A.flip()
            core.wait(0.75)
            text = visual.TextStim(win=self.window_A, text=f"", color="yellow")
            text.draw()
            self.window_A.flip()
            core.wait(1.0)
            text = visual.TextStim(win=self.window_A, text=f"{D:+d}", color="white")
            text.draw()
            self.window_A.flip()
        else:
            text = visual.TextStim(win=self.window_A, text="Wait", color="white")
            text.draw()
            self.window_A.flip()
            text = visual.TextStim(win=self.window_B, text=f"{N}", color="yellow")
            text.draw()
            self.window_B.flip()
            core.wait(0.75)
            text = visual.TextStim(win=self.window_B, text=f"", color="yellow")
            text.draw()
            self.window_B.flip()
            core.wait(1.0)
            text = visual.TextStim(win=self.window_B, text=f"{D:+d}", color="white")
            text.draw()
            self.window_B.flip()
            
        
    def _log(self, is_A_active: bool, time_start: float) -> None:
        if is_A_active:
            self.time_log_A.append(time.time() - time_start)
            self.outlet.push_sample(['Apress'])
        else:
            self.time_log_B.append(time.time() - time_start)
            self.outlet.push_sample(['Bpress'])
            
    def _wait_press(self, is_A_active: bool, time_start: float) -> None:
        keys_num = [str(i) for i in range(10)]
        keys_num.extend([f"num_{k}" for k in keys_num])
        while True:
            keys = event.getKeys()
            if keys:
                if keys[0] == 'q':
                    core.quit()
                elif keys[0] in keys_num:
                    break
        self._log(is_A_active, time_start)
        
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
        

    def pause_function(self, is_A_active: bool, i: int) -> bool:
        if i == 0: return is_A_active
        if i % self.pause != 0: return is_A_active
        
        if is_A_active:
            text = visual.TextStim(win=self.window_A, text="Wait", color="white")
            text.draw()
            self.window_A.flip()
            text = visual.TextStim(win=self.window_B, text="", color="white")
            text.draw()
            self.window_B.flip()
            is_A_active = False
        else:
            text = visual.TextStim(win=self.window_B, text="Wait", color="white")
            text.draw()
            self.window_B.flip()
            text = visual.TextStim(win=self.window_A, text="", color="white")
            text.draw()
            self.window_A.flip()
            is_A_active = True
        
        return is_A_active
    
    def play(self) -> None:
        time_start = time.time()
        self.outlet.push_sample(['expStart'])
        is_A_active = True
        for i, (N, D) in enumerate(zip(self.show_numbers, self.differences)):
            self._show_text(is_A_active, N, D)
            ti = time.time()
            self._wait_press(is_A_active, time_start)
            if is_A_active:
                text_A = visual.TextStim(win=self.window_A, text="", color="white")
                text_A.draw()
                self.window_A.flip()
            else:
                text_B = visual.TextStim(win=self.window_B, text="", color="white")
                text_B.draw()
                self.window_B.flip()
            # Simulate partner wait time
            core.wait(min(time.time() - ti, 2))
            is_A_active = self.pause_function(is_A_active, i)

        self.outlet.push_sample(['expEnd'])
        self._save()
        self._close()
        
    
if __name__ == "__main__":
    wm = WorkingMemory(save_folder="wm_out_single", filename="test_file")
    wm.play()