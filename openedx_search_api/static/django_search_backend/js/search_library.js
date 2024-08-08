"use strict"

function SearchEngine(engine = "meilisearch", config = undefined, indexUid) {

    const engines = {
        "meilisearch": function () {
            this.buildQuery = function (q, payload) {
                const filters = [];
                Object.keys(payload).map((key) => {
                    if (Array.isArray(payload[key]) && payload[key]) {
                        filters.push(`${key} IN [${payload[key].join(',')}]`);
                    } else if (!Array.isArray(payload[key]) && payload[key] instanceof Object) {
                        //     todo handle nested dictionary.
                    } else {
                        filters.push(`${key}='${payload[key]}'`);
                    }
                });
                const query = filters.join(' AND ')
                return {
                    q,
                    facets: [],
                    limit: 21,
                    offset: 0,
                    filter: query
                }
            }
            this.transformResponse = function (rawResponse) {
                return {
                    took: rawResponse.processingTimeMs,
                    results: rawResponse.hits,
                    limit: rawResponse.limit,
                    offset: rawResponse.offset,
                    total: rawResponse.estimatedTotalHits,
                    maxScore: null,
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
SearchEngine.prototype.search = function (term, filters) {
    const payload = this.queryBuilder(term, filters);
    return this.request(this.getSearchURL(), 'POST', JSON.stringify(payload));
}
SearchEngine.prototype.request = function (url, method, body) {
    const _this = this;
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.open(method, url, true);
        xhr.setRequestHeader('Content-type', 'application/json; charset=UTF-8');
        xhr.setRequestHeader('Authorization', `Bearer ${this.config.token}`);
        xhr.onreadystatechange = function () {
            if (this.readyState == 4) {
                if (this.status == 200) {
                    const results = _this.client.transformResponse(JSON.parse(this.responseText));
                    resolve(results);
                } else {
                    reject(this);
                }
            }
        }
        xhr.send(body);
    });
}