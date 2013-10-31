The Clout API retruns information about the clout score and clout ranking of Chicago aldermen.

To access the Clout API, call http://chicagoelections.datamade.us/clout/

You will receive a JSON array of object

```json
[

    {
        "alderman": "Burke, Edward M.",
        "clout": 5.5391710171565,
        "id": "ocd-person/a6785b48-3f6e-11e3-8ca6-22000a971dca",
        "rank": 1
    },
    {
        "alderman": "O'Connor, Patrick",
        "clout": 2.1030053889511,
        "id": "ocd-person/946a00b6-3cec-11e3-8a24-22000a971dca",
        "rank": 2
    },
    ...
]
```
 
Each object contains details about a particular alderman. It has four fields: `alderman`, `clout`, `id`, `rank`.

`alderman` is the name of the alderman. `id` is a unique key that we use for this **person** across APIs. `score` is
the our predicted "clout score" this is a unitless measurement. 'rank' is the rank of the alderman's clout score with the 
highest score having a rank of 1 and the lowest score having a rank of 50.






 
