

0.9.0 (unreleased)
===================

* urllib2 replaced by urllib3 (#10)
* No Diazo transformation if header X-Diazo-Off is set to true - either request or response (#15)
* Removed double memory usage when reading response body (#16)
* Fixed bug caused by many set-cookies coming from upstream (#23) - by @thiagovsk and @macartur
* Added stream support for serving big files with an acceptable memory footprint (#17 and #24). Thanks to @lucasmoura, @macartur, @carloshfoliveira and @thiagovsk.
* Moved Diazo functionalities to DiazoProxyView
