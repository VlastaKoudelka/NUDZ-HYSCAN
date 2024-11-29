from pylsl import StreamInfo, StreamOutlet
from psychopy import visual, core, event
import winsound

def lsl_comm(name):
    info = StreamInfo(name, "Markers", 1, 0, "string", "tg_eeg_channel")
    outlet = StreamOutlet(info)  # Broadcast the stream.
    return outlet

def show_cross(win):

    cross_stim = visual.TextStim(win=win, text='+', color="red", pos=(0, 0), height=0.1,
                                 wrapWidth=1.2, alignText='center', )
    cross_stim.draw()
    cross_stim.win.flip()


def show_prompt(win, text):
    prompt_stim = visual.TextStim(win=win, text=text, color="yellow", pos=(0, 0), height=0.1,
                                 wrapWidth=1.2, alignText='center', )
    prompt_stim.draw()
    prompt_stim.win.flip()

def main():

    outlet = lsl_comm("TG_EEG_markers")

    p1_scr = visual.Window(screen=0, pos=(0, 0), size=(1920, 1120), color='black', fullscr=0)
    p2_scr = visual.Window(screen=1, pos=(0, 0), size=(1920, 1120), color='black', fullscr=0)

    N_trials = 50


    intro_text = 'Gaze exchange\n' \
                 'Pravidla: Na začátku koukáte Vy i druhý hráč na fixační kříž. Po zaznění tónu koukají hráči na sebe.\n' \
                 'Po opětovném zaznění tónu koukají hráči opět na fixační kříž'

    intro_stim = visual.TextStim(win=p1_scr, text=intro_text, color="yellow", pos=(0, 0), height=0.1,
                                 wrapWidth=1.4, alignText='left')
    intro_stim.draw()



    outlet.push_sample(['ExStart'])
    p1_scr.flip()

    intro_stim.win = p2_scr
    intro_stim.text = intro_text
    intro_stim.draw()
    intro_stim.win.flip()



    core.wait(10)

    outlet.push_sample(['Cross'])
    show_cross(p1_scr)
    show_cross(p2_scr)

    core.wait(3)


    for i in range(0, N_trials):


        winsound.Beep(1000, 250)
        outlet.push_sample(['Stare'])
        show_prompt(p1_scr, 'Dívejte se na spoluhráče.')
        show_prompt(p2_scr, 'Dívejte se na spoluhráče.')
        core.wait(5)

        keys = event.getKeys()
        if 'q' in keys:
            core.quit()  # Immediately exit the program

        winsound.Beep(1000, 250)
        outlet.push_sample(['Cross'])
        show_cross(p1_scr)
        show_cross(p2_scr)

        core.wait(5)

    core.quit()


if __name__ == "__main__":
    main()