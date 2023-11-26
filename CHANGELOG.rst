0.12.0 (2023-10-19)
===================

* Declare Django 4.2 support in #167
* Drop mock dependency in favor of unittest.mock in #168
* Update README.rst with the correct Header name in #170. Thanks @adrgs !
* Fixed ignored headers issue in #172. Thanks for the detailed reporting @jagotu !
* Deprecated setup.py in github actions in #173 and #174


0.11.0 (2023-02-26)
===================

* Add X-Forwarded-For and X-Forwarded-Proto headers. Fixes #79.
* Add Django 3.2, 4.0 and 4.1 support. Fixes #126.
* Add Python 3.8, 3.9, 3.10 and 3.11 support
* Drop Python 3.4, 3.5 and 3.6 support
* Drop Django <3.0 support
* Fixed README badges


0.10.0 (2020-02-05)
===================

* Fix add_remote_user when run without AuthenticationMiddleware. Fix #86
* Add get_encoded_query_params method
* Add support for Python 3.7 and 3.8.
* Add support for Django 2.2 and 3.0.


0.9.15 (2018-05-30)
===================

* Fix issues with latest urllib3. Fixes #75.
* Fix issues with parsing cookies. Fixes #84.
* Drop Python 3.3, 3.4, and PyPy support.
* Add Python 3.6 support.


0.9.14 (2018-01-11)
===================

* Move construction of proxied path to method [@dimrozakis]
* User.get_username() rather than User.name to support custom User models [@acordiner]


0.9.13 (2016-10-31)
===================

* Added support to Django 1.10 (support to 1.7 was dropped)


0.9.12 (2016-05-23)
===================

* Fixed error 500 caused by content with wrong encoding [@lucaskanashiro, @macartur]


0.9.11 (2016-03-29)
===================

* Updated urllib3 to 1.12 (at least)


0.9.10 (2016-02-03)
===================

* Fixed Python 3 compatibility issue (see #59 and #61). Thanks @stefanklug and @macro1!


0.9.9 (2015-12-15)
==================

* Reorder header prior to httplib request. `Host` should be always the first request header.


0.9.8 (2015-12-10)
==================

* Added support to Django 1.9 (dropped support to Django 1.6)
* Added `get_request_headers` to make easier to set and override request headers


0.9.7 (2015-09-17)
==================

* Bug fixed: property preventing to set upstream and diazo_rules (#53, #54) [@vdemin]
* Security issue fixed: when colon is present at URL path urljoin ignores the upstream and the request is redirected to the path itself allowing content injection


0.9.6 (2015-09-09)
==================

* Fixed connections pools
* Use wsgiref to check for hop-by-hop headers [#50]
* Refactored tests
* Fixed security issue that allowed remote-user header injection


0.9.5 (2015-09-02)
==================

* Added extras_require to make easier diazo installation


0.9.4 (2015-08-27)
==================

* Alow to send context dict to transformation template. [@chaws, @macartur]


0.9.3 (2015-06-12)
==================

* Use StringIO intead of BytesIO on theme compilation (transformation)


0.9.2 (2015-06-09)
==================

Thanks @rafamanzo for the reports.

* Append a backslash on upstream when needed
* Validate upstream URL to make sure it has a scheme
* Added branch test coverage


0.9.1 (2015-05-18)
==================

* More permissive URL scheme (#41).
* Refactored code to allow setting custom headers by extending method (#40) [@marciomazza]


0.9.0 (2015-03-04)
===================

* urllib2 replaced by urllib3 (#10)
* No Diazo transformation if header X-Diazo-Off is set to true - either request or response (#15)
* Removed double memory usage when reading response body (#16)
* Fixed bug caused by many set-cookies coming from upstream (#23) - by @thiagovsk and @macartur
* Added stream support for serving big files with an acceptable memory footprint (#17 and #24). Thanks to @lucasmoura, @macartur, @carloshfoliveira and @thiagovsk.
* Moved Diazo functionalities to DiazoProxyView.
* Logging improved (#21).
* Added options for default_content_type and retries [@gldnspud].
* Sphinx docs (#25).
* 100% test coverage.
