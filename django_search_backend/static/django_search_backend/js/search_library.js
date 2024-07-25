"use strict"

function SearchEngine(engine = "meilisearch", config = undefined, indexUid) {

    const engines = {
        "meilisearch": function () {
            this.buildQuery = function (q, payload) {
                return {
                    q,
                    facets: [],
                    limit: 21,
                    offset: 0
                }
            }
            this.transformResponse = function (rawResponse) {
                return {
                    results: rawResponse.hits,
                    limit: rawResponse.limit,
                    offset: rawResponse.offset
                };
            }
            this.getSearchURL = function () {
                const {url} = config;
                return `${url}/indexes/${indexUid}/search`
            }
        }
    }

    this.client = new engines[engine]();
    this.config = config;
}

SearchEngine.prototype.queryBuilder = function (term, payload) {
    return this.client.buildQuery(term, payload);
}
SearchEngine.prototype.getSearchURL = function () {
    return this.client.getSearchURL();
}
SearchEngine.prototype.search = function (term, filters, onsuccess, onerror) {

    const payload = this.queryBuilder(term, filters)
    this.request(this.getSearchURL(), 'POST', JSON.stringify(payload),
        onsuccess,
        onerror
    );
}
SearchEngine.prototype.request = function (url, method, body, onsuccess, onerror) {
    const _this = this
    let xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=UTF-8')
    xhr.setRequestHeader('Authorization', `Bearer ${this.config.token}`);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            const results = _this.client.transformResponse(JSON.parse(this.responseText))
            onsuccess(results);
        } else {
            onerror(this);
        }
    }
    xhr.send(body);
}