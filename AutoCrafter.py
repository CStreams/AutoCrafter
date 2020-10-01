#! python3
import pyperclip
import random
import os
import time
import pyautogui
import re
import ItemEvaluators
from collections import defaultdict
import win32gui
import CraftLocations
import collections
from pynput import keyboard

# TODO do something with sleep statements (probably just make them a set time instead of rand uniform)
# probably a more human solution looking as average time per action or sequence they would line up too well
# hyperplanes >.< todo see if pythons random suffers

#todo fix hacky item name lookup
possible_names = {'Fluted Bascinet': 'Helm'}

influences = ['Shaper', 'Elder', 'Crusader', 'Redeemer', 'Hunter', 'Warlord']

def parseClipboard(item):

    item_sections = item.split('--------')
    item_data = defaultdict(list)
    used_sections = set()
    for i, section in enumerate(item_sections):
        for line in section.split('\r\n'):
            # Todo name lookup properly and error if not found
            # most of these need to be start of line matches as this can catch mods
            # todo parse these mods into nice formats like Rarity: Normal -> CONSTS.NORMAL etc
            # TODO weapons dont work as the base values are not taken e.g. weapon range, base aps
            # Sould probably be if line.startswith and not if x in y
            for name in possible_names.keys():
                if name in line:
                    if (temp := possible_names[name]) is not None:
                        item_data['name'] = temp
                    else:
                        exit('How did we get here?')

            if 'Rarity:' in line:
                item_data['rarity'] = line
                used_sections.add(i)
            if 'Requirements:' in line:
                item_data['requirements'].append(line)
                used_sections.add(i)
            if 'Item Level:' in line:
                item_data['itemlevel'].append(line)
                used_sections.add(i)
            if '(implicit)' in line:
                item_data['implicit'].append(line)
                used_sections.add(i)
            if '(enchant)' in line:
                item_data['enchant'].append(line)
                used_sections.add(i)
            if 'Sockets:' in line:
                socket_extract = re.match(r'Sockets: (.{0,12}) ', line).group(1)
                curryr = lambda f: lambda x: lambda y: f(y, x)
                item_data['links'] = max(map(curryr(str.count)('-'), socket_extract.split(' ')))
                item_data['sockets'] = dict(collections.Counter(socket_extract.replace(' ', '').replace('-', '')))  # tad ugly
                used_sections.add(i)

            if 'Armour:' in line:
                item_data['armour'].append(line)
                used_sections.add(i)
            if 'Energy Shield:' in line:
                item_data['energyshield'].append(line)
                used_sections.add(i)
            if 'Evasion Rating:' in line:
                item_data['evasionrating'].append(line)
                used_sections.add(i)

            if 'Abyss' == line:
                #item_data['abyss'] = True
                used_sections.add(i)

            if 'Map Tier:' in line:  # Map Check
                used_sections.add(i)

            if 'Corrupted' == line:
                item_data['corrupted'].append(line)
                used_sections.add(i)

            for influence in influences:
                if influence in line:
                    item_data['influence'].append(line)
                    used_sections.add(i)

    item_sections = [_ for i, _ in enumerate(item_sections) if i not in used_sections]  # remove used item sections

    if item_data['rarity'] != 'Rarity: Normal':
        # todo mods lookup and parsed into something better than the mod string
        item_data['mods'] = list(filter(None, item_sections.pop(0).split('\r\n')))
    else:
        item_data['mods'] = []

    return item_data


def applyCraft(craft_location, slot):
    pyautogui.moveTo(craft_location[0], craft_location[1])
    pyautogui.rightClick()
    time.sleep(random.uniform(0.053, 0.08))
    pyautogui.moveTo(slot[0], slot[1])
    pyautogui.leftClick()

def fossilPickup(fossil, slot, craft_tab):
    fossil_pos = craft_tab.getCurrencyPos(fossil)

    pyautogui.moveTo(fossil_pos[0][0], fossil_pos[0][1])
    pyautogui.keyDown('shift')
    time.sleep(0.05)
    pyautogui.click()
    pyautogui.keyUp('shift')
    time.sleep(random.uniform(0.05, 0.09))

    pyautogui.moveTo(fossil_pos[1][0], fossil_pos[1][1])  # checkbox click todo fix it for when there is only one left
    pyautogui.click()
    time.sleep(random.uniform(0.05, 0.09))
    pyautogui.moveTo(slot[0], slot[1])
    pyautogui.click()


def setupResonator(fossils, craft_tab):
    resonator = craft_tab.resonatorNeeded(fossils)
    fossilPickup(resonator, craft_tab.FOSSIL_SLOT, craft_tab)

    for fossil, resonator_slot in zip(fossils, resonator[2]):
        fossilPickup(fossil, resonator_slot, craft_tab)

def fossCrafter(item_data, slot, craft_tab, evaluation=None):
    setupResonator(craft_tab.FOSSILS_USING, craft_tab)

    applyCraft(craft_tab.FOSSIL_SLOT, craft_tab.ITEM_SLOT)


def altCrafter(item_data, slot, craft_tab=CraftLocations.CurrencyTab(), evaluation=None):  # todo move these elsewhere
    if item_data['rarity'] == 'Rarity: Normal':
        applyCraft(craft_tab.getTransmute(), slot)
    elif item_data['rarity'] == 'Rarity: Magic':
        if len(item_data['mods']) == 1:
            applyCraft(craft_tab.getAugmentation(), slot)
        elif evaluation[1]:
            applyCraft(craft_tab.getRegal(), slot)
        else:
            applyCraft(craft_tab.getAlteration(), slot)
    elif item_data['rarity'] == "Rarity: Rare":
        applyCraft(craft_tab.getScour(), slot)


def chanceCrafter(item_data, slot, craft_tab=CraftLocations.CurrencyTab(), evaluation=None):
    if item_data['rarity'] != 'Rarity: Normal':
        applyCraft(craft_tab.getScour(), slot)
    else:
        applyCraft(craft_tab.getChance(), slot)


def chaosCrafter(item_data, slot, craft_tab=CraftLocations.CurrencyTab(), evaluation=None):
    if item_data['rarity'] == 'Rarity: Normal':
        applyCraft(craft_tab.getTransmute(), slot)
    elif item_data['rarity'] == 'Rarity: Magic':
        applyCraft(craft_tab.getRegal(), slot)
    elif item_data['rarity'] == "Rarity: Rare":
        applyCraft(craft_tab.getChaos(), slot)

def sixLinkCrafter(item_data, slot, craft_tab=CraftLocations.CurrencyTab(), evaluation=None):
    applyCraft(craft_tab.getFusing(), slot)


def craftChecker(slot, crafter, craft_tab=None, evaluator=None, filewriter=None):
    # todo possible dc detection maybe and checks for crafting mats
    # make user enter amounts they have and log usage

    pyautogui.moveTo(slot[0], slot[1])
    pyautogui.hotkey('ctrl', 'c')

    time.sleep(random.uniform(0.1, 0.13))
    item_data = parseClipboard(pyperclip.paste())
    result = evaluator(item_data)

    if filewriter is not None:
        filewriter.write(str(item_data) + '\t' + str(result[0]) + '\t' + str(result[1]) + '\n')

    if result[0] and not result[1]: # not result[1] being to continue crafting if hit (magic items etc) named tuples please
        print('Item Crafted', item_data['name'])
        return

    crafter(item_data, slot, craft_tab, result)

    craftChecker(slot, crafter, craft_tab, evaluator, filewriter)


def windowEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))


def onPress(key):
    try:
        k = key.char
    except:
        if key.name == 'esc':
            os._exit(1)


def craft(inventory, crafter, craft_tab=CraftLocations.CurrencyTab(), evaluator=ItemEvaluators.Items().evaluate, write=False):
    lis = keyboard.Listener(on_press=onPress)  # kill on keypress
    lis.start()

    # bring window to the front
    top_windows = []
    win32gui.EnumWindows(windowEnumerationHandler, top_windows)
    for window in top_windows:
        if "path of exile" in window[1].lower():
            win32gui.ShowWindow(window[0], 5)
            win32gui.SetForegroundWindow(window[0])
            break
    else:
        exit('NoWindowFound')

    time.sleep(2)

    filewriter = None
    if write:
        filewriter = open('CraftLog/' + time.strftime("%Y%m%d-%H%M%S"), 'w')

    while slot := next(inventory):
        craftChecker(slot=slot, crafter=crafter, craft_tab=craft_tab, evaluator=evaluator, filewriter=filewriter)
        inventory.deactivateLastSlot()

    if filewriter is not None:
        filewriter.close()


def main():  # TODO seperate this functionality out to files its a mess
    inventory = CraftLocations.Inventory()
    active = [[0, 0]]
    inventory.activateSlots(active)
    craft(inventory, altCrafter, write=True)
    exit('Done')


if __name__ == "__main__":
    main()
