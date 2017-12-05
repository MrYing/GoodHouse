

def find(item, xpath, first=True):
    results = item.xpath(xpath)
    if not results:
        if first is True:
            return ''
        return []

    if first is True:
        result = results.extract_first().replace('\n', ' ').split(' ')
        return ''.join(result).strip()
    return [result.strip() for result in results.extract()]


def house_type_split(seq):
    results = []
    for i in seq:
        try:
            results.append(i.split(' ')[0])
        except:
            results.append(i)
    return results