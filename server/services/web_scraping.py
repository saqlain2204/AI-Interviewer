import requests
from bs4 import BeautifulSoup, NavigableString, Tag

def prettify_element(element, indent=0):
    prefix = '  ' * indent
    if isinstance(element, NavigableString):
        text = element.strip()
        return prefix + text if text else ''
    elif isinstance(element, Tag):
        if element.name in [f'h{i}' for i in range(1, 7)]:
            return f"{prefix}{element.get_text(strip=True).upper()}\n"
        elif element.name == 'p':
            return f"{prefix}{element.get_text(strip=True)}\n"
        elif element.name in ['ul', 'ol']:
            items = []
            for li in element.find_all('li', recursive=False):
                items.append(prettify_element(li, indent + 1))
            return f"{prefix}{element.name}:\n" + '\n'.join(items) + '\n'
        elif element.name == 'li':
            return f"{prefix}- {element.get_text(strip=True)}"
        else:
            return ''.join([prettify_element(child, indent) for child in element.children])
    return ''

def scrape_website(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    output = []
    for elem in soup.body.descendants if soup.body else soup.descendants:
        if isinstance(elem, Tag) and elem.name in [f'h{i}' for i in range(1, 7)] + ['p', 'ul', 'ol']:
            pretty = prettify_element(elem)
            if pretty.strip():
                output.append(pretty)

    return '\n'.join(output)



