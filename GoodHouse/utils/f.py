

def find(item, xpath, first=True):
    results = item.xpath(xpath)
    if not results:
        if first is True:
            return ''
        return []

    if first is True:
        result = results.extract_first().replace('\n', ' ').split(' ')
        return ''.join(result).strip()
    return [''.join(result.replace('\n', ' ').split(' ')).strip()
            for result in results.extract()]


def house_type_split(seq):
    results = []
    for i in seq:
        try:
            results.append(i.split('(')[0].strip())
        except:
            results.append(i)
    return results


def cut_queue(q, length):
    if q.qsize() > length:
        return [q.get() for _ in range(length)]
    return [q.get() for _ in range(q.qsize())]