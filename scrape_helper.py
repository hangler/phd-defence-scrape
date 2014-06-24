from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
import inspect
import requests

def xstr(s):
    if s is None:
        return ''
    return s

class AbstractDefenceListing(object):
    __metaclass__ = ABCMeta

    def __init__(self, soup):
        self.soup = soup

    @abstractmethod
    def listing_url(self):
        pass

    @abstractmethod
    def defences(self):
        pass

class AbstractDefenceDetail(object):
    __metaclass__ = ABCMeta

    @classmethod
    def blank_committee(self):
        return { 
                "exam chair": [],
                "supervisor": [],
                "co-supervisor": [],
                "external examiner": [],
                "internal examiner": [],
                "voting member": [],
                "non-voting member": [],
            }

    @classmethod
    def headers(self):
        headers = []
        for func in inspect.getmembers(self, predicate=inspect.ismethod):
            if "g_" in func[0]:
                function_name = func[0][2:] # Strip g_ prefix from function name
                headers.append(function_name)
        return "\t".join(headers) + "\n"

    def visit(self):
        values = {}
        # Call each function prefixed with g_. These return info on the defence
        for func in inspect.getmembers(self, predicate=inspect.ismethod):
            if "g_" in func[0]:
                function_name = func[0][2:] # Strip g_ prefix from function name
                values[function_name] = func[1]()
        return values

    @abstractmethod
    def g__page_url(self):
        pass

    @abstractmethod
    def g_student(self):
        pass

    @abstractmethod
    def g_title(self):
        pass

    @abstractmethod
    def g_defence_date(self):
        pass

    @abstractmethod
    def g_comm_exam_chair(self):
        pass

    @abstractmethod
    def g_comm_supervisor(self):
        pass

    @abstractmethod
    def g_comm_cosupervisors(self):
        pass

    @abstractmethod
    def g_comm_internal_examiner(self):
        pass

    @abstractmethod
    def g_comm_external_examiner(self):
        pass

    @abstractmethod
    def g_comm_voting_members(self):
        pass

    @abstractmethod
    def g_comm_nonvoting_members(self):
        pass

    @abstractmethod
    def committee(self):
        pass

    @abstractmethod
    def g_university(self):
        pass

    @abstractmethod
    def g_department(self):
        pass

class TabWriter(object):

    def __init__(self, file_name):
        self.file_name = file_name

    def write(self, text, tab=True, mode="a"):
        f = open(self.file_name, mode)
        f.write(text.encode('utf-8'))
        f.close()

    def write_headers(self):
         self.write(AbstractDefenceDetail.headers(), tab=False, mode="w")

    def write_row(self, defence_detail):
        row = ""
        if isinstance(defence_detail, AbstractDefenceDetail):
            defence_data = defence_detail.visit()
            for k in sorted(defence_data):
                value = defence_data[k]
                if isinstance(value, list):
                    row = row + ", ".join(unicode(x) for x in value) + "\t"
                elif value is None:
                    row = row + "\t"
                else:
                    row = row + value.replace("\n", "") + "\t"
        row = row + "\n"
        self.write(row, tab=False)  
