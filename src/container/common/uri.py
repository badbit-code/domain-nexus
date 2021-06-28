import re

uri_reg_ex = r"(?:([a-zA-Z][\dA-Za-z\+\.\-]*)(?:\:\/\/))?(?:([a-zA-Z][\dA-Za-z\+\.\-]*)(?:\:([^\<\>\:\?\[\]\@\/\#\b\s]*)?)?\@)?(?:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})|((?:\[[0-9a-f]{1,4})+(?:\:[0-9a-f]{0,4}){2,7}\])|([^\<\>\:\?\[\]\@\/\#\b\s\.]{2,}(?:\.[^\<\>\:\?\[\]\@\/\#\b\s]*)*))?(?:\:(\d+))?((?:[^\?\[\]\#\s\b]*)+)?(?:\?([^\[\]\#\s\b]*))?(?:\#([^\#\s\b]*))?"

uri_regex_object = re.compile(uri_reg_ex, re.I)


class URI:
    def __init__(self, uri: str = ""):

        results = uri_regex_object.findall(uri)[0]

        self.protocol = results[0]
        self.user = results[1]
        self.pwd = results[2]
        self.host = results[3] or results[4] or results[5]
        self.port = int(results[6] or "0")
        self.path = results[7]
        self.query = results[8]
        self.hash = results[9]
        self.original_string = uri

    @property
    def top_level_domain(self):
        """
        Returns the top level domain (e.i. com, net, org, io, etc.)
        if the host is a DNS name
        """
        return self.host.split(".").pop()

    @property
    def domain(self):
        """
        Returns the domain following the TLD if
        the host is a DNS name
        """
        try:
            return self.host.split(".").pop(-2)
        except:
            return ""

    @property
    def path_list(self):
        """
        Returns a list of the path names following the first / char
        """
        return self.path[1:].split("/")
