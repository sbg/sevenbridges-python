0.6.0 (2016-10-17)

Added support for error_handlers. Users can now register error_handlers
that will be executed upon each request. 

- Bugfixes
  - [Issue #45](https://github.com/sbg/sevenbridges-python/issues/45)
  - [Issue #46](https://github.com/sbg/sevenbridges-python/issues/46)



0.5.4 (2016-09-30)
==================
- Bugfixes
  - [Issue #42](https://github.com/sbg/sevenbridges-python/issues/42)
  - [Issue #43](https://github.com/sbg/sevenbridges-python/issues/43)



0.5.3 (2016-09-23)
==================
- Bugfixes
  - [Issue #40](https://github.com/sbg/sevenbridges-python/issues/40)
  - [Issue #41](https://github.com/sbg/sevenbridges-python/issues/41)



0.5.2 (2016-09-15)
==================
- Bugfixes
  - [Issue #35](https://github.com/sbg/sevenbridges-python/issues/35)
  - [Issue #39](https://github.com/sbg/sevenbridges-python/issues/39)
  

0.5.1 (2016-08-29)
==================
- Bugfixes
  - [Issue #28](https://github.com/sbg/sevenbridges-python/issues/28)
  
0.5.0 (2016-08-29)
==================

- Project settings available on project resource. These settings
  can be currently used to create locked projects.
- File now have tags. User is able to view/set/edit tags.
- Support for proxies. User can now configure library to use proxies.


- Bugfixes
  - [Issue #30](https://github.com/sbg/sevenbridges-python/issues/30)
  - [Issue #29](https://github.com/sbg/sevenbridges-python/issues/29)
  - [Issue #28](https://github.com/sbg/sevenbridges-python/issues/28)
  - [Issue #24](https://github.com/sbg/sevenbridges-python/issues/24)
  - [Issue #23](https://github.com/sbg/sevenbridges-python/issues/23)
  - [Issue #14](https://github.com/sbg/sevenbridges-python/issues/14)


0.4.4 (2016-08-19)
==================
- Upload changes
  Upload sync/asyc returns the upload handle. The uploaded file 
  is available by invoking .result() method.
- Query optimizations
  All queries except those on app resource are not optimized using
  the _fields=_all query parameter.
- Bugfixes
    - [Issue #21](https://github.com/sbg/sevenbridges-python/issues/21)
    - [Issue #22](https://github.com/sbg/sevenbridges-python/issues/22)

0.4.3 (2016-08-12)
==================
- Bugfixes
    - [Issue #16](https://github.com/sbg/sevenbridges-python/issues/16)
    - [Issue #17](https://github.com/sbg/sevenbridges-python/issues/17)
    - [Issue #18](https://github.com/sbg/sevenbridges-python/issues/18)

0.4.2 (2016-07-27)
==================
- Bugfixes
    - [Issue #12](https://github.com/sbg/sevenbridges-python/issues/12)

0.4.1 (2016-07-27)
==================
- Bugfixes
    - [Issue #10](https://github.com/sbg/sevenbridges-python/issues/10)
    - [Issue #11](https://github.com/sbg/sevenbridges-python/issues/11)

0.4.0 (2016-07-18)
==================
- Introducing support for Volumes API
- Downloader refactor.
- Task statistics now carries docker information.
- Breaking compatibility on job.logs model because of newly added support for custom logs.
  job.logs behaves as a dictionary.
- Refactor .get query members to use resources and not construct the response on their own.
- Useful enums available in models.enums.
- Transformers now validate for Resource instances or strings. Everything else raises exception.

0.3.0 (2016-06-20)
==================

- Introducing file upload
- Fixing bug related to object reload.

0.2.0 (2016-05-30)
==================

-   Documentation cleaning.
-   Breaking compatibility on compound fields now they are dicts if declared as writable.
-   Bug fixes
  - [Issue #1](https://github.com/sbg/sevenbridges-python/issues/1)
  - [Issue #2](https://github.com/sbg/sevenbridges-python/issues/2)
  - [Issue #3](https://github.com/sbg/sevenbridges-python/issues/3)


0.1.1 (2016-04-27)
==================

-   Doc fixes
-   Changes in error decorator to throw Value Error due to py2-py3 compatibilty.


0.1.0 (2016-04-27)
==================

-   initial release

