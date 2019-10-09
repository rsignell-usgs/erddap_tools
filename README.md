# erddap_tools
This is the approach we use for creating `datasets.xml` from a bunch of similar CF-compliant netcdf files. 

We first ran `GenerateDatasetsXML.sh` on one of the files, then created a jinja2 template from that result. 

We then just loop through the datasets populating the fields in the template.
