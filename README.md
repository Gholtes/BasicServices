# Analysis of accessibility of basic services in Victoria

Statistical analysis of the range and accessibility of basic services such as supermarkets and banks varies along with average income between neighbouring postcodes in Victoria, Australia.

## Getting Started

This is an econometrics project, with the analysis pipeline divided into three stages:
1.	Data sourcing: Location data is extracted from the Google Maps API with GoogleMapsAPI_DataExtraction.py
2.	Data engineering: The extracted location data is combined with population data to provide an appropriate dataset for analysis with Analysis.py
3.	Regression Analysis: A Poisson regression is used to analyse the relationship between income and accessibility of services in RegressionAnalysis.R

### Prerequisites

```
Python 3
R
Numpy
Pandas
Requests
```

A Google Cloud Platform account is also required to use the Maps API.

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

### Acknowledgments

* Tom Pagel
* Google Maps Documentation

