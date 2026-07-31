import json
import urllib.parse
import urllib.request


class LocationService:

    BASE_URL = "https://api.geocoded.me/v2"

    # =====================================
    # GET DATA
    # =====================================

    def _get(self, endpoint, params=None):

        if params is None:
            params = {}

        query = urllib.parse.urlencode(params)

        url = (
            f"{self.BASE_URL}"
            f"{endpoint}"
        )

        if query:
            url += "?" + query

        try:

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "GetLeadsAI/1.0",
                    "Accept": "application/json"
                },
                method="GET"
            )

            with urllib.request.urlopen(
                request,
                timeout=20
            ) as response:

                return json.loads(
                    response.read().decode("utf-8")
                )

        except Exception as e:

            print(
                f"Location API error: "
                f"{type(e).__name__}: {e}"
            )

            return None

    # =====================================
    # GET ALL ITEMS
    # =====================================

    def _get_all(
        self,
        endpoint,
        params
    ):

        results = []

        offset = 0
        limit = 100

        while True:

            request_params = dict(params)

            request_params["limit"] = limit
            request_params["offset"] = offset

            result = self._get(
                endpoint,
                request_params
            )

            if not result:
                break

            data = result.get(
                "data",
                []
            )

            if not data:
                break

            results.extend(data)

            meta = result.get(
                "meta",
                {}
            )

            total = meta.get("total")

            offset += len(data)

            if total is not None:

                if offset >= total:
                    break

            if len(data) < limit:
                break

        return results

    # =====================================
    # GET COUNTRIES
    # =====================================

    def get_countries(self):

        data = self._get_all(
            "/countries",
            {
                "fields": "id,name,iso2"
            }
        )

        countries = []

        for item in data:

            name = item.get(
                "name",
                ""
            ).strip()

            code = item.get(
                "iso2",
                ""
            ).strip()

            if name and code:

                countries.append(
                    {
                        "name": name,
                        "code": code
                    }
                )

        countries.sort(
            key=lambda x: x["name"].lower()
        )

        return countries

    # =====================================
    # GET STATES
    # =====================================

    def get_states(
        self,
        country_code
    ):

        data = self._get_all(
            "/states",
            {
                "filter[country]": country_code,
                "fields": "id,name,countryCode,stateCode"
            }
        )

        states = []

        for item in data:

            name = item.get(
                "name",
                ""
            ).strip()

            code = item.get(
                "stateCode",
                ""
            ).strip()

            if name:

                states.append(
                    {
                        "name": name,
                        "code": code
                    }
                )

        states.sort(
            key=lambda x: x["name"].lower()
        )

        return states

    # =====================================
    # GET CITIES
    # =====================================

    def get_cities(
        self,
        country_code,
        state_code
    ):

        data = self._get_all(
            "/cities",
            {
                "filter[country]": country_code,
                "filter[state]": state_code,
                "fields": "id,name,countryCode,stateCode"
            }
        )

        cities = []

        for item in data:

            name = item.get(
                "name",
                ""
            ).strip()

            if name:
                cities.append(name)

        cities = sorted(
            list(set(cities)),
            key=lambda x: x.lower()
        )

        return cities
    