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

