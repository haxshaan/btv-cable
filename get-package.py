import requests
from bs4 import BeautifulSoup
import csv
from sys import exit
import os.path
import json


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

    try:
        session.post(login, data=payload)

    except Exception:
        print('Please check your Internet Connection or try again later!')
        exit(0)


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

    channel_list = list()

    for item in list_buq:
        if 'Subscribed' in item.text.strip():
            channel_list.append(item.text.strip('\n').split('\n')[0])

        else:
            pass

    return channel_list


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


def calc_price(price_dict, cust_price_list):

    total = 0

    for channel in cust_price_list:
        total += float(price_dict[channel.strip()])

    gst = 0.18 * total

    return total + gst


def allto_csv(html):

    """
    Function to scrape sub details and write to a csv file
    :param html: html data
    :return: csv file
    """

    soup = BeautifulSoup(html, 'html.parser')

    t_body = soup.find_all(class_='info')

    channel_dict = dict()

    w = csv.reader(open('Package price.csv', 'r'))

    for rows in w:
        if any(x.strip() for x in rows):
            channel_dict[rows[0]] = rows[1]

    with open('all_sub.csv', 'a') as out_file:

        h = csv.writer(out_file)

        h.writerow(['ID', 'Customer Name', 'STB Number', 'Status', 'Amount'])

        for item in t_body:
            if 'Active' in item.text.strip():
                cust = item.text.strip().split('\n')

                all_packtest = get_active_pack(cust[2], cust[1], cust[0])

                price_t = calc_price(channel_dict, all_packtest)

                h.writerow([cust[0], cust[1], cust[2], cust[3], price_t])

                print(cust[0], cust[1], cust[2], cust[3], price_t)


def linktohtml(url):
    """
    Takes a url and returns its html.
    :param: url of the page
    :return: html
    """

    r = session.get(url)

    return r.content


def main():

    global session, stb_num, choice

    print("Welcome to BTV Digital software by Shantam.\n\nPlease choose from below options:")

    print('Twitter: {0}'.format('@Haxcrypto'))

    while True:

        try:
            choice = int(input("1. Get Active Packs     2. Check Package Price     3. Refresh Price list    "
                               "4. Generate All User list.\n" + '>  '))
        except ValueError:
            continue
        if choice not in range(1, 5):
            continue
        else:
            break

    if os.path.exists('config.ini'):
        with open('config.ini', 'r') as f:
            creds = json.load(f)
            uname = [*creds][0]
            passw = creds[uname]

    else:
        uname = input("Enter login id: ")
        passw = input("Enter password: ")
        creds = dict()
        creds[uname] = passw
        with open('config.ini', 'w') as f:
            json.dump(creds, f)

    session = requests.Session()

    log_in(uname, passw)

    if choice == 1:

        stb_num = input("Enter STB No.: ")

        stb_det = stb_status(stb_status_html())

        stb_id = stb_det[0]
        stb_name = stb_det[1]
        stb_ua = stb_det[2]

        all_packtest = get_active_pack(stb_ua, stb_name, stb_id)

        for item in all_packtest:
            print(item)

    elif choice == 4:

        link = sub_url

        while True:

            content = linktohtml(link)

            allto_csv(content)

            soup = BeautifulSoup(content, 'html.parser')

            nxt = soup.find(class_='next')

            if nxt:

                for item in nxt.find_all('a', href=True):
                    if item.text:
                        link = home + item['href']
                        continue
                    else:
                        print('Cant get href in link')
                        break

            else:
                print('No more Next buttons.')
                break

    elif choice == 2:

        stb_num = input("Enter STB No.: ")

        stb_det = stb_status(stb_status_html())

        stb_id = stb_det[0]
        stb_name = stb_det[1]
        stb_ua = stb_det[2]

        all_packtest = get_active_pack(stb_ua, stb_name, stb_id)

        w = csv.reader(open('Package price.csv', 'r'))

        channel_dict = dict()

        for rows in w:
            if any(x.strip() for x in rows):
                channel_dict[rows[0]] = rows[1]

        print('Total Package Price: ', calc_price(channel_dict, all_packtest))

    elif choice == 3:

        stb_num = input("\nEnter STB No.: ")

        stb_det = stb_status(stb_status_html())

        stb_id = stb_det[0]
        stb_name = stb_det[1]
        stb_ua = stb_det[2]

        get_active_pack(stb_ua, stb_name, stb_id)

        calc_all(stb_ua, stb_name, stb_id)  # Gets alacarta channels and their respected price.

        print(write_csv(calc_all(stb_ua, stb_name, stb_id), 'Package price.csv'))    # Creates csv file.

    else:
        pass


if __name__ == '__main__':

    counter = 1

    while True:

        if counter == 1:

            main()
            counter += 1
            continue

        else:

            continu = input("Press any key to exit or 'c' to continue: ")

            if continu == 'c':
                main()
                continue

            else:
                break


