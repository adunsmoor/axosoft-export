#!/bin/env python

# This uses the API at http://developer.axosoft.com/api/defects.html
#
# ISSUES: 
#
# * Errors aren't handled gracefully
# 
# * This can hit the API limit pretty quickly and there is no
#   save/restart
#

import json
import requests
import getpass
import ConfigParser as configparser

def get_access_token(site, username, password, client_id, client_secret):
    """get an access token using the API""" 

    url = "https://%s/api/oauth2/token" % (site)
    payload = {
	'grant_type': 'password', 
        'username': username, 
	'password': password, 
	'client_id': client_id, 
	'client_secret': client_secret, 
	'scope': 'read'
    }

    response = requests.get(url, params=payload).json()
    if 'access_token' not in response:
        print response
    return response['access_token']

def get_defects(site, token):
    """get all defects"""

    # NOTE: This gets *all* the defects which might take a long time or need to
    # be broken up. The api indicates the ability to do pagination which I
    # don't need yet.
    url = "https://%s/api/v5/defects/?access_token=%s" % (site, token)
    response = requests.get(url).json()

    return response

def get_defect_comments(id, site, token):
    """get all comments for a defect"""

    url = "https://%s/api/v5/defects/%s/comments?access_token=%s" % (site, id, token)
    response = requests.get(url).json()

    return response
    
def export_defects(site, token):

    defects = get_defects(site, token)
    if 'data' not in defects:
        print defects

    for ticket in defects['data']:
        id = ticket['id']
        comments = get_defect_comments(id, site, token)

        with open('defects/%s.json'%(id), 'w') as f:
            s = json.dumps(ticket, sort_keys=True, indent=2, separators=(',', ': '))
            f.write(s)
        with open('defects/%s.comment.json'%(id), 'w') as f:
            f.write(json.dumps(comments, sort_keys=True, indent=2, separators=(',', ': ')))

if __name__ == '__main__':

    # [Axosoft]
    # site = example.axosoft.com
    # # if you don't have an access token then set
    # # client_id and client_secret to get a token
    # token = 
    # client_id = 
    # client_secret = 
    #
    config = configparser.SafeConfigParser()
    config.read('axosoft.config')

    site = config.get('Axosoft', 'site')

    # if token isn't in the config then try to get one
    if not config.has_option('Axosoft', 'token'):
        client_id = config.get('Axosoft', 'client_id')
        client_secret = config.get('Axosoft', 'client_secret')

	print 'Axosoft Site: %s' % (site)
        username = raw_input('Axosoft User Name: ')
        password = getpass.getpass('Axosoft Password: ')
        token = get_access_token(site, username, password)
        print 'Axosoft Token: %s' % (token)

        config.set('Axosoft', 'token', token)

    token = config.get('Axosoft', 'token')
    export_defects(site, token)
