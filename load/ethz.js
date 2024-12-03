import { check } from 'k6';
import http from 'k6/http';

/* run with:
export HTTP_PROXY=http://policy:@forward-proxy.scion:9080;
export HTTPS_PROXY=https://policy:@forward-proxy.scion:9443;
export GODEBUG=http2client=0;
export VUS=100;
SUFFIX="$(date +"%Y-%m-%d_%T")_"$VUS"_ethz"; k6 run --out "csv=data/data_$SUFFIX.csv" ethz.js | tee "data/log_$SUFFIX.log";
unset HTTP_PROXY; unset HTTPS_PROXY; unset GODEBUG
*/

// https://grafana.com/docs/k6/latest/using-k6/
export const options = {
    insecureSkipTLSVerify: true,
    // httpDebug: 'full',

    scenarios: {
        ethz: {
            executor: 'constant-vus',
            exec: "run",
            vus: __ENV.VUS,
            duration: '30s',
            env: {
                ADDRESS: "https://ethz.ch/de.html",
            },
        },
    }
};

export function run() {
    if (!__ENV.HTTP_PROXY || __ENV.HTTP_PROXY.length == 0 || !__ENV.HTTPS_PROXY | __ENV.HTTPS_PROXY.length == 0) fail();

    const res = http.get(__ENV.ADDRESS);
    check(res, {
        'is status 200': (r) => r.status === 200,
    });
}
