# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 12:25:26 2022

@author: Nathan Woodburn
"""

import requests
r = requests.get('https://github.com/timeline.json')
r.json()
