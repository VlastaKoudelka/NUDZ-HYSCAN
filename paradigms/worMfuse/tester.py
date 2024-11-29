from psychopy import visual, core
from psychopy.iohub import launchHubServer

# Start iohub for multiple device handling
iohub = launchHubServer()

# List available devices (check device names in the console)A    D is needed

# Create a window
win = visual.Window(size=(800, 600), color="black", units="pix")

# Text stimuli for each keyboard's action
text1 = visual.TextStim(win, text="Keyboard 1 Pressed", pos=(0, 0), color="white")
text2 = visual.TextStim(win, text="Keyboard 2 Pressed", pos=(0, 0), color="red")

# Flag to toggle between displays
display_text1 = True

# Main loop to wait for spacebar press and alternate actions
while True:
    # Check for spacebar press from Keyboard 1
    keys1 = keyboard1.getPresses(keys=["space"])
    if keys1:
        display_text1 = not display_text1  # Toggle display flag
        print("Spacebar pressed on Keyboard 1")

    # Check for spacebar press from Keyboard 2
    keys2 = keyboard2.getPresses(keys=["space"])
    if keys2:
        display_text1 = not display_text1  # Toggle display flag
        print("Spacebar pressed on Keyboard 2")

    # Draw text based on the toggle
    if display_text1:
        text1.draw()
    else:
        text2.draw()
    win.flip()

    # Break loop with escape key from any keyboard
    if "escape" in [key.key for key in keys1] or "escape" in [key.key for key in keys2]:
        break

# Close the window
win.close()
core.quit()
