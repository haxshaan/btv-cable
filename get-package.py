import requests
from bs4 import BeautifulSoup
import csv
from sys import exit


home = 'http://1.22.215.49:56442/NewSMS/'
login = home + 'adminlogin.action'
sub_url = home + 'subscriberlist.action'
sub_search = sub_url + '/searchsubscriberbyfilter.action'


def log_in(user, passw):

    """
    Function which creates a session and logs in.
    :param user: UserID
    :param passw: Password
    """
    payload = {'user.userID': str(user),
               'user.password': str(passw)}

    session.post(login, data=payload)


def stb_status_html():

    payload_sub = {'filter': 'ua', 'value': stb_num}
    sub_stb_page = session.post(sub_search, data=payload_sub)

    return sub_stb_page.content

    # with open('html2.txt', 'wb') as f:
    # f.write(sub_stb_page.content)


def stb_status(html):
    """

    :rtype: A list containing stb details.
    """
    soup = BeautifulSoup(html, 'html.parser')

    list_customer = soup.find_all(class_='info')

    if list_customer:

        for item in list_customer:
            if 'Active' in item.text.strip():
                stb_status_text = item.text.strip().split('\n')

                print(stb_status_text[:4], '\n')

                return stb_status_text
            elif 'Surrendered' in item.text.strip():
                print('The Box is in Suspended state')
                exit(0)
            else:
                print('The Box is Deactivated')
                exit(0)

    else:
        print('\nThe STB is not in ID')
        exit(0)


def get_active_pack(a, b, c):
    buq_url = home + 'bouquedetail.action?ua={0}&subscriberName={1}&subscriberID={2}'.format(a, b, c)

    buq_html = session.get(buq_url)

    # with open('html3.txt', 'wb') as f:
    # f.write(buq_html.content)

    soup = BeautifulSoup(buq_html.content, 'html.parser')

    list_buq = soup.find_all(class_='info')

    with open('temp.k', 'w') as fh:

        for item in list_buq:
            if 'Subscribed' in item.text.strip():
                if choice == str(1):
                    print(item.text.strip('\n').split('\n')[0])
                elif choice == str(2):
                    fh.write(item.text.strip('\n').split('\n')[0] + '\n')
                else:
                    pass
            else:
                pass


def calc_all(a, b, c):
    """

    :rtype: Generates a csv file containing alacarta channel and their price.
    """
    sub_more_url = home + 'subscribemorebouque.action?ua={0}&subscriberName={1}&subscriberID={2}'.format(a, b, c)

    h = session.get(sub_more_url)

    soup = BeautifulSoup(h.content, 'html.parser')

    list_buq = soup.find_all(class_='info')

    channel_dict = dict()

    for item in list_buq:

        buq = item.text.split('\n')

        channel_dict[buq[2]] = buq[3]

    return channel_dict


def write_csv(dict1, name):
    w = csv.writer((open(name, 'w')))

    for key, val in dict1.items():
        w.writerow([key, val])

    w.writerow(['FTA_Basic', 130])


def calc_price(price_csv, cust_price):

    w = csv.reader(open(price_csv, 'r'))

    channel_dict = dict()

    for rows in w:
        if any(x.strip() for x in rows):
            channel_dict[rows[0]] = rows[1]

    total = 0

    with open(cust_price, 'r') as f:
        for channel in f:
            total += float(channel_dict[channel.strip()])

    gst = 0.18 * total

    return total + gst


def main():

    global session, stb_num, choice

    print("Welcome to BTV Digital software by Shantam.\n\nPlease choose 1 or 2:")

    while True:

        try:
            choice = int(input("1. Get Active Packs     2. Check Package Price     3. Refresh Price list\n" + '>  '))
        except ValueError:
            continue
        if choice not in range(1, 4):
            continue
        else:
            break

    session = requests.Session()

    log_in()

    stb_num = input("\nEnter STB No.: ")

    stb_det = stb_status(stb_status_html())

    stb_id = stb_det[0]
    stb_name = stb_det[1]
    stb_ua = stb_det[2]

    get_active_pack(stb_ua, stb_name, stb_id)       # Gets channels subscribed in a particular stb.

    if choice == str(2):
        print('Total Package Price: ', calc_price('Package price.csv', 'temp.k'))
    elif choice == str(3):
        calc_all(stb_ua, stb_name, stb_id)  # Gets alacarta channels and their respected price.

        print(write_csv(calc_all(stb_ua, stb_name, stb_id), 'Package price.csv'))    # Creates csv file.

    else:
        pass


if __name__ == '__main__':
    main()