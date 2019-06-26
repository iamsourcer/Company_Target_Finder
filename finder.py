#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib.parse
from bs4 import BeautifulSoup as bs
from pprint import pprint as pp
import pickle
import argparse


def encoded_skills(techlist):
    query = ''
    for tech in techlist:
        query += urllib.parse.quote(tech + ' ')
    return query


def search(skills, location, max_page=10):
    # TODO: scrapear la descripcion del puesto para analysis
    # TODO: mejorar los logs con un loader para que no acumule basura

    print('Alright, we are looking for ' + ' '.join(skills) + ' in ' + location)
    url = 'https://www.indeed.com/jobs'
    url += '?q={}&l={}&radius=25&start={}'
    roles = []
    PAGE_SIZE = 10

    for page in range(1, max_page):
        url = url.format(encoded_skills(skills), location, page * PAGE_SIZE)
        print(url)
        r = requests.get(url)
        soup = bs(r.text, 'html.parser')
        # tabla = soup.find(id='resultsCol')

        print('page:', page)
        print('total results:', len(roles))
        results = soup.find_all('div', attrs={'class': 'result'})

        for result in results:
            title = result.find(class_='title').a.text.strip()
            company = result.find(class_='company').text.strip()
            data_dic = {}
            data_dic['title'] = title
            data_dic['company'] = company
            roles.append(data_dic)
    return roles


def group_companies_by_role(roles):
    # key = roles y value = set de companies
    companies_by_role = {}
    for role in roles:
        if role['title'] not in companies_by_role.keys():
            companies_by_role[role['title']] = set()
        companies_by_role[role['title']].add(role['company'])
    return companies_by_role


def group_roles_by_company(roles):
    # key = company y value = set de roles
    roles_by_company = {}
    for role in roles:
        if role['company'] not in roles_by_company.keys():
            roles_by_company[role['company']] = set()
        roles_by_company[role['company']].add(role['title'])
    return roles_by_company


def get_companies(role, location, db):
    pass


def load_db(filename):
    try:
        with open(filename, 'rb') as fo:
            db = pickle.load(fo)
        return db
    except:
        db = {}
        dump_db(filename, db)
        return db


def update_db(db, location, results):
    if location not in db.keys():
        db[location] = results
    else:
        current_data = db[location]
        for company, roles in results.items():
            if company not in current_data.keys():
                current_data[company] = roles
            else:
                current_data[company].union(roles)


def dump_db(filename, data):
    with open(filename, 'wb') as fo:
        pickle.dump(data, fo)


if __name__ == '__main__':
    PICKLE_FILE = 'data.pickle'
    parser = argparse.ArgumentParser(description='Source - Indeed Scraper')
    parser.add_argument('--location', dest="location", required=True)
    parser.add_argument('--skills', dest="skills", nargs='*')
    parser.add_argument('--role', dest="role")

    try:
        # Modo scrapper
        #   indeed_companies.py 'San Francisco, CA' --skills kubernetes
        # Modo consulta
        #   indeed_companies.py 'San Francisco, CA' --role 'Devops Engineer'
        args = parser.parse_args()
        db = load_db(PICKLE_FILE)
        print(args)
        # Modo Scrapper
        if args.skills:
            roles = search(args.skills, args.location)
            companies = group_companies_by_role(roles)

            print('Loading data...',
                  len(db[args.location]),
                  ' available companies')

            update_db(db, args.location, results=companies)
            dump_db(PICKLE_FILE, db)
            print('Dumping data...',
                  len(db[args.location]),
                  ' available companies')

        # Modo Consulta
        # TODO: corregir modo consulta
        if args.role:
            for roles, company in db[args.location].items():
                if args.role.lower() in roles.lower():
                    print(company)

    except Exception as e:
        print(e)
        print('algo fallo')
