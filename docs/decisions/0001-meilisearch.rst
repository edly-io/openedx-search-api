Content Search Powered by Meilisearch
#####################################

Status
******

Draft


Context
*******

Existing search functionality
=============================

The Open edX platform currently implements many different forms of search. For
example, users can search for course content, library content, forum posts, and
more. Most of the search functionality in the core platform is powered by the
Elasticsearch search engine (though other functionality developed by 2U, such as
in edx-enterprise, is powered by Algolia).

Most uses of Elasticsearch in Open edX use
`edx-search <https://github.com/openedx/edx-search>`_ which provides a partial
abstraction over Elasticsearch. The edx-search library formerly used
`django-haystack <https://django-haystack.readthedocs.io/>`_ as an abstraction
layer across search engines, but "that was ripped out after the package was
abandoned upstream and it became an obstacle to upgrades and efficiently
utilizing Elasticsearch (the abstraction layer imposed significant limits)"
(thanks to Jeremy Bowman for this context). Due to these changes, the current
edx-search API is a mix of abstractions and direct usage of the Elasticsearch
API, which makes it confusing and difficult to work with. In addition, each
usage of edx-search has been implemented fairly differently. See
`State of edx-search <https://openedx.atlassian.net/wiki/spaces/AC/pages/3884744738/State+of+edx-search+2023>`_
for details (thanks to Andy Shultz).

Other platform components use Elasticsearch more directly:

* ``course-discovery`` and ``edx-notes-api`` do not use ``edx-search``, but are
  very tied to Elasticsearch via the use of ``django-elasticsearch-dsl`` and
  ``django-elasticsearch-drf``.
* ``cs_comments_service`` uses Elasticsearch via the official ruby gems.

Problems with Elasticsearch
===========================

At the same time, there are many problems with the current reliance on
Elasticsearch:

1. In 2021, the license of Elasticsearch changed from Apache 2.0 to a more
   restrictive license that prohibits providing "the products to others as a
   managed service". Consequently, AWS forked the search engine to create
   OpenSearch and no longer offers Elasticsearch as a service. This is
   problematic for many Open edX operators that use AWS and prefer to avoid
   any third-party services.
2. Elasticsearch is very resource-intensive and often uses more than a gigabyte
   of memory just for small search use cases.
3. Elasticsearch has poor support for multi-tenancy, which multiplies the
   problem of resource usage for organizations with many small Open edX sites.
4. The existing usage of edx-search/Elasticsearch routes all search requests and
   result processing through edxapp (the LMS) or other IDAs, increasing the
   load on those applications.

Meilisearch
===========

Meilisearch ("MAY-lee search") is a new, promising search engine that offers a
compelling alternative to Elasticsearch. It is open source, feature rich, and
very fast and memory efficient (written in Rust, uses orders of magnitude less
memory than Elasticsearch for small datasets). It has a simple API with an
official python driver, and has official integrations with the popular
Instantsearch frontend library from Algolia. It has strong support for
multi-tenancy, and allows creating restricted API keys that incorporate a user's
permissions, so that search requests can be made directly from the user to
Meilisearch, rather than routing them through Django. Initial testing has shown
it to be much more developer friendly than Elasticsearch/OpenSearch.

As of August 2024, there are only two known concerns with Meilisearch:

1. It doesn't (yet) support High Availability via replication, although this is
   planned and under development. It does have other features to support high
   availability, such as very low restart time (in ms).
2. It doesn't support boolean operators in keyword search ("red AND panda"),
   though it does of course support boolean operators in filters. This is a
   product decision aimed at keeping the user experience simple, and is unlikely
   to change.

Problem with edx-search
=======================

The edx-search feature is currently utilized only within the edx-platform, and many of its implementations are now deprecated in the new microfrontend environments. Additionally, it lacks the personalized token functionality, making it incompatible with advanced search engines such as Meilisearch. Even if we attempt to extend edx-search to support Meilisearch, it would still follow the same proxy mechanism and would not be able to utilize personalized tokens effectively. To find a detailed list of architectural issues here.

Decision
********

Open edX Search API
===================

We are proposing a new abstraction package with more generalised architecture inorder to support all available search engines including elasticsearch, meilisearch and algolia.
The Open edX Search API is designed with a forward-thinking approach, ensuring seamless integration with a wide range of future search engines.
This package aims to provide flexibility, scalability, and ease of use for developers looking to enhance their search capabilities within the Open edX platform.


Architecture
============

The Open edX Search API comprises four main components: the Driver, Indexer, Load Indexes Command, and a JavaScript library. Each component is described in detail below.

Driver Class
============

The base driver class contains the following functions: `get_user_token()`, `check_connection()`, `indexes()`, `index()`, and `get_search_rules()`. To integrate a new search engine or driver, the child class must implement all these functions.
This class is responsible for initializing the communication protocol between client and the search service. To change the driver class by updating the value of `SEARCH_ENGINE` in django settings.
the default value is `SEARCH_ENGINE = "openedx_search_api.drivers.meilisearch.MeiliSearchEngine"`

Indexer Class
=============

The base indexer class consists of the `index()` and `index_documents()` functions. To override the default functionality of the base class, the child indexer class should implement these functions.
Inorder to update the indexer class set `INDEXER_CLASS` attribute in django settings default value is `INDEXER_CLASS = "openedx_search_api.indexers.base.BaseIndexer"`

Load Indexes
============

A management command reads index configurations from the Django settings module and populates the indexes accordingly. further more we can also add configurable parameters to update specific index and set specific dataset.

`python ./manage.py load_indexes`

Javascript SDK
==============

A global JavaScript client SDK is available to facilitate communication with search services, serving as an abstraction layer to form search engine queries. Once the package is installed on the backend, this SDK will be accessible via a public static endpoint. By default, it supports Meilisearch, but it is structured to be adaptable for use with other search services.

The SearchEngine object includes the following functions:

1. `queryBuilder`
2. `getSearchURL`
3. `search`
4. `request`

Examples
========
Below is an example of adding a client SDK:
```html
<script src="<%= process.env.BASE_URL %>/static/django_search_backend/js/search_library.js" type="text/javascript"></script>
```

We have created an example to showcase this `here <https://github.com/openedx/frontend-app-learning/compare/master...qasimgulzar:frontend-app-learning:qasim/autosuggest-courseware>`_.

Please also refer to the Content Class `Example <https://github.com/openedx/edx-platform/pull/35177/files#diff-9f2ba6df1933f2b8b4a9939582d954107a465742a83db2c13cdc89eec8cc1fc3>`.
