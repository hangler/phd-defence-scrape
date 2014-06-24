from scrape_helper import *
import re

class SFUListing(AbstractDefenceListing):

    def __init__(self, json):
        # No soup required; this is all JSON
        self.json = json

    @classmethod
    def listing_url(self):
        return "https://rails1.its.sfu.ca:44384/events?from=X_FROM_X&to=X_TO_X&urls%5B%5D=https%3A%2F%2Fconnect.sfu.ca%2Fhome%2Fdgsit%40sfu.ca%2Fsfudefences"

    def extract_name(self, summary):

        first_separator_index = len(summary)
        
        separators = [
            "-",
            ",",
            "education",
            "msc",
            "phd",
        ]

        # Find the shortest segment starting out the string (before encountering a separator)
        # This will likely be the name
        for s in separators:
            index = summary.lower().find(s)
            if index < first_separator_index and index > 0:
                first_separator_index = index

        return summary[:first_separator_index]

    def extract_department(self, summary):
        if summary.find("Education") > 0:
            return "Education"
        elif summary.find("Psychology") > 0:
            return "Psychology"
        # Usually, department will be listed last after the final comma
        elif "," in summary:
            return summary[summary.rfind(",") + 2:]
        elif "-" in summary:
            return summary[summary.rfind("-") + 2:]
        # Couldn't find anything
        return summary

    def format_committee_member(self, committee_member, key):
        committee_member = committee_member.replace(key, "").replace(":", "").replace(",", "").strip().title()
        return committee_member

    def extract_committee(self, description):
        description = description.lower()

        # Replace all dr.s
        description = description.replace("dr. ", "").replace("dr ", "")

        committee = SFUDefenceDetail.blank_committee()

        for key in committee:
            if key in description:
                # Key will be something like "supervisor"
                targets = [
                    r"%s: \b.*\b.*\b" % key,
                    r"\b.*\b.*\b, %s" % key,
                ]
                for target in targets:
                    result = re.findall(target, description)
                    if result:
                        [committee[key].append(self.format_committee_member(r, key)) for r in result]

        return committee

    def extract_date(self, datetime):
        return datetime[:10]

    def is_phd_defence(self, summary):
        return "phd" in summary.lower()

    def defences(self, page_url):
        details = []
        
        for item in self.json:
            summary = item["summary"]
            description = item["description"]
            datetime = item["start_time"]
            if self.is_phd_defence(summary):
                name = self.extract_name(summary)
                department = self.extract_department(summary)
                committee = self.extract_committee(description)
                date = self.extract_date(datetime)
                title = description.replace("\t", "")
                detail = SFUDefenceDetail(page_url=page_url, student=name, title=title, defence_date=date, committee=committee, department=department)
                details.append(detail)

        return details


class SFUDefenceDetail(AbstractDefenceDetail):

    @classmethod
    def blank_committee(self):
        return { 
                "chair": [],
                "supervisor": [],
                "external examiner": [],
                "internal examiner": [],
            }

    def __init__(self, page_url, student, title, defence_date, committee, department):
        self.page_url = page_url
        self.student = student
        self.title = title
        self.defence_date = defence_date
        self.committee = committee
        self.department = department

    def g__page_url(self):
        return self.page_url

    def g_student(self):
        return self.student

    def g_title(self):
        return self.title

    def g_defence_date(self):
        return self.defence_date

    def g_comm_exam_chair(self):
        return self.committee["chair"]

    def g_comm_supervisor(self):
        return self.committee["supervisor"]

    def g_comm_cosupervisors(self):
        pass

    def g_comm_internal_examiner(self):
        return self.committee["internal examiner"]

    def g_comm_external_examiner(self):
        return self.committee["external examiner"]

    def g_comm_voting_members(self):
        pass

    def g_comm_nonvoting_members(self):
        pass

    def committee(self):
        return self.committee

    def g_university(self):
        return "Simon Fraser University"

    def g_department(self):
        return self.department