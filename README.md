# delimitedchecker
Checks files and directories for properly delimited record data

Delimited record data is "simple" delimited. It does not check for embedded delimiters within text strings or other advanced settings (such as embedded quotes within quotes if quoted "text string"):

GOOD:
  column1,column2,column3
  A,B,c
  D,E,F

  column1|column2|column3
  A|B|C
  D|E|F
  G|"H1, H2"|I

BAD :
  column1,column2,column3
  A,"B1,B2",C
  "D1,D2",E,"F1,F2"

  column1,column2,column3
  A,"B1'"'s,B2",C
  "D1,D2",E,"F1,F2"

  column1|column2|column3
  A|"B1|B2"|C
  "D1|D2"|E|"F1|F2"
