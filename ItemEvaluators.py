import re
from collections import defaultdict
import ItemEvals.EyeJewels as EJ
import ItemEvals.Jewels as J

class Items:
    ITEMS = defaultdict(list)
    sockets = defaultdict(list)
    RARITIES = {"Rarity: Normal": 0, "Rarity: Magic": 1, "Rarity: Rare": 2, "Rarity: Unique": 3}


    def __init__(self):

        self.ITEMS.update(EJ.items)  # todo should probably make a interface that finds all the files in /ItemEvals and imports them
        self.ITEMS.update(J.items)  # possible dead mod list where if it is rolled scour item


    def modsMatch(self, regex, line):
        if (temp := re.match(regex, line, flags=0)) is not None:
            return int(temp.group(1))
        return 0

    def evaluateResists(self, mods):
        cold = 0
        lightning = 0
        fire = 0
        chaos = 0
        allres = 0
        for mod in mods:  # todo implement hybrid res
            allres +=       int(self.modsMatch(r"\+(.{0,5})% to all Elemental Resistances", mod))
            cold +=         int(self.modsMatch(r"\+(.{0,5})% to Cold Resistance", mod))
            lightning +=    int(self.modsMatch(r"\+(.{0,5})% to Lightning Resistance", mod))
            fire +=         int(self.modsMatch(r"\+(.{0,5})% to Fire Resistance", mod))
            chaos +=        int(self.modsMatch(r"\+(.{0,5})% to Chaos Resistance", mod))

        return (cold + lightning + fire) + allres * 3 + chaos  # might want to separate these later

    def evaluate(self, item_data):

        if type(item_data['name']) == list:  # not ideal but its how it is
            print('No evals supplied')
            exit('NoEval')

        if item_data['rarity'] == "Rarity: Unique":  # possibly bad if using this to divine uniques might want a waited sum eval for that anyway
            return True, False

        for item_match in self.ITEMS[item_data['name']]:

            if item_match['rarity'] > self.RARITIES[item_data['rarity']]:  # dont want to run 4/6 stat items against magic level mods
                print('should be here', item_match)
                continue

            if self.evaluateResists(item_data['mods']) < item_match['resistances']:
                continue

            prefixcount = 0
            for x in item_match['prefix'] or []:
                for mod in item_data['mods'] or []:
                    if self.modsMatch(x[0], mod) >= int(x[1]): #  should probably make it default to int but this is fine
                        prefixcount += 1

            if prefixcount < item_match['matchprefix'] and item_match['matchsum'] == 0:
                continue

            suffixcount = 0
            for x in item_match['suffix'] or []:
                for mod in item_data['mods'] or []:
                    if self.modsMatch(x[0], mod) >= int(x[1]):
                        suffixcount += 1

            if suffixcount < item_match['matchsuffix'] and item_match['matchsum'] == 0:
                continue

            if item_match['matchsum'] != 0 and prefixcount + suffixcount < item_match['matchsum']:  # fail on the case where there is a matchsum and its not met
                continue

            return True, item_match['continue']

        return False, item_match['continue']

    def socketEval(self, item_data):  # could probably bake this into ItemEvaluators. evaluate at some point
        for sockets in self.sockets:  # could also use auto chrome and six socket
            if item_data['links'] + 1 >= sockets['links']:  # +1 as one - is usually called a 2 link W-W = 2 W-W-W = 3
                return True, False

        return False, False
