Simple Ptt Article Extractor
============================

##### Simple Ptt Article information extractor.

### Req. Packages:

    Scrapy
    Requests

### Demo:

    python SimplePttArticleExtracter/Ptt.py

### Usage:

```python
    >>> from SimplePttArticleExtracter import Article

    >>> Parser = Article()

    >>> rsp = Parser.get('StupidClown', 'M.1462275619.A.150')

    >>> print(rsp)
```





