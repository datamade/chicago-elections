The elections API provides election results and statistics for Chicago elections.

There are currently three types of endpoints:

| endpoints         | url pattern                                        |
|-------------------|----------------------------------------------------|
| Election listings | http://chicagoelections.datamade.us/elections/     |
| Election results  | http://chicagoelections.datamade.us/elections/{id} |
| Ballots           | http://chicagoelections.datamade.us/balllots/{id}  |

### Election listings

A call to http://chicagoelections.datamade.us/elections/ will return all the elections that we have in our API in
JSON format. 

```json
[

    {
        "date": "2000-03-21",
        "name": "March 2000 Primary Democratic",
        "id": 10
    },
    {
        "date": "2000-03-21",
        "name": "March 2000 Primary Republican",
        "id": 7
    },
    ...
```

The result will be an array of objects. Each object corresponds to a single election. Within each object there are 
three fields `date`, `name`, and `id`. The `date` value is the date of the election. The `name` value is the name of
the election. The `id` value is the primary key for this election within our API, which we will use in the other two
endpoints.

### Election results

To get the elections results of a particular election, call http://chicagoelections.datamade.us/elections/{id}. For
example to get the elections results for the March 2012 Democratic Party Primary Election, call 
http://chicagoelections.datamade.us/elections/22/.

```json
{

    "ballots_cast": [
        {
            "count": 3687,
            "ward": 1
        },
        ...
    ],
    "results": [
        {
            "votes": 385,
            "precinct_count": 48,
            "ward": 1,
            "race": "Appellate Court Judge (Vacancy of Cahill)",
            "option": "James Michael McGing"
        },
        ...
    ],
    "election": {
        "date": "2012-03-20",
        "election_type": "Primary",
        "id": 22,
        "name": "March 2012 Democratic Party Primary Election"
    },
    "voters": [
        {
            "count": 26893,
            "ward": 1
        },
        ...
    ]
}
```

You will recieve a JSON object with four fields `ballots_cast`, `results`, `election`, and `voters`.

#### `ballots_cast`

The value of `ballots_cast` is an array of objects representing the number of ballots cast each ward of the city.

```json
    "ballots_cast": [
        {
            "count": 3687,
            "ward": 1
        },
        ...
    ],
```

Each of these objects has two fields: `ward` and `count`. The value of `ward` is the ward number of the ward **at the
time of the election.** The value of `count` is the number of ballots cast in the particular ward during this election.
This is basically a count of the number of people who turned out to vote in this ward.

#### `results`
The value of `ballots` is an array of objects representing the count of votes for a candidate or ballot option, in a race, 
in a ward. 

```json
    "results": [
        {
            "votes": 385,
            "precinct_count": 48,
            "ward": 1,
            "race": "Appellate Court Judge (Vacancy of Cahill)",
            "option": "James Michael McGing"
        },
        ...
    ],
```

Each object has five fields: `votes`, `precinct_count`, `ward`, `race`, and `option`. The value of `ward` is the ward number of the ward **at the
time of the election.** The `race` value is the name of race. The `option` is the name of the candidate or ballot option
in race. The `votes` value is the number of votes that the ballot option received in this race in this ward. The value
of `precinct_count` is the number of precincts within the ward.

##### `election`
The value of `election` is an object that describes this election.

```json
    "election": {
        "date": "2012-03-20",
        "election_type": "Primary",
        "id": 22,
        "name": "March 2012 Democratic Party Primary Election"
```

It has the same form as the objects in the Elections Listing endpoing, with the addition of `election_type`. The value
of `election_type` is either `Primary`, `General`, `Special Primary` or `Special General`. These values correspond to
different types of elections.


##### `voters`

The value of `voters` is an array of objects where the objects contain the number of registered voters within a ward

```json
    "voters": [
        {
            "count": 26893,
            "ward": 1
        },
        ...
    ]
```

Each object has two values: `ward` and `count`. The value of `ward` is the ward number of the ward **at the
time of the election.** The value of `count` is the number of registered voters in that ward.






