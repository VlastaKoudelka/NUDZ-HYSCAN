from functions import *
from psychopy.hardware import keyboard
from pylsl import StreamInfo, StreamOutlet
from save_object import SaveObject
import pylsl

def main():
    # global outlet, markers, main_time
    # set lsl communication

    info = StreamInfo("TG_EEG_markers", "Markers", 1, 0, "string", "tg_eeg_channel")
    outlet = StreamOutlet(info)  # Broadcast the stream.

    # This is not necessary but can be useful to keep track of markers and the
    # events they correspond to.
    markers = ['ExStart','CueInv','SendInv','ShowInv','RepCue','SendRep','ShowRep','ShowTot','test']



    N_trials = 15

    investor_cash = 10

    inv_cum_cash = investor_cash
    trst_cum_cash = 0
    investments = []
    repayments = []
    investor_rt = []
    trustee_rt = []


    var_name = ['inv_cum_cash', 'trst_cum_cash', 'investment', 'repayment', 'investor_rt', 'trustee_rt', 'time']
    save_folder = 'hsc_test'
    file_name = 'test_dyad'
    save_obj = SaveObject(var_name, save_folder, file_name, save_time = False)


    investor_scr = visual.Window(screen = 0,pos = (0, 0),size= (1920,1120), color = 'black', fullscr = 0)
    trustee_scr = visual.Window(screen = 1,pos = (0, 0),size = (1920,1120), color = 'black', fullscr = 0)

    investor_kb = keyboard.Keyboard()


    intro_text_investor = 'Vítejte v Trust game!\n' \
                    'Každé kolo obdržíte fixní počet peněz (' + str(investor_cash) + ' jednotek), které můžete investovat ' \
                    '(investovat lze 0 až ' + str(investor_cash) + ')\n\n' \
                    'Bankéř vám na základě svého uvážení zašle část vaší investice zpět.' \
                    ' Výdělky se každé kolo kumulativně sčítají vám i bankéři.'

    intro_text_trustee = 'Vítejte v Trust game!\n' \
                          'Každé kolo obdržíte od investora investici (třikrát navýšenou).\n\n' \
                          'Můžete se rozhodnout, jak velkou část investice zašlete zpátky.' \
                          ' Výdělky se každé kolo kumulativně sčítají vám i investorovi.'

    main_time = core.Clock()
    outlet.push_sample(['ExStart']) # Send sls triger

    intro_stim = visual.TextStim(win=investor_scr, text=intro_text_investor, color="yellow", pos=(0, 0), height=0.1, wrapWidth=1.4, alignText='left')
    intro_stim.draw()
    investor_scr.flip()

    intro_stim.win = trustee_scr
    intro_stim.text = intro_text_trustee
    intro_stim.draw()
    intro_stim.win.flip()

    core.wait(15) #15






    for i in range(0, N_trials):

        outlet.push_sample(['CueInv'])

        save_obj.clear()
        # cue to invest
        intro_stim.alignText = 'center'
        intro_stim.wrapWidth = 1.2

        intro_stim.win = trustee_scr # during investing step trustee's screen is blank
        intro_stim.text = '+'
        intro_stim.color = 'red'
        intro_stim.draw()
        intro_stim.win.flip()

        intro_stim.win = investor_scr
        intro_stim.text = 'Nyní můžete investovat!'
        intro_stim.color = 'yellow'
        intro_stim.draw()
        intro_stim.win.flip()
        core.wait(2) #4

        static_sentence = "Můžete investovat 0 až " + str(investor_cash) + '. \n Chci investovat: '

        investing_stim = visual.TextStim(win = investor_scr, text=static_sentence, color="yellow", pos=(0, 0), height=0.1, wrapWidth=1.2, alignText='center',)

        resp, rt = get_keyboard_response(investing_stim, investor_kb, investor_cash, outlet, markers, 'investor')

        save_obj.place({'investment': resp, 'investor_rt': rt, 'time': main_time.getTime()})

        investments.append(resp)
        investor_rt.append(rt)
        print(rt)
        # blank

        intro_stim.win = trustee_scr # during investing step trustee's screen is blank
        intro_stim.text = '+'
        intro_stim.color = 'red'
        intro_stim.draw()
        intro_stim.win = investor_scr
        intro_stim.draw()
        intro_stim.win.flip()

        core.wait(4) # 8

        # reveal investment to both

        # erase crossmark
        intro_stim.text = ''
        intro_stim.draw()
        intro_stim.win.flip()

        intro_stim.win = trustee_scr
        intro_stim.draw()
        intro_stim.win.flip()

        reveal_investment(investor_scr, investor_cash - investments[i], investments[i], 0)

        outlet.push_sample(['ShowInv'])
        investor_scr.flip()

        reveal_investment(trustee_scr, investor_cash - investments[i], investments[i], 0)
        trustee_scr.flip()


        core.wait(5) #10

        # blank

        intro_stim.win = trustee_scr # during investing step trustee's screen is blank
        intro_stim.text = '+'
        intro_stim.draw()
        intro_stim.win.flip()

        intro_stim.win = investor_scr
        intro_stim.draw()
        intro_stim.win.flip()

        core.wait(4)


        # cue to repay

        intro_stim = visual.TextStim(win=investor_scr, text='+', color="red", pos=(0, 0), height=0.1, wrapWidth=1.2, alignText='center')
        intro_stim.draw()

        outlet.push_sample(['RepCue'])
        investor_scr.flip()

        text = 'Investice ' + str(investments[i]) + ' x 3 = ' + str(3*investments[i]) + '.\n' + 'Vrátit (0 až ' + str(3*investments[i]) + '): '


        repayment_stim = visual.TextStim(win = trustee_scr, text=text, color="yellow", pos=(0, 0), height=0.1, wrapWidth=1.2, alignText='center',)


        resp, rt = get_keyboard_response(repayment_stim, investor_kb, 3 * investments[i], outlet, markers, 'receiver')
        save_obj.place({'repayment': resp, 'trustee_rt': rt, 'time': main_time.getTime()})

        repayments.append(resp)
        trustee_rt.append(rt)
        print(rt)

        # blank

        intro_stim.win = trustee_scr  # during investing step trustee's screen is blank
        intro_stim.color = 'red'
        intro_stim.text = '+'
        intro_stim.draw()
        intro_stim.win.flip()

        intro_stim.win = investor_scr
        intro_stim.draw()
        intro_stim.win.flip()

        core.wait(4)

        # repayment revealed

        intro_stim.text = ''
        intro_stim.draw()
        intro_stim.win.flip()

        intro_stim.win = trustee_scr
        intro_stim.draw()
        intro_stim.win.flip()

        reveal_investment(investor_scr, 3*investments[i] - repayments[i], repayments[i], 'trustee')

        outlet.push_sample(['ShowRep'])
        investor_scr.flip()

        reveal_investment(trustee_scr, 3*investments[i] - repayments[i], repayments[i], 'trustee')
        trustee_scr.flip()

        core.wait(5)

        # blank

        intro_stim.win = trustee_scr  # during investing step trustee's screen is blank
        intro_stim.text = '+'
        intro_stim.draw()
        intro_stim.win.flip()

        intro_stim.win = investor_scr
        intro_stim.draw()
        intro_stim.win.flip()

        core.wait(4)

        # show totals

        intro_stim.text = ''
        intro_stim.draw()
        intro_stim.win.flip()

        intro_stim.win = trustee_scr
        intro_stim.draw()
        intro_stim.win.flip()



        inv_cum_cash += -investments[i] + repayments[i]
        trst_cum_cash += 3*investments[i] - repayments[i]

        save_obj.place({'inv_cum_cash': inv_cum_cash, 'trst_cum_cash': trst_cum_cash, 'time': main_time.getTime()})

        reveal_investment(investor_scr,inv_cum_cash, trst_cum_cash, 'summary')

        outlet.push_sample(['ShowTot'])
        investor_scr.flip()

        reveal_investment(trustee_scr,inv_cum_cash, trst_cum_cash, 'summary')
        trustee_scr.flip()

        core.wait(5)

        # blank

        intro_stim.win = trustee_scr  # during investing step trustee's screen is blank
        intro_stim.text = '+'
        intro_stim.draw()
        intro_stim.win.flip()

        intro_stim.win = investor_scr
        intro_stim.draw()
        intro_stim.win.flip()

        core.wait(3) #np.random.uniform(12, 42, 1)

    investor_scr.close()
    trustee_scr.close()
    core.quit()

if __name__ == "__main__":
    main()


