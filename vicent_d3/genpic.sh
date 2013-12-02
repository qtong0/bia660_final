#!/bin/sh
#recommend
mkdir $1
cd $1

python -c "import sys;sys.path.append('../');import vicent_bar_chart_pro;vicent_bar_chart_pro.ratioBar('$1','recommend',0.8,0.9,0.5,0.9,1)"
#price,review allmenu vs yelp
python -c "import sys;sys.path.append('../');import vicent_stack_bar_chart;vicent_stack_bar_chart.stackChart('$1','ratio')"
python -c "import sys;sys.path.append('../');import vicent_stack_bar_chart;vicent_stack_bar_chart.stackChart('$1','review')"
#price,review,price from allmenu
python -c "import sys;sys.path.append('../');import vicent_bar_chart;vicent_bar_chart.ratioBar('$1','ratio')"
python -c "import sys;sys.path.append('../');import vicent_bar_chart;vicent_bar_chart.ratioBar('$1','review')"
python -c "import sys;sys.path.append('../');import vicent_bar_chart;vicent_bar_chart.ratioBar('$1','price')"
#line
python -c "import sys;sys.path.append('../');import vicent_line_chart;vicent_line_chart.line('$1')"



