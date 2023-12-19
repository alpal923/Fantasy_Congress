from bs4 import BeautifulSoup
import requests
import re
from openai import OpenAI
import numpy as np
import csv


def get_issue_links(senator):
    senator_div_classes = {"romney": "elementor elementor-797",
                           "lee": re.compile(r"^issues-grid.*"),
                           "klobuchar": "element element_textblocks",
                           "smith": "elementor-element elementor-element-06c8f64 elementor-nav-menu__align-left elementor-nav-menu--dropdown-none elementor-widget elementor-widget-nav-menu"}
    senator_issue_endings = {"romney": "/issues",
                             "lee": "/issues",
                             "klobuchar": "/public/index.cfm/issues",
                             "smith": "/issues"}
    response = requests.get("https://www." + senator + ".senate.gov" + senator_issue_endings[senator])
    soup = BeautifulSoup(response.text, "html.parser")
    divs = soup.find_all("div", {"class": senator_div_classes[senator]})
    last_div = divs[-1] if divs else None
    issue_links = []
    if last_div is not None:
        for link in last_div.find_all("a"):
            if link.get("href") not in issue_links:
                issue_links.append(link.get("href"))
    new_links = []
    for link in issue_links:
        if link[0] == "/":
            new_links.append("https://www." + senator + ".senate.gov" + link)
        elif link[0] == "?":
            new_links.append("https://www." + senator + ".senate.gov/issues" + link)
        elif link[0] != "h":
            new_links.append("https://www." + senator + ".senate.gov/" + link)
        else:
            new_links.append(link)
    if senator == "smith":
        new_links.append("https://www.smith.senate.gov/issues/housing/")
    return new_links


def get_issue_statement(senator, issue):
    chosen_link = ""
    issue_links = get_issue_links(senator)
    for link in issue_links:
        if re.search(issue, link.lower()):
            chosen_link = link
            break
    statement = ""
    if chosen_link:
        paragraph_classes = {"romney": re.compile(r"elementor-element elementor-element-[a-z0-9]+\b elementor-widget elementor-widget-text-editor"),
                             "lee": "element-content",
                             "klobuchar": "article",
                             "smith": re.compile(r"elementor-element elementor-element-[a-z0-9]+\b elementor-widget elementor-widget-text-editor")}
        response = requests.get(chosen_link)
        soup = BeautifulSoup(response.text, "html.parser")
        divs = soup.find_all("div", {"class": paragraph_classes[senator]})
        for div in divs:
            paragraphs = div.find_all("p")
            for paragraph in paragraphs:
                statement += paragraph.text
    return statement


def rate_position(senator, issue):
    client = OpenAI()
    statement = get_issue_statement(senator, issue)
    if statement:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "You are to evaluate how authoritarian a given position or a proposed bill is. Rate it on a scale to -1 to 1 where -1 is the most authoritarian and 1 is the most libertarian. Please answer with a number between -1 and 1. If you cannot evaluate it based on the given information, answer with a 0."},
            {"role": "user", "content": statement[:4097]}
            ]
        )
        generated_text_gov = completion.choices[0].message.content
        ratings = re.findall(r"-?0\.?[0-9]?", generated_text_gov)
        left_right_rate = np.mean([float(rating) for rating in ratings]) if len(ratings) > 0 else 0.0
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "You are to evaluate how left or right wing a given position or a proposed bill is. Rate it on a scale to -1 to 1 where -1 is the most left wing and 1 is the most right wing in the context of American politics. Please answer with a value between -1 and 1. If you cannot evaluate it based on the given information, answer with a 0."},
            {"role": "user", "content": statement[:4097]}
            ]
        )
        generated_text_pos = completion.choices[0].message.content
        ratings = re.findall(r"-?0\.?[0-9]?", generated_text_pos)
        auth_lib_rate = np.mean([float(rating) for rating in ratings]) if len(ratings) > 0 else 0.0
        return left_right_rate, auth_lib_rate
    else:
        return None, None


def generate_position_matrix(senator):
    issues = [re.compile(r"second|2"), 'agriculture', 'budget', 'competition', 'consumer', 'drought', 
              'education', re.compile(r"energy|natural"), re.compile(r"(?<!-)environment"), 'ethics', 
              re.compile(r"(?<!-)families|family"), 'health', 'housing', 'immigration', 'indian', 
              'infrastructure', 'jobs', 'lands', 'rural-utah', 'safety', 'security', 'seniors', 'tax', 
              'technology', 'trade', 'veterans', 'working-families']
    x_sum = y_sum = x_num = y_num = 0
    pol_row = [f"{senator.capitalize()}: Left/Right"]
    gov_row = [f"{senator.capitalize()}: Auth/Lib"]
    for issue in issues:
        left_right_rate, auth_lib_rate = rate_position(senator, issue)
        if left_right_rate is not None and left_right_rate != 0:
            x_sum += left_right_rate
            x_num += 1
        if auth_lib_rate is not None and auth_lib_rate != 0:
            y_sum += auth_lib_rate
            y_num += 1
        pol_row += [left_right_rate]
        gov_row += [auth_lib_rate]
    left_right_mean = round(x_sum / x_num, 4) if x_num > 0 else 0.0
    auth_lib_mean = round(y_sum / y_num, 4) if y_num > 0 else 0.0
    for i in range(len(pol_row)):
        if pol_row[i] is None:
            pol_row[i] = left_right_mean
        if gov_row[i] is None:
            gov_row[i] = auth_lib_mean
    return [pol_row, gov_row]
    

def generate_positions_csv():
    position_data = [['Senator Name and Metric', '2nd Amendment', 'Agriculture', 'Budget', 'Competition Policy', 
                    'Consumer Protection', 'Drought', 'Education', 'Energy', 'Environment', 'Ethics', 'Families', 
                    'Healthcare', 'Housing', 'Immigration', 'Indian Affairs', 'Infrastructure', 'Jobs', 'Lands', 'Rural Utah', 
                    'Safety', 'Security', 'Seniors', 'Taxes', 'Technology', 'Trade', 'Veterans', 'Working Families']]
    senators = ["romney", "lee", "klobuchar", "lee"]
    for senator in senators:
        position_data += generate_position_matrix(senator)
    with open("senator_issue_positions.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(position_data)


if __name__ == "__main__":
    generate_positions_csv()
