"use strict"

function SearchEngine(engine = "meilisearch", config = undefined, indexUid) {

    const engines = {
        "meilisearch": function () {
            this.buildQuery = function (q, payload) {
                return {
                    indexUid,
                    q,
                    facets: [],
                    limit: 21,
                    offset: 0
                }
            }
        }
    }

    this.client = new engines[engine]();
    this.config = config;
}

SearchEngine.prototype.queryBuilder = function (term, payload) {
    return this.client.buildQuery(term, payload);
}
SearchEngine.prototype.multiSearch = function (term, filters, onsuccess, onerror) {
    const {url, token} = this.config;
    const payload={
        queries: [
            this.queryBuilder(term, filters)
        ]
    }
    this.request(`${url}/multi-search`, 'POST', JSON.stringify(payload),
        onsuccess,
        onerror
    );
}
SearchEngine.prototype.request = function (url, method, body, onsuccess, onerror) {
    let xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-type', 'application/json; charset=UTF-8')
    xhr.setRequestHeader('Authorization', `Bearer ${this.config.token}`);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            onsuccess(this.responseText);
        } else {
            onerror(this);
        }
    }
    xhr.send(body);
}