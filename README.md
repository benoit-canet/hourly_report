hourly_report
=============

A simple script to manage hourly work reports

This script parse a markdown formated file in order to compute time worked and
generate a report that can be given to the customer.

Input file format
-----------------

Each day of work done must be indicated by typing the "date: DD/MM/YYYY" tag.

In a day of work slices of time worked are indicated by the two tag "start: HHhMM"
and "stop: HHhMM".

Generating a daily or weekly report
-----------------------------------

Run

     python report.py -f hours

Then copy paste the output to your boss/customer and confirm that these hours must
not be reported again.

This confirmation will add a "last:" tag at the end of the file.

Computing total time elapsed for billing
----------------------------------------

Run

    python report.py -f hours -s

It will print all the file content with the daily worked hours and compute the
total sum of hours worked.
Then archive the input file and create a new one.

Sample input file
-----------------

    date: 05/02/2014
    start: 14h00
    stop: 15h00
    
    title
    -----
    
    * fooo
    * barr
    * onx

