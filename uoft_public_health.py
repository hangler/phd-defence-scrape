from scrape_helper import *
import re

class UofTPublicHealthListing(AbstractDefenceListing):

    @classmethod
    def listing_url(self):
        return "http://www.dlsph.utoronto.ca/page/"

    def parse_date(self, date_element):
        #first_comma_index = date_element.text.index(",")
        #second_comma_index = date_element.text.index(",", first_comma_index + 1)
        #date = date_element.text[:second_comma_index + 6] # "..., 2014" so slice at 2nd comma + 6 chars
        search_results = re.search("2\d\d\d", date_element.text)
        room_index = search_results.start() + 4
        date = date_element.text[:room_index].strip().title()
        return date

    def singularize(self, label):
        if label.endswith("s"):
            label = label[:-1]
        return label

    def clean(self, text):
        return text.strip().replace(u"\xa0", " ").replace(u"\u2028", "").replace("[", "").replace("]", "")

    def defences(self, page_url):
        details = []
        names = []

        count = 1
        for row in self.soup.find('table', {'class': 'mceItemTable'}).findAll('tr'):
            names.append(self.clean(row.find('td').text))

        for name in names:
            base_element = None
            for para in self.soup.findAll('p'):
                if name.lower() in para.text.lower():
                    base_element = para
            
            # Backup in case the *first* name has been messed up, e.g. ANNA vs. ANNE
            # Also removes periods in name (e.g. Lisa J. --> Lisa J)
            if not base_element:
                temp_name = ' '.join(name.split(' ')[1:])
                for para in self.soup.findAll('p'):
                    if temp_name.lower().replace(".", "") in para.text.lower().replace(".", ""):
                        base_element = para      

            date_element = base_element.findNext('p')
            date = self.parse_date(date_element)
            
            title_element = date_element.findNext('p')
            title = self.clean(title_element.text).title()

            committee_table = title_element.findNext('table')
            exam_chairs = None

            committee = AbstractDefenceDetail.blank_committee()
            label = ""
            try:
                for row in committee_table.findAll('tr'):
                    label_cell = row.findNext('td')
                    label_changed = False
                    if len(label_cell.text) > 1:
                        label = label_cell.text.replace(":", "").lower()
                        label_changed = True
                        label = self.singularize(label)
                    #print "%s (%s)" % (label, str(label in committee))
                    detail_cell = label_cell.findNext('td')
                    if label in committee:
                        committee[label].append(self.clean(detail_cell.text.title()))
            except AttributeError:
                # There is no committee table, e.g. it's TBD
                continue

            detail = UofTPublicHealthDefenceDetail(page_url=page_url, student=name.title(), title=title, defence_date=date, committee=committee)
            details.append(detail)

        return details


class UofTPublicHealthDefenceDetail(AbstractDefenceDetail):

    def __init__(self, page_url, student, title, defence_date, committee):
        self.page_url = page_url
        self.student = student
        self.title = title
        self.defence_date = defence_date
        self.committee = committee

    def g__page_url(self):
        return self.page_url

    def g_student(self):
        return self.student

    def g_title(self):
        return self.title

    def g_defence_date(self):
        return self.defence_date

    def g_comm_exam_chair(self):
        return self.committee["exam chair"]

    def g_comm_supervisor(self):
        return self.committee["supervisor"]

    def g_comm_cosupervisors(self):
        return self.committee["co-supervisor"]

    def g_comm_external_examiner(self):
        return self.committee["external examiner"]

    def g_comm_voting_members(self):
        return self.committee["voting member"]

    def g_comm_nonvoting_members(self):
        return self.committee["non-voting member"]

    def committee(self):
        return self.committee

    def g_university(self):
        return "University of Toronto"

    def g_department(self):
        return "Dalla Lana School of Public Health"