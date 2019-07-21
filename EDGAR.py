import requests
from bs4 import BeautifulSoup
import re
import xml.etree.ElementTree as ET
import csv
import sys

class Spider:
    def __init__(self, CIK_list):
        self.CIK_list = CIK_list
        self.host = 'https://www.sec.gov'
        self.path = '/cgi-bin/browse-edgar'
        self.query_params_format = '?CIK={}&owner=exclude&action=getcompany'
        self.url_list = [self.host + self.path + self.query_params_format.format(CIK) for CIK in self.CIK_list]
        self.CIK_url_map = dict(zip(self.CIK_list, self.url_list))
        self.html_parser = 'html.parser'
        self.xml_parser = 'xml'
        self.pattern_13F = re.compile(r'.*13F.*$')
        self.pattern_info_table = re.compile(r'.*information.*table.*$')
        self.raw_titles = [
            'nameOfIssuer',
            'titleOfClass',
            'cusip',
            'value',
            'sshPrnamt',
            'sshPrnamtType',
            'investmentDiscretion',
            'Sole',
            'Shared',
            'None',
        ]
        self.shrsOrPrnAmt_children = [ 'sshPrnamt', 'sshPrnamtType']
        self.voting_authority_children = [ 'Sole', 'Shared', 'None']
        self.logging_msg_row_count = 30
        self.status_map = {}

    #-------------------------------------------------------------
    # return a BeautifulSoup result with url and parser type as inputs
    #-------------------------------------------------------------
    def BsRequest(self, url, parser_type):
        res = requests.get(url)
        source_code = res.content
        soup = BeautifulSoup(source_code, parser_type)
        return soup

    #-------------------------------------------------------------
    # return a list of title for generated TSV file
    #-------------------------------------------------------------
    def getTitles(self):
        titles = []
        for head in self.raw_titles:
            if head in self.shrsOrPrnAmt_children:
                titles.append('shrsOrPrnAmt_'.format(head))
            elif head in self.voting_authority_children:
                titles.append('votingAuthority_{}'.format(head))
            else:
                titles.append(head)
        return titles

    def create_report_failure(self):
        self.status_map[self.curr_CIK] = None
        self.log_done()

    def create_report_success(self):
        self.status_map[self.curr_CIK] = self.curr_file_name
        self.log_done()

    def log_done(self):
        self.log_title('CIK {}: DONE'.format(self.curr_CIK))
        print('\n')

    def status(self):
        print('\n')
        print('************************** Generate TSV File Status Report ***************************')
        for CIK, result in self.status_map.items():
            status = 'Succeeded' if result else 'Failed'
            failed_msg = 'No file created'
            print('{}: {} --- {}'.format(CIK, status, result or failed_msg))
        print('**************************************************************************************')
        print('\n\n')

    def log_msg(self, msg):
        print('CIK {}: {}'.format(self.curr_CIK, msg))

    def log_title(self, title):
        print('---------------------------------- {} ----------------------------------'.format(title))

    #----------------------------------------------------------------------------
    # Log message while parsing and writing data with current row number as input
    #----------------------------------------------------------------------------
    def process_logging(self, curr_row_num):
        if (curr_row_num) % self.logging_msg_row_count == 0:
            self.log_msg('parsing in process: {} rows'.format(str(curr_row_num)))

    #-----------------------------------------------------------------------
    # Writes data to TSV file with BeautifulSoup XML content object as input
    #-----------------------------------------------------------------------
    def createTsv(self, xml):
        self.curr_file_name = '{}_{}.tsv'.format(self.curr_CIK, self.curr_company_name)
        out_file = open(self.curr_file_name, 'w+')
        titles = self.getTitles()
        tsv_writer = csv.writer(out_file, delimiter='\t')
        tsv_writer.writerow(titles)
        data_list = xml.find_all('infoTable')
        for i, row in enumerate(data_list):
            row_result = []
            for type in self.raw_titles:
                tag = row.find(re.compile(r'.*({}).*$'.format(type)))
                val = None if tag is None else tag.text
                row_result.append(val)
            tsv_writer.writerow(row_result)
            self.process_logging(i+1)
        self.log_msg('parsed {} rows'.format(str(len(data_list))))
        out_file.close()
        self.log_msg('{} generated'.format(self.curr_file_name))
        self.create_report_success()

    #--------------------------------------------------------------------------------------------------------------
    # Get xml report content data and call create TSV method with the paths of each report page on website as input
    #--------------------------------------------------------------------------------------------------------------
    def getXml(self, paths):
        for path in paths:
            soup = self.BsRequest(self.host + path, self.html_parser)
            tags_xml = soup.find_all(href=re.compile(r'.*\.xml$'), text=re.compile(r'.*\.xml$'))
            for tag in tags_xml:
                for sibling in tag.parent.next_siblings:
                    if bool(self.pattern_info_table.match(str(sibling.string).lower())):
                        self.createTsv(self.BsRequest(self.host + tag.get('href'), self.xml_parser))
                        return # Stop function here so we only get the recent one, iterate thorugh tags if wanna get all files or add a count to stop at certain amount of files.
        self.create_report_failure() # No matched xml found on website

    #-------------------------------------------------------------------------------------------------------------------------
    # Main driver method, get the html contecnt for specific CIK with BsRequest method, pass report page path to getXml method
    #-------------------------------------------------------------------------------------------------------------------------
    def crawl(self):
        for CIK, url in self.CIK_url_map.items():
            self.curr_CIK = CIK
            self.log_title('CIK {}: BEGIN'.format(CIK))
            soup = self.BsRequest(url, self.html_parser)
            if len(soup.select('.companyName')) == 0:
                print('Oops! No matched CIK for {} (or code to retrieve company name is deprecated)'.format(CIK))
                self.create_report_failure()
                continue
            self.curr_company_name = soup.select('.companyName')[0].contents[0]
            tags_13f = soup.find_all(text=self.pattern_13F)
            page_paths = [tag.parent.next_sibling.next_sibling.a.get('href') for tag in tags_13f]
            self.getXml(page_paths)
        self.status()

if __name__ == '__main__':
    def is_int(input):
        try:
            num = int(input)
        except ValueError:
            return False
        return True

    def command_check():
        if len(sys.argv) == 1:
            print('Please run the script with the CIK number(s) to parse (Python3 EDGAR.py 1234567 123123)')
            sys.exit()

        CIK_list = sys.argv[1:]
        for CIK in CIK_list:
            for chr in CIK:
                if not is_int(chr):
                    print('Wrong format: {}'.format(CIK))
                    print('Please provide CIKs that only contains number')
                    sys.exit()
        return CIK_list

    CIK_list = command_check()
    spider = Spider(CIK_list)
    spider.crawl()
    # 0001166559 0001756111 0001555283 0001397545 0001543160 0001496147 0001357955 0001439289 0001086364
