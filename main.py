"""
hello mp is a telegram bot to send a single message to all parliment members at once.

The bot part is not implemented yet.
"""
import bs4
import requests


def get_token(final_url, fail=None) -> str:
    """gets the csrf token of the write to mp form"""
    if fail:
        return "wrong_token"

    base_url = "https://majlis.gov.mv/en/20-parliament/members/"
    url = final_url
    majlis_session = requests.session()  # Majlis is in session now xD
    majlis_session.get(base_url)

    # lets assume they gave us our cookies for visiting the parliament
    # if we have cookies we can get the page properly ( sometimes they trigger an error when we dont have cookies)
    res = majlis_session.get(url)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    token = soup.find("input", {"name": "_token"})["value"]
    return token


def extact_member_urls() -> list:
    """from the base members url we extract all the member links"""

    # https://majlis.gov.mv/en/20-parliament/members/
    res = requests.get("https://majlis.gov.mv/en/20-parliament/members/")
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    soup.find_all("a", href=True)
    links = [link["href"] for link in soup.find_all("a", href=True)]

    # filter by links that contain https://majlis.gov.mv/en/20-parliament/members/
    filtered_links = [link for link in links if "https://majlis.gov.mv/en/20-parliament/members/" in link]
    filter_party_links = [link for link in filtered_links if "party" in link]

    # remove the party links
    links = filtered_links.copy()

    for link in filter_party_links:
        links.remove(link)
    return links


def get_member_name(url) -> str:
    """
    gets the name of the member from the url (first h4 tag)
    """
    res = requests.get(url)

    assert res.status_code == 200, "Failed to get the page"

    soup = bs4.BeautifulSoup(res.text, "html.parser")
    name = soup.find("h4").text
    # print(name)
    return name


def get_member_party(url) -> str:
    """
    todo: gets the party of the member from the url
    """
    pass


def send_message(message:str) -> None:
    """sends the message to all the members"""
    links = extact_member_urls()

    # random sort : so we dont spam the same person while testing
    import random
    random.shuffle(links)

    for link in links:
        token = get_token(link, fail=True)
        message = requests.post(link, data={"_token": token, "m": message})
        mp_name = get_member_name(link)
        if message.status_code == 405:
            print("Message to {} failed".format(mp_name))
            break
        break  # lets actually not send the message to everyone


if __name__ == "__main__":
    send_message("hello mp")
