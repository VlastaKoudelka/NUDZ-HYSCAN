from psychopy import visual, core
# from psychopy.hardware import keyboard
from psychopy.visual import rect
# from pylsl import StreamInfo, StreamOutlet

def get_keyboard_response(stim, kb, lim, outlet, markers, flag):

    response = ""
    rt = 0
    que = []
    static_sentence = stim.text

    kb.clock.reset()
    kb.clearEvents()
    # Main loop to capture keyboard input
    while True:
        # Update the text of sentence_stim by appending the user input to the static sentence
        stim.text = static_sentence + response

        # Draw the sentence with user input appended
        stim.draw()
        stim.win.flip()

        # Capture keys pressed by the user
        keys = kb.waitKeys(
            keyList=['num_1', 'num_2', 'num_3', 'num_4', 'num_5', 'num_6', 'num_7', 'num_8', 'num_9', 'num_0', 'return',
                     'backspace', 'lctrl', 'lshift', 'q'])
        que.append(keys[0].name)
        rt_flag = 0
        end_flag = 0
        for key in keys:

            if 'lctrl' in que and 'lshift' in que and 'q' in que:
                print("Experiment stopped by experimenter.")
                core.quit()

            if key == 'return' and response != "":  # End input when 'return' is pressed
                if flag == 'investor':
                    outlet.push_sample(['SendInv'])
                else:
                    outlet.push_sample(['SendRep'])

                end_flag = 1
                break
            elif key == 'backspace':  # Allow backspace to delete last character
                response = response[:-1]
            elif key != 'return' and key.name not in 'lctrl lshift q':  # Add the character typed by the user

                if rt_flag == 0: # Reaction time is taken at the moment when first number is writen

                    rt = key.rt
                    rt_flag = 1

                response += key.name[4:]

                if int(response) > lim:
                    response = ''

        if end_flag == 1:
            break
    return int(response), rt

def reveal_investment(window, kept: int, gave: int, cond) -> None:
    baseline_height = -0.2
    default_height = 0.5

    if kept != 0 or gave != 0:
        reveal_inv_stim_kept = visual.rect.Rect(win=window, width=0.1, height=default_height, fillColor='red', units='norm',
                                                pos=(-0.20, baseline_height + default_height/2))
        reveal_inv_stim_gave = visual.rect.Rect(win=window, width=0.1, height=default_height, fillColor='red', units='norm',
                                                pos=(0.20, baseline_height + default_height/2))

        reveal_inv_stim_kept.height = reveal_inv_stim_kept.height * (kept/(kept+gave))
        reveal_inv_stim_gave.height = reveal_inv_stim_gave.height * (gave/(kept+gave))

        reveal_inv_stim_kept.pos = (-0.20, baseline_height + reveal_inv_stim_kept.height / 2)
        reveal_inv_stim_gave.pos = (0.20, baseline_height + reveal_inv_stim_gave.height / 2)

        reveal_inv_stim_kept.draw()
        reveal_inv_stim_gave.draw()


    kept_stim = visual.TextStim(win=window, text=str(kept), color="yellow", pos=(-0.20, -0.3), height=0.1, wrapWidth=1.2, alignText='center')
    gave_stim = visual.TextStim(win=window, text=str(gave), color="yellow", pos=(0.20, -0.3), height=0.1, wrapWidth=1.2, alignText='center')
    kept_stim.draw()
    gave_stim.draw()



    help_s1 = visual.TextStim(win=window, text='Investor:', color="yellow", pos=(0, 0.8), height=0.1, wrapWidth=1.2, alignText='center')
    help_s2 = visual.TextStim(win=window, text='Ponechal', color="yellow", pos=(-0.20, 0.6), height=0.1, wrapWidth=1.2, alignText='center')
    help_s3 = visual.TextStim(win=window, text='Investoval', color="yellow", pos=(0.20, 0.6), height=0.1, wrapWidth=1.2, alignText='center')
    if cond == 'summary':
        help_s1.text = 'Zisky celkem'
        help_s2.text = 'Investor'
        help_s3.text = 'Bankéř'

    if cond == 'trustee':
        help_s1.text = 'Bankéř:'
        help_s2.text = 'Ponechal:'
        help_s3.text = 'Vrátil:'

    help_s1.draw()
    help_s2.draw()
    help_s3.draw()