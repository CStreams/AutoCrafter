import random

class CurrencyTab:

    # pixel x, y, amount available
    TRANSMUTE =     [45,    275,    100]
    ALTERATION =    [95,    270,    100]
    AUGMENTATION =  [220,   325,    100]
    REAGAL =        [410,   270,    100]
    ALCHEMY =       [470,   270,    0]
    CHAOS =         [530,   270,    5]
    CHANCE =        [215,   270,    100]
    SCOUR =         [155,   455,    10]
    ANNUL =         [155,   270,    0]
    JEWELLER =      [100,   400,    100]
    FUSING =        [155,   400,    100]

    widthHeight = 53
    error = 20  # how close to the edges it can click this is best left above 2
    def getCurrencyPos(self, currency):
        if currency[2] == 0:
            print('Out of Currency')
            exit('No Craft Materials')
        currency[2] = currency[2] - 1
        return random.randint(currency[0] + self.error, currency[0] + self.widthHeight - self.error), \
               random.randint(currency[1] + self.error, currency[1] + self.widthHeight - self.error)

    def getTransmute(self):  # there has to be a better way
        return self.getCurrencyPos(self.TRANSMUTE)

    def getAlteration(self):
        return self.getCurrencyPos(self.ALTERATION)

    def getAugmentation(self):
        return self.getCurrencyPos(self.AUGMENTATION)

    def getRegal(self):
        return self.getCurrencyPos(self.REAGAL)

    def getChance(self):
        return self.getCurrencyPos(self.CHANCE)

    def getScour(self):
        return self.getCurrencyPos(self.SCOUR)

    def getAlchemy(self):
        return self.getCurrencyPos(self.ALCHEMY)

    def getChaos(self):
        return self.getCurrencyPos(self.CHAOS)

    def getJeweller(self):
        return self.getCurrencyPos(self.JEWELLER)

    def getFusing(self):
        return self.getCurrencyPos(self.FUSING)



class FossilTab:
    # pixel x, y, amount available
    JAGGED =        [110,   215,    10]
    DENSE =         [180,   215,    10]
    FRIDGID =       [245,   215,    10]
    ABBERANT =      [310,   215,    10]
    SCORTCHED =     [375,   215,    10]
    METALLIC =      [445,   215,    10]
    PRISTINE =      [510,   215,    10]

    BOUND =         [45,    280,    10]
    CORRODED =      [110,   280,    10]
    PERFECT =       [180,   280,    10]
    PRISMATIC =     [245,   280,    10]
    ENCHANTED =     [310,   280,    10]
    ATHERIC =       [375,   280,    10]
    LUCENT =        [445,   280,    10]
    SHUDDERING =    [510,   280,    10]


    # Resonators Location, SocketLocations
    PRIMATIVE_RESONATOR =   [510,   585,    [(390,  515)]]
    POTENT_RESONATOR =      [555,   650,    [(390,  500),   (390, 540)]]
    POWERFUL_RESONATOR =    [450,   650,    [(370,  500),   (410, 500), (410, 540)]]

    FOSSIL_SLOT =   [350,   435]
    ITEM_SLOT =     [240,   435]

    FOSSILS_USING = []

    # size of each inv slot
    widthHeight = 53  # todo half for quad tabs
    # width from the edge of the box always < widthheight
    error = 13

    active = False

    # todo remove this just make it a inventory with 1 slot instead of with the tab
    def toggleSlots(self, slot_list=None):
        self.active = True

    def deactivateLastSlot(self):
        self.active = False

    def getCurrencyPos(self, currency):
        if currency[2] == 0:
            print('Out of Currency')
            exit('No Craft Materials')
            
        if type(currency[2]) != list:
            currency[2] = currency[2] - 1

        tempx = currency[0]
        tempy = currency[1]

        if tempx < 220 / 2:  # 220 being the selection box with this corrects it when its at the edge of the screen
            tempx = tempx + (220 / 2 - tempx)

        return (
                    (
                        random.randint(currency[0] + self.error, currency[0] + self.widthHeight - self.error), \
                        random.randint(currency[1] + self.error, currency[1] + self.widthHeight - self.error)
                    ),
                    (
                        tempx + 115, tempy - 30  # + 115 & - 30 are the check box offsets
                    )
                )


    def resonatorNeeded(self, fossils):
        if len(fossils) == 1:
            return self.PRIMATIVE_RESONATOR
        elif len(fossils) == 2:
            return self.POTENT_RESONATOR
        elif len(fossils) == 3:
            return self.POWERFUL_RESONATOR

    def __next__(self):
        if self.active:
            return self.ITEM_SLOT


class Inventory:
    #todo fix these vairibles for multi tabs / more generic
    inventoryWidth = 12
    inventoryHeight = 5
    activeSlots = []
    activeSlotsCount = 0
    topLeftItem = (1275, 590)
    widthHeight = 53

    lastSlot = [-1, -1]

    error = 12

    def __init__(self):
        self.activeSlots = [[False for y in range(self.inventoryHeight)] for x in range(self.inventoryWidth)]

    def activateSlots(self, slot_l):
        self.activeSlotsCount = len(slot_l)
        for slot in slot_l:
            self.activeSlots[slot[0]][slot[1]] = True

    def moveToSlot(self, x, y):
        xCoordinate = self.topLeftItem[0] + x * self.widthHeight
        yCoordinate = self.topLeftItem[1] + y * self.widthHeight
        return random.randint(xCoordinate + self.error, xCoordinate + self.widthHeight - self.error), \
               random.randint(yCoordinate + self.error, yCoordinate + self.widthHeight - self.error)

    def deactivateLastSlot(self):
        self.activeSlots[self.lastSlot[0]][self.lastSlot[1]] = False

    def __next__(self):  # find first item in the list still needing crafted
        for x, slotList in enumerate(self.activeSlots):
            for y, _ in enumerate(slotList):
                if self.activeSlots[x][y]:
                    self.lastSlot = [x, y]
                    return self.moveToSlot(x, y)

        print('Crafting Done')  # effectively dead statements but they can stay as crafting should be stopped by then
        exit('Finished')
