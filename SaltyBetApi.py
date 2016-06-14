import requests, json


"""
This module creates a API for the online betting site http://www.saltybet.com
"""
class SaltyBetApi():

    __isAuthed = False

    """
    SaltyBetApi exposes the API and allows the user to interact with the website
    """
    def __init__(self):
        """
        Construct a new SaltyBetApi instance
        """
        self.session = requests.Session()
        self.session.head("http://www.saltybet.com")
    def logIn(self, email, password):
        """
        Log in the User
        :param email: Email of the User
        :param password: Password of the User
        :return: Status of the Login
        """
        parseString = "email=" + email.replace("@", "%40") + "&pword=" + password + "&authenticate=signin"
        requestLength = str(len(parseString))
        header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "http://www.saltybet.com/authenticate?signin=1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        req = requests.Request('POST', "http://www.saltybet.com/authenticate?signin=1", headers=header)
        prepped = req.prepare()
        prepped.body = parseString
        prepped.headers['Content-Length'] = requestLength
        resp = self.session.send(prepped)
        if "selectedplayer" in resp.text:
            self.__isAuthed = True
            return True
        else:
            return False

    def getStatus(self):
        """
        Get the current gamestate
        :return: A string with the current gamestate
        """
        return requests.get('http://www.saltybet.com/state.json').json()["status"]

    def getPlayerName(self, playernumber):
        """
        Returns the Character name associated with the generic "playerx"
        :param playernumber: The number of the player, 1 or 2
        :return: The player name, by default it will return the name of the second player
        """
        r = requests.get('http://www.saltybet.com/state.json')
        if playernumber == 1:
            return r.json()["p1name"]
        else:
            return r.json()["p2name"]

    def getDollars(self):
        if not self.__isAuthed:
            return -1
        """
        Get the current amount of SaltBucks
        :return: The amount of SaltBucks (int)
        """
        resp = self.session.get("http://www.saltybet.com/")
        startIndex = resp.text.find('id="balance">') + 13
        stringToInt = ""
        while resp.text[startIndex] != "<":
            stringToInt += resp.text[startIndex]
            startIndex += 1
        return int(stringToInt.replace(",", ""))

    def __canBet(self):
        if not self.__isAuthed:
            return False
        r = requests.get('http://www.saltybet.com/state.json')
        if r.json()["status"] == "open":
            return True
        return False

    def placeBet(self, player, wager):
        """
        Place a bet, autochecks if you can place the bet
        :param player: Either player1 or player2
        :param wager: The wager you want to put in
        :return: If placing the bet failed
        """
        if not self.__canBet():
            return False
        header = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "http://www.saltybet.com/authenticate?signin=1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36",
            "Accept": "*/*",
            "X-Requested-With":"XMLHttpRequest",
            "Origin":"http://www.saltybet.com",
            "Referer":"http://www.saltybet.com/",
            "Host":"www.saltybet.com",
            "Connection": "keep-alive",
            "Cookie": "__cfduid=" + self.session.cookies["__cfduid"] + "; PHPSESSID=" + self.session.cookies["PHPSESSID"]
        }
        req = requests.Request('POST', "http://www.saltybet.com/ajax_place_bet.php", headers=header)
        prepped = req.prepare()
        prepped.body = "selectedplayer=<PLAYER>&wager=<WAGER>".replace("<PLAYER>", player).replace("<WAGER>", str(wager))
        prepped.headers['Content-Length'] = len(prepped.body)
        resp = self.session.send(prepped)
        if resp.text != b"":
            return True
        return False

Api = SaltyBetApi()
lastStatus = Api.getStatus()

