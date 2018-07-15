import re
import requests

BASE_CONCEPT_NET_URL = 'http://api.conceptnet.io/'
ARTICLES = ['a', 'an', 'the']

def connected_to_internet(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.RequestException as e:
        print(e)
    return False

# 2.0 for threshold     of confidence level

def proper_format(concept):
    return str.replace(concept, ' ', '_').lower()


def lookup_concept(concept):
    if connected_to_internet():
        return requests.get(BASE_CONCEPT_NET_URL + 'c/en/' + proper_format(concept)).json()
    else:
        return []


def get_significant_word(concept):
    return str.replace(concept[6:], '_', ' ')


def get_related_concepts(concept):
    if connected_to_internet():
        return [get_significant_word(x['@id']) for x in
            requests.get(BASE_CONCEPT_NET_URL + 'related/c/en/' + proper_format(concept) + '?filter=/c/en').json()[
                'related']]
    else:
        return []


def get_similarity(concept1, concept2):
    if connected_to_internet():
        return requests.get(
            BASE_CONCEPT_NET_URL + 'related/c/en/' + proper_format(concept1) + '?filter=/c/en/' + proper_format(
                concept2)).json()['related'][0]['weight']
    else:
        return []


def get_connection(concept1, concept2):
    if connected_to_internet():
        return requests.get(
            BASE_CONCEPT_NET_URL +
            'query?node=/c/en/' + proper_format(concept1) +
            '&other=/c/en/' + proper_format(concept2)).json()
    else:
        return []


def remove_articles(string):
    return re.compile("\\b(" + "|".join(ARTICLES) + ")\\W", re.I).sub("", string)


def query(concept, position, relation, weight=2.0):
    if connected_to_internet():
        return [(remove_articles(x['start']['label']),
                 remove_articles(x['end']['label'])) for x in
                requests.get(BASE_CONCEPT_NET_URL +
                             'query?' + position + '=/c/en/' +
                             proper_format(concept) + '&rel=/r/' + relation).json()['edges'] if x['weight'] >= weight]
    else:
        return []


def check_if_connection(concept1, concept2, relation):
    if connected_to_internet():
        return len(requests.get(BASE_CONCEPT_NET_URL + 'query?node=/c/en/' +
                                proper_format(concept1) + '&rel=/r/' + relation +
                                "&other=/c/en/" + proper_format(concept2)).json()['edges']) > 0
    else:
        return []
