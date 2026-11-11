#!/usr/bin/env python

import request
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class Scanner:
    def __init__(self,url,ignore_links):
        self.session = request.Session()
        self.target_url=url
        self.target_links=[]
        self.links_to_ignore=ignore_links

    def extract_links_from(selfself,url):
        response = self.session.get(url)
        links= re.findall(pattern:b'href="(.*?)"',response.content)
        return [link.decode('utf-8' , errors='replace') for link in links]

    def crawl(self,url=None):
        if url == None:
            url=self.target_url
        href_links = self.extract_links_from(url)
        for link in href_links:
            link =urljoin(url,link)

            if "#" in link:
                link = link.split("#")[0]

                if self.target_url in link and link not in self.target_links:
                    self.target_links.append(link)
                    print(link)
                    self.crawl(link)

        def extract_forms(self,url):
            response = self.session.get(url)
            parsed html=BeautifulSoup(response.content.decode('utf-8',errors='replace'), "html.parser")
            return parsed_html.find_all("form")

        def submit_form(self,form,value,url):
            action = form.get("action")
            post_url=urljoin(url,action)
            method = form.get("method")

            inputs_list=form.find_all("input")
            post_data= {}
            for input in inputs_list:
                input_name=input.get("name")
                input_type=input.get("type")
                input_value=input.get("value")
                if input_type=="text":
                    input_value = input_value

                post_data[input_name]=input_value
            if method == "post":
                return self.session.post(post_url,data=post_data)
            return self.session.post(post_url,params=post_data)

        def run_scanner(self):
            for link in self.target_links:
                forms = self.extract_forms(link)
                for form in forms :
                    print("[+] Testting form in" + link)
                    if is_vulnerable_to_xss:
                        print("\n\n[***] XSS discovered in " + link) + "in the following form")
                        print(form)

                if "=" in link:
                    print("\n\n[+] Testing " + link)
                    is_vulnerable_to_xss = self.test_xss_in_link(link)
                    if is_vulnerable_to_xss:
                        print("[***] Discovered XSS in " + link)

        def test_xss_in_link(self,url):
            xss_test_script = "<sCript>alert('test')</scriPt>"
            url = url.replace("=","=" + xss_test_script)
            response =  self.session.get(url)

            return xss_test_script in response.content.decode('utf-8')

        def test_xss_in_form(self,form,url):
            xss_test_script = "<sCript>alert('test')</scriPt>"
            response = self.submit_form(form,xss_test_script,url)
            return xss_test_script in response.content.decode('utf-8')