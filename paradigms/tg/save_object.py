import os
import csv
from time import time, sleep
from typing import Any

class SaveObject(object):
    def __init__(self, var_names: list[str], save_folder: str, filename: str,
                 save_time: bool = True, reset_cvs: bool = True) -> None:
        """Hyperscanning save object.

        Args:
            var_names (list[str]): List of variable names.
            save_folder (str): Save folder
            filename (str): Given experiment name
            save_time (bool, optional): Save current time in addition to rest of variables. Defaults to True.
            reset_cvs (bool, optional): Delete existing csv upon resetting of the experiment. Defaults to True.
        """

        # Create save folder
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
    
        # Variables
        self.keys = var_names
        self.vars = {name: None for name in var_names}
        
        # Path handling
        self.save_fodler = save_folder
        self.filename = filename
        
        # Time handling
        self.save_time = save_time
        self.start_time = time()
        
        # Reset
        self.reset_csv = reset_cvs
        self.n_calls = 0
        
    def _save(self) -> None:
        self.n_calls += 1
        filepath = f"{os.path.join(self.save_fodler, self.filename)}.csv"
        columns = self.keys
         
        # Compute time if needed
        if self.save_time:
            columns.insert(0, "time")
            current_time = time()
            experiment_time = current_time - self.start_time

        # Reset csv
        if os.path.exists(filepath) and self.reset_csv and self.n_calls == 1:
            os.remove(filepath)

        # Write header file
        if not os.path.exists(filepath):
            with open(filepath, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                    
        # Write data
        with open(filepath, mode="a", newline="") as f:
            writer = csv.writer(f)
            data = self.vars.values()
            if self.save_time:
                data = list(data)
                data.insert(0, experiment_time)
            writer.writerow(data)
        
    def clear(self):
        self.vars = {k: None for k in self.vars.keys()}
    def place(self, changes: dict[str, Any]) -> None:
        # Make sure, variable names match
        for key in changes.keys():
            assert key in self.keys, f"{key} not in saved keys ({self.keys})."
        
        # Rewrite current variables
        for k, v in changes.items(): self.vars[k] = v
        
        self._save()
        

if __name__ == "__main__":
    var_name = ["a", "b", "c"]
    save_folder = "out"
    filename = "test_name"
    save_obj = SaveObject(var_name, save_folder, filename)
    
    for i in range(5):
        data = {"a": i + 1, "b": i + 2.0, "c": f"abc={i + 3}"}
        save_obj.place(data)
        sleep(0.05)