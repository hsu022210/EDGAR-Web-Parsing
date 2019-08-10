# Coding Challenge

Write code in Python that parses fund holdings pulled from EDGAR, given a ticker or CIK, and writes a .tsv file from them.

## Author

Alec Hsu

### Background

People can invest in mutual funds that hold many stocks and bonds. Funds list what they own  every quarter, so investors can get a sense of what they are actually exposed to, e.g. a  "21st Century Tactical Technology Fund" does not just own 50% AAPL and 50% GOOG. Fund holdings are listed on the SEC website, EDGAR.

### Exmaple

For this example, we will use this CIK: 0001166559
Start on this * [page](https://www.sec.gov/edgar/searchedgar/companysearch.html), enter in the CIK (or ticker), and it will take you * [here](https://www.sec.gov/cgi-bin/browse-edgar?CIK=0001166559&owner=exclude&action=getcompany).

Find the "13F" report documents from the ones listed, parse and generate tab-delimited text from the xml, write the text to a file.

## Goals

Your code should be able to use any of the following mutual fund tickers:

```
Gates Foundation | 0001166559
Caledonia | 0001166559
Peak6 Investments LLC | 0001756111
Kemnay Advisory Services Inc. | 0001555283
HHR Asset Management, LLC | 0001397545
Benefit Street Partners LLC | 0001543160
Okumus Fund Management Ltd. | 0001496147
PROSHARE ADVISORS LLC | 0001357955
TOSCAFUND ASSET MANAGEMENT LLP | 0001439289
Black Rock | 0001086364
```

Assume you need to fetch only the most recent report, but consider how you could get previous ones. Be sure to check all of the included tickers, since the format of the 13F reports will differ. Let us know your thoughts on how to deal with different formats.

### Get started

Create a `virtualenv` to have a cleaner environment for package dependencies and actiavte it

```
virtualenv venv
```

Activate

```
source venv/bin/activate
```

This file is written in `Python 3`, please install/check Python 3 version.

```
Python -V
```

Install required packages

```
pip install -r requirements.txt
```

### Usage

Run the `EDGAR.py` following by one or more CIK number(s) to parse from EDGAR website.

Some CIK numbers: `0001166559 0001756111 0001555283 0001397545 0001543160 0001496147 0001357955 0001439289 0001086364`
```
python EDGAR.py 0001166559 0001756111 ...
```

### Output

After the script ran it will generate/overwrite a TSV file for each CIK with naming rule `{CIK}_{Company Name}.tsv` in current folder and a generated status report will show up in the end of logging from running script.

```
************* Generate TSV File Status Report ************
0001166559: Succeeded --- 0001166559_BILL & MELINDA GATES FOUNDATION TRUST .tsv
0001756111: Succeeded --- 0001756111_PEAK6 Investments LLC .tsv
0001555283: Succeeded --- 0001555283_Kemnay Advisory Services Inc. .tsv
....
***********************************************************
```

## Built With

* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Pulling data out of HTML and XML files
* [Requests](https://2.python-requests.org/en/master/) - HTTP library for Python
* [lxml](https://lxml.de/) - Used to process XML

## Authors

* **Alec Hsu**

## Question

> Assume you need to fetch only the most recent report, but consider how you could get previous ones. Be sure to check all of the included tickers, since the format of the 13F reports will differ. Let us know your thoughts on how to deal with different formats.

- Retriving all of the 13F reports is implemented with regex text pattern matching.
- Comment in the code indicate what should change for getting not only the recent 13F report.
